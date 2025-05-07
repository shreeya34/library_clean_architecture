from datetime import datetime, timedelta
from typing import Dict, Any
from uuid import UUID
import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from modules.infrastructure.config import settings
from modules.infrastructure.database.utils import commit_and_refresh
from modules.domain.exceptions.admin.exception import (
    BookNotFoundError,
    BookUnavailableError,
    InvalidMemberCredentialsError,
    MemberNotFoundError
)
from modules.domain.exceptions.admin.exception import RaiseUnauthorizedError
from modules.infrastructure.database.models.member import BorrowedBooks, ReturnBook
from modules.infrastructure.database.models.admin import Member
from modules.domain.member.models import (
    BorrowBookRequest,
    MemberLoginRequest,
    ReturnBookRequest,
)
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.infrastructure.security.auth_handler import get_current_user, signJWT
from modules.infrastructure.logger import get_logger
from modules.domain.member.response import BorrowedBookResponse
from modules.infrastructure.repositories.admin_repositories import get_member_by_name
from modules.domain.exceptions.member.exception import BookNotBorrowedError, DuplicateBookBorrowError
from modules.infrastructure.repositories.member_repositories import create_member_login, get_book_by_title
from modules.application.interfaces.member_services import MemberService

logger = get_logger()
postgres_manager = PostgresManager(settings)

class LibraryMemberService(MemberService):
    def member_logins(self, member_login: MemberLoginRequest, db: Session) -> Dict[str, Any]:
        """Implementation of member login"""
        logger.info(f"Login for: {member_login.name}")

        member = get_member_by_name(db, member_login.name)
        if not member:
            logger.warning("Failed login attempt for non-existent member: %s", member_login.name)
            raise InvalidMemberCredentialsError(member_login.name)

        access_token = signJWT(member.name, member.member_id, is_admin=False)
        logger.info(f"Login successful for user: {member_login.name}")

        new_login = create_member_login(db, member.member_id, member_login.name)

        return {
            "message": "Login successful",
            "member_id": member.member_id,
            "token": access_token,
        }

    def borrow_book(self, book_request: BorrowBookRequest, db: Session, current_user: dict) -> BorrowedBookResponse:
        """Implementation of book borrowing"""
        book_title = book_request.book_title
        user_id_str = current_user.get("admin_id")
        
        if not user_id_str:
            logger.error("Borrow attempt by user without valid user_id in token")
            raise RaiseUnauthorizedError()
        
        try:
            user_id = uuid.UUID(user_id_str)
            # Convert UUID to string for querying the database
            user_id_str = str(user_id)
        except ValueError:
            logger.error("Invalid UUID format for user_id: %s", user_id_str)
            raise RaiseUnauthorizedError()
            
        member = db.query(Member).filter(Member.member_id == user_id_str).first()
        if not member:
            logger.error("Borrow attempt by non-existent member: %s", user_id_str)
            raise MemberNotFoundError(user_id_str)

        book = get_book_by_title(db, book_title)
        if not book or book.stock <= 0:
            logger.warning("Borrow attempt for unavailable book: %s", book_title)
            raise BookUnavailableError(book_title)
        
        # Convert book ID to integer if needed (it appears to be an integer in your model)
        book_id = book.id
        
        # Ensure both IDs are strings for comparison with string columns
        member_id_str = member.member_id
        
        already_borrowed = db.query(BorrowedBooks).filter(
            BorrowedBooks.book_id == book_id,
            BorrowedBooks.member_id == member_id_str
        ).first()

        if already_borrowed:
            logger.warning("Duplicate borrow attempt: %s by user %s", book.title, member.name)
            raise DuplicateBookBorrowError(book.title)

        borrow_date = datetime.now()
        expiry_date = borrow_date + timedelta(weeks=2)

        borrowed_book = BorrowedBooks(
            title=book.title,
            member_id=member_id_str,  # Use string version
            book_id=book_id,          # Use integer version
            name=member.name,
            borrow_date=borrow_date.isoformat(),
            expiry_date=expiry_date.isoformat(),
        )

        book.stock -= 1
        commit_and_refresh(db, borrowed_book)

        logger.info("Book borrowed: %s by %s", book.title, member.name)
        return BorrowedBookResponse(
            title=book.title,
            member_id=member_id_str,
            name=member.name,
            borrow_date=borrow_date.isoformat(),
            expiry_date=expiry_date.isoformat(),
        )
    def return_book(self, return_request: ReturnBookRequest, db: Session, current_user: dict) -> Dict[str, Any]:
        """Implementation of book return"""
        book_title = return_request.book_title
        user_id = current_user.get("admin_id")
        
        if not user_id:
            logger.error("Return attempt by user without valid user_id in token")
            raise RaiseUnauthorizedError()

        member = db.query(Member).filter(Member.member_id == user_id).first()
        if not member:
            logger.error("Return attempt by non-existent member: %s", user_id)
            raise MemberNotFoundError(user_id)

        book = get_book_by_title(db, book_title)
        if not book:
            logger.warning("Return attempt for non-existent book: %s", book_title)
            raise BookNotFoundError(book_title)
            
        borrowed_book = db.query(BorrowedBooks).filter(
            BorrowedBooks.book_id == book.id,
            BorrowedBooks.member_id == member.member_id
        ).first()
           
        if not borrowed_book:
            logger.warning("Book %s is not borrowed by member %s", book_title, member.name)
            raise BookNotBorrowedError(book_title)
        
        return_date = datetime.now()
        returned_book = ReturnBook(
            title=book.title,
            member_id=member.member_id,
            book_id=book.id,
            name=member.name,
            return_date=return_date,
        )
        db.delete(borrowed_book)
        db.commit() 

        book.stock += 1
        commit_and_refresh(db, returned_book)

        logger.info("Book returned: %s by %s", book.title, member.name)

        return {
            "book_title": book.title,
            "name": member.name,
            "return_date": return_date.isoformat(),
        }

member_service = LibraryMemberService()
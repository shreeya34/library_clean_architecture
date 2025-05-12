from datetime import datetime, timedelta
from typing import Dict, Any
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from modules.domain.repositories.member.member_repositories import IMemberRepository
from modules.infrastructure.database.utils import commit_and_refresh
from modules.domain.exceptions.admin.exception import (
    BookNotFoundError,
    BookUnavailableError,
    MemberNotFoundError,
)
from modules.domain.exceptions.member.exception import (
    BookAlreadyReturnedError,
    InvalidUUIDError,
    OnlyMembersCanBorrowError,
    OnlyMembersReturnBorrowError,
    RaiseUnauthorizedError,
)
from modules.infrastructure.database.models.member import BorrowedBooks, ReturnBook
from modules.infrastructure.database.models.admin import Member
from modules.interfaces.request.member_request import (
    BorrowBookRequest,
    MemberLoginRequest,
    ReturnBookRequest,
)
from modules.infrastructure.security.auth_handler import signJWT
from modules.infrastructure.logger import get_logger
from modules.interfaces.response.member_response import BorrowedBookResponse
from modules.domain.exceptions.member.exception import (
    BookNotBorrowedError,
    DuplicateBookBorrowError,
    InvalidMemberCredentialsError,
)
from modules.domain.services.member_services import MemberService
from modules.infrastructure.security.password_utils import check_password
from modules.shared.decorators.db_exception_handler import db_exception_handler
from modules.shared.utils.member_utils import create_borrowed_book_entry, parse_uuid

logger = get_logger()


class LibraryMemberService(MemberService):

    def __init__(self, member_repo: IMemberRepository):
        self.member_repo = member_repo

    @db_exception_handler("member login")
    def member_logins(
        self, member_login: MemberLoginRequest, db: Session
    ) -> Dict[str, Any]:
        member = self.member_repo.get_member_by_name(db, member_login.name)
        if not member or not check_password(member_login.password, member.password):
            logger.warning(f"Invalid credentials for: {member_login.name}")
            raise InvalidMemberCredentialsError(member_login.name)

        token = signJWT(member.name, member.member_id, is_admin=False)
        self.member_repo.create_member_login(db, member.member_id, member.name)
        db.commit()

        logger.info(f"User {member_login.name} logged in successfully.")
        return {
            "message": "Login successful",
            "member_id": member.member_id,
            "token": token,
        }

    @db_exception_handler("borrow books")
    def borrow_book(
        self, book_request: BorrowBookRequest, db: Session, current_user: dict
    ) -> BorrowedBookResponse:
        if current_user.get("is_admin"):
            raise OnlyMembersCanBorrowError()

        member_id = str(parse_uuid(current_user.get("admin_id", "")))
        member = self.member_repo.get_member_by_id(db, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        books = self.member_repo.get_available_books_by_title(
            db, book_request.book_title
        )
        if not books:
            raise BookUnavailableError(book_request.book_title)

        book = books[0]
        if self.member_repo.has_already_borrowed(db, book.id, member.member_id):
            raise DuplicateBookBorrowError(book.title)

        borrowed = create_borrowed_book_entry(book, member)
        book.stock -= 1
        self.member_repo.save_borrowed_book(db, borrowed)

        return BorrowedBookResponse(
            title=borrowed.title,
            member_id=borrowed.member_id,
            name=borrowed.name,
            borrow_date=borrowed.borrow_date,
            expiry_date=borrowed.expiry_date,
        )

    @db_exception_handler("return books")
    def return_book(
        self, return_request: ReturnBookRequest, db: Session, current_user: dict
    ) -> Dict[str, Any]:
        """Handles returning a borrowed book by a member."""
        if current_user.get("is_admin"):
            raise OnlyMembersReturnBorrowError()

        member = self._get_valid_member(db, current_user.get("admin_id"))
        book = self._get_valid_book(db, return_request.book_title)
        borrowed_book = self._validate_borrowed_book(db, book.id, member.member_id)

        self._process_return(db, book, member, borrowed_book, datetime.now())

        return {
            "book_title": book.title,
            "name": member.name,
            "return_date": datetime.now().isoformat(),
        }

    def _get_valid_member(self, db: Session, user_id: int):
        member = self.member_repo.get_member_by_id(db, user_id)
        if not member:
            raise MemberNotFoundError(user_id)
        return member

    def _get_valid_book(self, db: Session, title: str):
        book = self.member_repo.get_book_by_title(db, title)
        if not book:
            raise BookNotFoundError(title)
        return book

    def _validate_borrowed_book(self, db: Session, book_id: int, member_id: int):
        borrowed_book = self.member_repo.get_borrowed_book(db, book_id, member_id)
        if not borrowed_book:
            raise BookNotBorrowedError(book_id)
        return borrowed_book

    def _process_return(
        self, db: Session, book, member, borrowed_book, return_date: datetime
    ):
        returned_book = ReturnBook(
            title=book.title,
            member_id=member.member_id,
            book_id=book.id,
            name=member.name,
            return_date=return_date,
        )
        try:
            self.member_repo.delete_borrowed_book(db, borrowed_book)
            book.stock += 1
            commit_and_refresh(db, returned_book)
        except (BookNotBorrowedError, BookAlreadyReturnedError) as e:
            raise HTTPException(status_code=400, detail=str(e))

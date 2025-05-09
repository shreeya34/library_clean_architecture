from datetime import datetime, timedelta
from typing import Dict, Any
import uuid
from sqlalchemy.orm import Session
from modules.domain.repositories.member.member_repositories import IMemberRepository
from modules.infrastructure.database.utils import commit_and_refresh
from modules.domain.exceptions.admin.exception import (
    BookNotFoundError,
    BookUnavailableError,
    MemberNotFoundError,
)
from modules.domain.exceptions.member.exception import (
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
from modules.shared.utils.member_utils import create_borrowed_book_entry, parse_uuid

logger = get_logger()


class LibraryMemberService(MemberService):

    def __init__(self, member_repo: IMemberRepository):
        self.member_repo = member_repo

    def member_logins(
        self, member_login: MemberLoginRequest, db: Session
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Login attempt for: {member_login.name}")

            member = self.member_repo.get_member_by_name(db, member_login.name)
            if not member or not check_password(member_login.password, member.password):
                logger.warning("Invalid login credentials for: %s", member_login.name)
                raise InvalidMemberCredentialsError(member_login.name)

            access_token = signJWT(member.name, member.member_id, is_admin=False)
            logger.info(f"Login successful for user: {member_login.name}")

            self.member_repo.create_member_login(
                db, member.member_id, member_login.name
            )
            db.commit()

            return {
                "message": "Login successful",
                "member_id": member.member_id,
                "token": access_token,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error during login: {str(e)}")
            raise

    def borrow_book(
        self, book_request: BorrowBookRequest, db: Session, current_user: dict
    ) -> BorrowedBookResponse:
        if current_user.get("is_admin", False):
            logger.error("Admin user attempted to borrow a book: %s", current_user)
            raise OnlyMembersCanBorrowError()

        user_id = parse_uuid(current_user.get("admin_id", ""))
        member = self.member_repo.get_member_by_id(db, str(user_id))
        if not member:
            raise MemberNotFoundError(str(user_id))

        book = self.member_repo.get_book_by_title(db, book_request.book_title)
        if not book or book.stock <= 0:
            raise BookUnavailableError(book_request.book_title)

        if self.member_repo.has_already_borrowed(db, book.id, member.member_id):
            raise DuplicateBookBorrowError(book.title)

        borrowed_book = create_borrowed_book_entry(book, member)
        book.stock -= 1
        self.member_repo.save_borrowed_book(db, borrowed_book)

        return BorrowedBookResponse(
            title=borrowed_book.title,
            member_id=borrowed_book.member_id,
            name=borrowed_book.name,
            borrow_date=borrowed_book.borrow_date,
            expiry_date=borrowed_book.expiry_date,
        )

  
    def return_book(
    self, return_request: ReturnBookRequest, db: Session, current_user: dict
) -> Dict[str, Any]:
        """Handles returning a borrowed book by a member."""

        if current_user.get("is_admin"):
            logger.error("Admin user attempted to return a book: %s", current_user)
            raise OnlyMembersReturnBorrowError()

        user_id = current_user.get("admin_id")
        if not user_id:
            logger.error("Missing user_id in token")
            raise RaiseUnauthorizedError()

        member = self._get_valid_member(db, user_id)
        book = self._get_valid_book(db, return_request.book_title)
        borrowed_book = self._validate_borrowed_book(db, book.id, member.member_id)

        return_date = datetime.now()
        self._process_return(db, book, member, borrowed_book, return_date)

        logger.info("Book returned: %s by %s", book.title, member.name)
        return {
            "book_title": book.title,
            "name": member.name,
            "return_date": return_date.isoformat(),
        }

    def _get_valid_member(self, db: Session, user_id: int):
        member = self.member_repo.get_member_by_id(db, user_id)
        if not member:
            logger.error("Non-existent member: %s", user_id)
            raise MemberNotFoundError(user_id)
        return member

    def _get_valid_book(self, db: Session, title: str):
        book = self.member_repo.get_book_by_title(db, title)
        if not book:
            logger.warning("Non-existent book: %s", title)
            raise BookNotFoundError(title)
        return book

    def _validate_borrowed_book(self, db: Session, book_id: int, member_id: int):
        borrowed_book = self.member_repo.get_borrowed_book(db, book_id, member_id)
        if not borrowed_book:
            logger.warning("Book ID %s not borrowed by member ID %s", book_id, member_id)
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
        except Exception as e:
            db.rollback()
            logger.error(f"Error during return: {str(e)}")
            raise

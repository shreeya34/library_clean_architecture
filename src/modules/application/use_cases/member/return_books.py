from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException
from modules.domain.exceptions.admin.exception import (
    BookNotFoundError,
    MemberNotFoundError,
)
from modules.domain.exceptions.member.exception import (
    BookAlreadyReturnedError,
    BookNotBorrowedError,
    OnlyMembersReturnBorrowError,
)
from modules.domain.repositories.member.member_repositories import IMemberRepository
from modules.infrastructure.database.models.member import ReturnBook
from modules.infrastructure.database.utils import commit_and_refresh
from sqlalchemy.orm import Session
from modules.interfaces.request.member_request import ReturnBookRequest


class ReturnBookUseCase:
    def __init__(self, member_repo: IMemberRepository):
        self.member_repo = member_repo

    def execute(
        self, return_request: ReturnBookRequest, db: Session, current_user: dict
    ) -> Dict[str, Any]:
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

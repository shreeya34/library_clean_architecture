from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from entrypoints.api.member.request import (
    MemberLoginRequest,
    BorrowBookRequest,
    ReturnBookRequest,
)
from entrypoints.api.member.member_response import BorrowedBookResponse
from typing import Dict, Any


class MemberService(ABC):
    @abstractmethod
    def member_logins(
        self, member_login: MemberLoginRequest, db: Session
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def borrow_book(
        self, book_request: BorrowBookRequest, db: Session, current_user: dict
    ) -> BorrowedBookResponse:
        pass

    @abstractmethod
    def return_book(
        self, return_request: ReturnBookRequest, db: Session, current_user: dict
    ) -> Dict[str, Any]:
        pass

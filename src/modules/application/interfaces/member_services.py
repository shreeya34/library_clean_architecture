from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from modules.domain.member.models import MemberLoginRequest, BorrowBookRequest, ReturnBookRequest
from modules.domain.member.response import BorrowedBookResponse
from typing import Dict, Any

class MemberService(ABC):
    @abstractmethod
    def member_logins(self, member_login: MemberLoginRequest, db: Session) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def borrow_book(self, book_request: BorrowBookRequest, db: Session, current_user: dict) -> BorrowedBookResponse:
        pass
    
    @abstractmethod
    def return_book(self, return_request: ReturnBookRequest, db: Session, current_user: dict) -> Dict[str, Any]:
        pass
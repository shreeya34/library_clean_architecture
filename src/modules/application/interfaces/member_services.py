from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from modules.domain.member.models import MemberLogins, BorrowBookRequest, ReturnBookRequest
from modules.domain.member.response import BorrowedBookResponse

class MemberService(ABC):
    @abstractmethod
    def login_member(self, member_login: MemberLogins, db: Session) -> dict:
        pass
    
    @abstractmethod
    def borrow_book(self, book_request: BorrowBookRequest, db: Session, current_user: dict) -> BorrowedBookResponse:
        pass
    
    @abstractmethod
    def return_book(self, return_request: ReturnBookRequest, db: Session, current_user: dict) -> dict:
        pass
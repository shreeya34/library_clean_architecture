from typing import Dict, Any
from sqlalchemy.orm import Session
from modules.domain.repositories.member.member_repositories import IMemberRepository
from modules.application.use_cases.member.borrow_books import BorrowBookUseCase
from modules.application.use_cases.member.member_login import MemberLoginUseCase
from modules.application.use_cases.member.return_books import ReturnBookUseCase

from entrypoints.api.member.request import (
    BorrowBookRequest,
    MemberLoginRequest,
    ReturnBookRequest,
)
from entrypoints.api.member.member_response import (
    BorrowedBookResponse,
    MemberLoginResponse,
)
from modules.domain.services.member_services import MemberService
from modules.infrastructure.shared.decorators.db_exception_handler import db_exception_handler


class LibraryMemberService(MemberService):

    def __init__(self, member_repo: IMemberRepository):
        self.member_repo = member_repo

    @db_exception_handler("member login")
    def member_logins(
        self, member_login: MemberLoginRequest, db: Session
    ) -> MemberLoginResponse:
        usecase = MemberLoginUseCase(self.member_repo)
        return usecase.login_member(member_login, db)

    @db_exception_handler("borrow books")
    def borrow_book(
        self, book_request: BorrowBookRequest, db: Session, current_user: dict
    ) -> BorrowedBookResponse:
        usecase = BorrowBookUseCase(self.member_repo)
        return usecase.borrow_books(book_request, db, current_user)

    @db_exception_handler("return books")
    def return_book(
        self, return_request: ReturnBookRequest, db: Session, current_user: dict
    ) -> Dict[str, Any]:
        """Handles returning a borrowed book by a member."""

        usecase = ReturnBookUseCase(self.member_repo)
        return usecase.return_books(return_request, db, current_user)

from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from entrypoints.api.dependencies.annotated_deps import CurrentUserDep, DBSessionDep
from modules.infrastructure.dependencies.member_dependencies import get_member_service
from modules.infrastructure.security.auth_berarer import JWTBearer
from entrypoints.api.member.request import (
    MemberLoginRequest,
    BorrowBookRequest,
    ReturnBookRequest,
)
from entrypoints.api.member.member_response import BorrowedBookResponse
from modules.domain.exceptions.member.exception import (
    InvalidMemberCredentialsError,
    RaiseBorrowBookError,
)
from modules.application.services.member_services import LibraryMemberService


router = APIRouter()


@router.post("/member/login")
def member_login(
    memberLogin: MemberLoginRequest,
    db: DBSessionDep,
    member_service: LibraryMemberService = Depends(get_member_service),
):
    """
    Endpoint for member login
    """
    try:
        login_result = member_service.member_logins(memberLogin, db)
        return asdict(login_result)
    except InvalidMemberCredentialsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/borrow", response_model=BorrowedBookResponse, dependencies=[Depends(JWTBearer())]
)
def borrow_book(
    book_body: BorrowBookRequest,
    db: DBSessionDep,
    user: CurrentUserDep,
    member_service: LibraryMemberService = Depends(get_member_service),
):
    try:
        borrowed_books = member_service.borrow_book(book_body, db, user)
        if borrowed_books:
            return borrowed_books
        else:
            raise RaiseBorrowBookError()
    except RaiseBorrowBookError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/return_book", dependencies=[Depends(JWTBearer())])
def return_books(
    book_body: ReturnBookRequest,
    db: DBSessionDep,
    user: CurrentUserDep,
    member_service: LibraryMemberService = Depends(get_member_service),
):

    returned_books = member_service.return_book(book_body, db, user)
    if returned_books:
        return {
            "message": "Book returned successfully",
            "returned_books": returned_books,
        }

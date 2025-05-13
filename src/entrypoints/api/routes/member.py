from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modules.infrastructure.database.dependency import get_db_from_app
from modules.infrastructure.dependencies.member_dependencies import get_member_service
from modules.infrastructure.security.auth_berarer import JWTBearer
from modules.infrastructure.security.auth_handler import get_current_user
from modules.interfaces.request.member_request import (
    MemberLoginRequest,
    BorrowBookRequest,
    ReturnBookRequest,
)
from modules.interfaces.response.member_response import BorrowedBookResponse
from modules.domain.exceptions.member.exception import (
    RaiseBorrowBookError,
)
from modules.application.services.member_services import LibraryMemberService


router = APIRouter()


@router.post("/member/login")
def member_login(
    memberLogin: MemberLoginRequest,
    db: Session = Depends(get_db_from_app),
    member_service: LibraryMemberService = Depends(get_member_service),
):
    """
    Endpoint for member login
    """
    login_result = member_service.member_logins(memberLogin, db)
    return {
        "message": "Login Success",
        "member_id": login_result["member_id"],
        "token": login_result["token"],
    }


@router.post(
    "/borrow", response_model=BorrowedBookResponse, dependencies=[Depends(JWTBearer())]
)
def borrow_book(
    book_body: BorrowBookRequest,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
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
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
    member_service: LibraryMemberService = Depends(get_member_service),
):

    returned_books = member_service.return_book(book_body, db, user)
    if returned_books:
        return {
            "message": "Book returned successfully",
            "returned_books": returned_books,
        }

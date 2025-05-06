from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modules.infrastructure.database.dependency import get_db_from_app
from modules.infrastructure.security.auth_berarer import JWTBearer
from modules.infrastructure.security.auth_handler import get_current_user
from modules.domain.member.models import (
    
    BorrowBookRequest,
    ReturnBookRequest,
)
from modules.domain.member.response import BorrowedBookResponse
from modules.domain.exceptions.member.exception import (
    RaiseBookError,
    RaiseBorrowBookError,
   
)
from modules.infrastructure.services.member_services import (
    member_logins,
    get_borrowed_books_data,
    get_returned_books_data,
)
from modules.infrastructure.logger import get_logger

logger = get_logger()


router = APIRouter()


from modules.domain.member.models import MemberLoginRequest

@router.post("/member/login")
def member_login(
    memberLogin: MemberLoginRequest,
    db: Session = Depends(get_db_from_app)
):
    """
    Endpoint for member login
    """
    # try:
    login_result = member_logins(memberLogin, db)
    return {
            "message": "Login Success",
            "member_id": login_result["member_id"],
            "token": login_result["token"],
        }
    # except Exception as e:
    #     logger.error(f"Internal Server Error: {str(e)}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Internal Server Error: {str(e)}"
    #     )


@router.post(
    "/borrow", response_model=BorrowedBookResponse, dependencies=[Depends(JWTBearer())]
)
def borrow_book(
    book_body: BorrowBookRequest,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    borrowed_books = get_borrowed_books_data(book_body, db, user)
    if borrowed_books:
        return borrowed_books
    else:
        raise RaiseBorrowBookError()


@router.post("/return_book", dependencies=[Depends(JWTBearer())])
def return_books(
    book_body: ReturnBookRequest,
    # db: Session = Depends(get_db),
    db: Session = Depends(get_db_from_app),

    user: dict = Depends(get_current_user),
):
    
    returned_books = get_returned_books_data(book_body, db, user)
    if returned_books:
        return {
            "message": "Book returned successfully",
            "returned_books": returned_books,
        }
    else:
        raise RaiseBookError()
    
    

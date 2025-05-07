from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modules.infrastructure.database.dependency import get_db_from_app
from modules.infrastructure.security.auth_berarer import JWTBearer
from modules.infrastructure.security.auth_handler import get_current_user
from modules.domain.member.models import (
    MemberLoginRequest,
    BorrowBookRequest,
    ReturnBookRequest,
)
from modules.domain.member.response import BorrowedBookResponse
from modules.domain.exceptions.member.exception import (
    BookAlreadyReturnedError,
    BookNotBorrowedError,
    RaiseBookError,
    RaiseBorrowBookError,
)
from modules.infrastructure.services.member_services import member_service
from modules.infrastructure.logger import get_logger

logger = get_logger()

router = APIRouter()

@router.post("/member/login")
def member_login(
    memberLogin: MemberLoginRequest,
    db: Session = Depends(get_db_from_app)
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
):
    borrowed_books = member_service.borrow_book(book_body, db, user)
    if borrowed_books:
        return borrowed_books
    else:
        raise RaiseBorrowBookError()

@router.post("/return_book", dependencies=[Depends(JWTBearer())])
def return_books(
    book_body: ReturnBookRequest,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    try:
        returned_books = member_service.return_book(book_body, db, user)
        if returned_books:
            return {
                "message": "Book returned successfully",
                "returned_books": returned_books,
            }
        
    except BookNotBorrowedError as e:
            logger.warning(str(e))
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    except BookAlreadyReturnedError as e:
            logger.warning(str(e))
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
            raise RaiseBookError()
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from modules.infrastructure.database.dependency import get_db_from_app
from modules.infrastructure.security.auth_berarer import JWTBearer
from modules.infrastructure.security.auth_handler import get_current_user
from modules.domain.member.models import (
    MemberLogins,
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


@router.post("/member/login")
def member_login(
    memberLogin: MemberLogins, 
                #  db: Session = Depends(get_db)):
        db: Session = Depends(get_db_from_app)
        ):

    login_member = member_logins(memberLogin, db)
    if login_member:
        return {
            "message": "Login Success",
            "member_id": login_member["member_id"],
            "token": login_member["token"],
        }
    else:
        return {"error": "Invalid credentials"}


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
    
    

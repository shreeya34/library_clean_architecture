from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from modules.infrastructure.config import settings
from modules.infrastructure.database.utils import commit_and_refresh
from modules.domain.exceptions.admin.exception import (
    BookNotFoundError,
    BookUnavailableError,
     InvalidMemberCredentialsError,
    MemberNotFoundError
  
)

from modules.domain.exceptions.admin.exception import RaiseUnauthorizedError

from modules.infrastructure.database.models.member import BorrowedBooks, ReturnBook
from modules.infrastructure.database.models.admin import  Member
from modules.domain.member.models import (
    BorrowBookRequest,
    MemberLogins,
    ReturnBookRequest,
)
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.infrastructure.security.auth_handler import get_current_user, signJWT
from modules.infrastructure.logger import get_logger
from modules.domain.member.response import BorrowedBookResponse
from modules.infrastructure.repositories.admin_repositories import get_member_by_name
from modules.domain.exceptions.member.exception import BookNotBorrowedError, DuplicateBookBorrowError
from modules.infrastructure.repositories.member_repositories import create_member_login, get_book_by_title

logger = get_logger()

postgres_manager = PostgresManager(settings)


def member_logins(memberLogin: MemberLogins, db: Session = Depends( postgres_manager.get_db)) -> dict:

    logger.info(f"Login for: {memberLogin.name}")

    member = get_member_by_name(db, memberLogin.name)
    if not member:
        logger.warning(
            "Failed login attempt for non-existent member: %s", memberLogin.name
        )
        raise InvalidMemberCredentialsError(memberLogin.name)

    access_token = signJWT(member.name, member.member_id, is_admin=False)
    logger.info(f"Login successful for user: {memberLogin.name}")

    new_login = create_member_login(db, member.member_id, memberLogin.name)

    return {
        "message": "Login successful",
        "member_id": member.member_id,
        "token": access_token,
    }


def get_borrowed_books_data(
    book_body: BorrowBookRequest,
    db: Session = Depends( postgres_manager.get_db),
    user: dict = Depends(get_current_user),
) -> dict:
    book_title = book_body.book_title
    user_id = user.get("admin_id")
    if not user_id:
        logger.error("Borrow attempt by user without valid user_id in token")
        raise RaiseUnauthorizedError()

    member = db.query(Member).filter(Member.member_id == user_id).first()
    if not member:
        logger.error("Borrow attempt by non-existent member: %s", user_id)
        raise MemberNotFoundError(user_id)

    book = get_book_by_title(db, book_title)
    if not book or book.stock <= 0:
        logger.warning("Borrow attempt for unavailable book: %s", book_title)
        raise BookUnavailableError(book_title)
    
    already_borrowed = db.query(BorrowedBooks).filter(
        BorrowedBooks.book_id == book.id,
        BorrowedBooks.member_id == member.member_id
    ).first()

    if already_borrowed:
        logger.warning("Duplicate borrow attempt: %s by user %s", book.title, member.name)
        raise DuplicateBookBorrowError(book.title)

    borrow_date = datetime.now()
    expiry_date = borrow_date + timedelta(weeks=2)

    borrowed_book = BorrowedBooks(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        borrow_date=borrow_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
    )

    book.stock -= 1
    commit_and_refresh(db, borrowed_book)

    logger.info("Book borrowed: %s by %s", book.title, member.name)
    return BorrowedBookResponse(
        title=book.title,
        member_id=member.member_id,
        name=member.name,
        borrow_date=borrow_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
    )


def get_returned_books_data(
    book_body: ReturnBookRequest,
    db: Session = Depends( postgres_manager.get_db),
    user: dict = Depends(get_current_user),
) -> dict:
    book_title = book_body.book_title
    user_id = user.get("admin_id")
    if not user_id:
        logger.error("Return attempt by user without valid user_id in token")
        raise RaiseUnauthorizedError()

    member = db.query(Member).filter(Member.member_id == user_id).first()

    if not member:
        logger.error("Return attempt by non-existent member: %s", user_id)
        raise MemberNotFoundError(user_id)

    book = get_book_by_title(db, book_title)
    if not book:
        logger.warning("Return attempt for non-existent book: %s", book_title)
        raise BookNotFoundError(book_title)
    borrowed_book = db.query(BorrowedBooks).filter(
        BorrowedBooks.book_id == book.id,
        BorrowedBooks.member_id == member.member_id
    ).first()
       
    if not borrowed_book:
        logger.warning("Book %s is not borrowed by member %s", book_title, member.name)
        raise BookNotBorrowedError(book_title)
    
    return_date = datetime.now()
    returned_book = ReturnBook(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        return_date=return_date,
    )
    db.delete(borrowed_book)
    db.commit() 

    book.stock += 1
    commit_and_refresh(db, returned_book)

    logger.info("Book returned: %s by %s", book.title, member.name)

    return {
        "book_title": book.title,
        "name": member.name,
        "return_date": return_date.isoformat(),
    }

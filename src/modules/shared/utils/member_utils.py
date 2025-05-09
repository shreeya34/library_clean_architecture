import uuid
from datetime import datetime, timedelta
from modules.infrastructure.database.models.member import BorrowedBooks
from modules.infrastructure.database.models.admin import Member,Book

from modules.domain.exceptions.member.exception import (
    InvalidUUIDError)

def parse_uuid(id_str: str) -> uuid.UUID:
    try:
        return uuid.UUID(id_str)
    except ValueError:
        raise InvalidUUIDError()

def create_borrowed_book_entry(book: Book, member: Member) -> BorrowedBooks:
    borrow_date = datetime.now()
    expiry_date = borrow_date + timedelta(weeks=2)
    return BorrowedBooks(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        borrow_date=borrow_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
    )


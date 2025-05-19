

from datetime import datetime, timedelta
from modules.infrastructure.database.models.admin import Book, Member
from modules.infrastructure.database.models.member import BorrowedBooks


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

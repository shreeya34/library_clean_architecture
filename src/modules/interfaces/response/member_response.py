from dataclasses import dataclass
from datetime import datetime


@dataclass
class BorrowedBookResponse:
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime


@dataclass
class BorrowBookSuccessResponse:
    message: str
    borrowed_book: BorrowedBookResponse


@dataclass
class ReturnedBookResponse:
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime

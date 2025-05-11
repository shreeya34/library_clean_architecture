from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemberLoginRequest:
    name: str
    password: str


@dataclass
class MemberLoginInfo:
    name: str
    status: str
    login_time: datetime


@dataclass
class ReturnBookRequest:
    book_title: str


@dataclass
class BorrowBookRequest:
    book_title: str

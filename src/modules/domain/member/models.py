from pydantic import BaseModel


class MemberLogins(BaseModel):
    name: str
    password: str


class ReturnBookRequest(BaseModel):
    book_title: str


class BorrowBookRequest(BaseModel):
    book_title: str

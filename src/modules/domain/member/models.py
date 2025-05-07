


from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class MemberLoginRequest(BaseModel):
    name: str
    password: str

class MemberLoginInfo(BaseModel):
    name: str
    status: str
    login_time: datetime
    
    class Config:
        from_attributes = True 


class ReturnBookRequest(BaseModel):
    book_title: str


class BorrowBookRequest(BaseModel):
    book_title: str

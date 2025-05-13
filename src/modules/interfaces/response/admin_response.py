from dataclasses import dataclass
from pydantic import BaseModel
from typing import List
from uuid import UUID


# admin

@dataclass
class AdminResponseModel:
    admin_id: str
    username: str

    class Config:
        orm_mode = True
@dataclass
class AdminLoginResponse:
    message: str
    token: str
    admin_id: str

    class Config:
        orm_mode = True 
   

class MemberResponse(BaseModel):
    name: str
    role: str
    member_id: str

    class Config:
        orm_mode = True
        from_attributes = True


class MemberAddResponse(BaseModel):
    message: str
    new_member: MemberResponse
    plain_password: str  


class MembersListResponse(BaseModel):
    filtered_members: list[MemberResponse]


class BookResponseModel(BaseModel):
    id: UUID
    title: str
    author: str
    stock: int
    available: bool

    class Config:
        orm_mode = True
        from_attributes = True
class BookAddResponse(BaseModel):
    message: str
    new_book: BookResponseModel


class BookAvailabilityResponse(BaseModel):
    title: str
    author: str
    available: bool


class BookViewResponse(BaseModel):
    message: str
    books: List[BookAvailabilityResponse]
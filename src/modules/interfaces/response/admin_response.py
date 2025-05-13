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
   
@dataclass   
class MemberResponse:
    name: str
    role: str
    member_id: str

    class Config:
        orm_mode = True
        from_attributes = True
@dataclass       
class MemberAddResponse:
    message: str
    new_member: MemberResponse
    plain_password: str  
@dataclass
class MembersListResponse:
    filtered_members: List[MemberResponse]

@dataclass
class BookResponseModel:
    id: UUID
    title: str
    author: str
    stock: int
    available: bool

    class Config:
        orm_mode = True
        from_attributes = True
@dataclass
class BookAddResponse:
    message: str
    new_book: BookResponseModel

@dataclass
class BookAvailabilityResponse:
    title: str
    author: str
    available: bool

@dataclass
class BookViewResponse(BaseModel):
    message: str
    books: List[BookAvailabilityResponse]
from pydantic import BaseModel
from typing import List
from uuid import UUID


# admin
class MemberResponse(BaseModel):
    name: str
    role: str
    member_id: str

    class Config:
        orm_mode = True
        from_attributes = True


class MembersListResponse(BaseModel):
    filtered_members: List[MemberResponse]


class BookResponseModel(BaseModel):
    id: UUID
    title: str
    author: str
    stock: int
    available: bool

    class Config:
        orm_mode = True
        from_attributes = True

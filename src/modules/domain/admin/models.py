from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class CreateModel(BaseModel):
    username: str
    password: str


class AdminLogins(BaseModel):
    username: str
    status: Optional[str] = None 
    password: str


class NewMember(BaseModel):
    name: str
    role: str


class NewBooks(BaseModel):
    title: str
    author: str
    stock: int
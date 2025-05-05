from datetime import datetime
from typing import List
from pydantic import BaseModel


class CreateModel(BaseModel):
    username: str
    password: str


class AdminLogins(BaseModel):
    username: str
    status: str
    password: str


class NewMember(BaseModel):
    name: str
    role: str


class NewBooks(BaseModel):
    title: str
    author: str
    stock: int
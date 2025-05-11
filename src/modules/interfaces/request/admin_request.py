from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateModel:
    username: str
    password: str


@dataclass
class AdminLogins:
    username: str
    password: str
    status: Optional[str] = None



@dataclass
class NewMember:
    name: str
    role: str


@dataclass
class NewBooks:
    title: str
    author: str
    stock: int

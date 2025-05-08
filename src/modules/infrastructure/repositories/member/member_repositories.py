# modules/domain/interfaces/member_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import Book, Member


class IMemberRepository(ABC):
    @abstractmethod
    def get_member_by_name(self, db: Session, name: str) -> Member:
        pass

    @abstractmethod
    def create_member_login(self, db: Session, member_id: UUID, name: str):
        pass

    @abstractmethod
    def get_book_by_title(self, db: Session, title: str) -> Book:
        pass

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import (
    Admin,
    Book,
    BookAvailability,
    Member,
    ViewMembers,
)


class IAdminRepository(ABC):
    @abstractmethod
    def get_admin_by_username(self, db: Session, username: str) -> Admin:
        pass

    @abstractmethod
    def get_member_by_name(self, db: Session, name: str) -> Member:
        pass

    @abstractmethod
    def get_all_members(self, db: Session) -> list[Member]:
        pass

    @abstractmethod
    def get_view_member_by_id(self, db: Session, member_id: str) -> ViewMembers:
        pass

    @abstractmethod
    def get_all_view_members(self, db: Session) -> list[ViewMembers]:
        pass

    @abstractmethod
    def get_member_by_id(self, db: Session, member_id: str) -> Member:
        pass

    @abstractmethod
    def get_book_availability_by_book_id(
        self, db: Session, book_id: int
    ) -> BookAvailability:
        pass

    @abstractmethod
    def get_existing_book(self, db: Session, newbook: Book) -> Book:
        pass

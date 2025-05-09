from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from modules.interfaces.request.admin_request import (
    CreateModel,
    AdminLogins,
    NewMember,
    NewBooks,
)
from modules.interfaces.response.admin_response import (
    MemberResponse,
    MembersListResponse,
)


class AdminServiceInterface(ABC):
    @abstractmethod
    def create_admin(self, admin: CreateModel, db: Session) -> dict:
        pass

    @abstractmethod
    def login_admin(self, admin_data: AdminLogins, db: Session) -> dict:
        pass

    @abstractmethod
    def add_member(self, newuser: NewMember, db: Session, current_user: dict) -> dict:
        pass

    @abstractmethod
    def add_books(self, newbook: NewBooks, db: Session, current_user: dict) -> dict:
        pass

    @abstractmethod
    def view_available_books(self, title: str, db: Session, current_user: dict) -> dict:
        pass

    @abstractmethod
    def view_all_members(self, db: Session, current_user: dict) -> MembersListResponse:
        pass

    @abstractmethod
    def view_member_by_id(
        self, member_id: str, db: Session, current_user: dict
    ) -> MemberResponse:
        pass

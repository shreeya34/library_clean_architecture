from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import Admin, Member
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.security.password_utils import hash_password
from modules.domain.exceptions.admin.exception import (
    AdminAlreadyExistsError,
    MemberAlreadyExistsError,
)
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.interfaces.request.admin_request import CreateModel
from modules.interfaces.response.admin_response import AdminResponseModel
import uuid


def create_admin_entity(username: str, password: str) -> Admin:
    return Admin(
        admin_id=str(uuid.uuid4()),
        username=username,
        password=hash_password(password),
        role="admin",
    )


def create_member_entity(name: str, password: str) -> Member:
    return Member(
        member_id=str(uuid.uuid4()),
        name=name,
        password=hash_password(password),
        role="admin",
    )


class CreateAdminUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, admin: CreateModel) -> dict:
        if self.admin_repo.get_admin_by_username(db, admin.username):
            raise AdminAlreadyExistsError(admin.username)
        if self.admin_repo.get_member_by_name(db, admin.username):
            raise MemberAlreadyExistsError(admin.username)

        admin_entity = create_admin_entity(admin.username, admin.password)
        member_entity = create_member_entity(admin.username, admin.password)

        commit_and_refresh(db, admin_entity)
        commit_and_refresh(db, member_entity)

        return (
            AdminResponseModel(
                admin_id=admin_entity.admin_id, username=admin_entity.username
            )
        ).dict()

import uuid
from sqlalchemy.orm import Session
from modules.domain.factories.member_factory import MemberFactory
from entrypoints.api.admin.request import NewMember
from entrypoints.api.admin.response import MemberAddResponse, MemberResponse
from modules.infrastructure.security.password_utils import (
    generate_random_password,
    hash_password,
)
from modules.domain.exceptions.admin.exception import MemberAlreadyExistsError
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Member
from modules.domain.repositories.admin.admin_repositories import IAdminRepository


def generate_credentials() -> tuple[str, str]:
    plain = generate_random_password()
    hashed = hash_password(plain)
    return plain, hashed


def create_new_member(name: str, role: str, hashed_password: str) -> Member:
    return MemberFactory.create_member(name=name, role=role, password=hashed_password)


class AddMemberUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def register_member(self, db: Session, newuser: NewMember) -> MemberAddResponse:
        if self.admin_repo.get_member_by_name(db, newuser.name):
            raise MemberAlreadyExistsError(newuser.name)

        plain_password, hashed_password = generate_credentials()

        new_member = create_new_member(newuser.name, newuser.role, hashed_password)

        commit_and_refresh(db, new_member)

        return MemberAddResponse(
            message="Member added successfully",
            new_member=MemberResponse.from_orm(new_member),
            plain_password=plain_password,
        )

# modules/domain/use_cases/add_member_use_case.py

import uuid
from sqlalchemy.orm import Session
from modules.domain.factories.member_factory import MemberFactory
from modules.interfaces.request.admin_request import NewMember
from modules.interfaces.response.admin_response import MemberAddResponse, MemberResponse
from modules.infrastructure.security.password_utils import generate_random_password, hash_password
from modules.domain.exceptions.admin.exception import MemberAlreadyExistsError
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Member
from modules.domain.repositories.admin.admin_repositories import IAdminRepository


class AddMemberUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, newuser: NewMember) -> MemberAddResponse:
        if self.admin_repo.get_member_by_name(db, newuser.name):
            raise MemberAlreadyExistsError(newuser.name)

        plain_password = generate_random_password()
        hashed_password = hash_password(plain_password)

        new_member = MemberFactory.create_member(
            name=newuser.name,
            role=newuser.role,
            password=hashed_password,
        )

        commit_and_refresh(db, new_member)

        return MemberAddResponse(
            message="Member added successfully",
            new_member=MemberResponse.from_orm(new_member),
            plain_password=plain_password,
        )

from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import Admin, Member
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.security.password_utils import hash_password
from modules.domain.exceptions.admin.exception import AdminAlreadyExistsError
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.interfaces.request.admin_request import CreateModel
from modules.interfaces.response.admin_response import AdminResponseModel
import uuid
from dataclasses import asdict

class CreateAdminUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, admin: CreateModel) -> dict:
        if self.admin_repo.get_admin_by_username(db, admin.username):
            raise AdminAlreadyExistsError(admin.username)

        admin_entity = Admin(
            admin_id=str(uuid.uuid4()),
            username=admin.username,
            password=hash_password(admin.password),
            role="admin",
        )
        commit_and_refresh(db, admin_entity)

        member_entity = Member(
            member_id=str(uuid.uuid4()),
            name=admin.username,
            password=hash_password(admin.password),
            role="admin",
        )
        commit_and_refresh(db, member_entity)

        return asdict(AdminResponseModel(admin_id=admin_entity.admin_id, username=admin_entity.username))

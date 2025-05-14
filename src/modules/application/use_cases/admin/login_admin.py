from datetime import datetime
from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import AdminLogin
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.security.password_utils import check_password
from modules.infrastructure.security.auth_handler import signJWT
from modules.interfaces.request.admin_request import AdminLogins
from modules.interfaces.response.admin_response import AdminLoginResponse
from modules.domain.exceptions.admin.exception import (
    AdminAccessDeniedError,
    InvalidAdminCredentialsError,
)
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from dataclasses import asdict


def create_admin_login_entity(username: str, password: str, member_id: str) -> AdminLogin:
    return AdminLogin(
        username=username,
        status="success",
        login_time=datetime.utcnow(),
        password=password,
        member_id=member_id,
    )


def create_login_response(token: str, admin_id: str) -> AdminLoginResponse:
    return AdminLoginResponse(
        message="Login successful",
        token=token,
        admin_id=admin_id,
    )


class LoginAdminUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, login_data: AdminLogins) -> dict:
        admin = self.admin_repo.get_admin_by_username(db, login_data.username)
        if not admin:
            raise AdminAccessDeniedError(login_data.username)

        if not check_password(login_data.password, admin.password):
            raise InvalidAdminCredentialsError(login_data.username)

        token_response = signJWT(admin.username, admin.admin_id, is_admin=True)

        login_entity = create_admin_login_entity(
            username=login_data.username,
            password=login_data.password,
            member_id=admin.admin_id,
        )

        commit_and_refresh(db, login_entity)

        return asdict(create_login_response(token_response["access_token"], admin.admin_id))

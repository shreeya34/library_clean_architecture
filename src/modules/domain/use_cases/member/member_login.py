from modules.domain.exceptions.member.exception import InvalidMemberCredentialsError
from modules.domain.repositories.member.member_repositories import IMemberRepository
from modules.infrastructure.logger import get_logger
from modules.infrastructure.security.auth_handler import signJWT
from modules.infrastructure.security.password_utils import check_password
from modules.interfaces.request.member_request import MemberLoginRequest
from modules.interfaces.response.member_response import MemberLoginResponse
from sqlalchemy.orm import Session

logger = get_logger()


class MemberLoginUseCase:
    def __init__(self, member_repo: IMemberRepository):
        self.member_repo = member_repo

    def execute(
        self, member_login: MemberLoginRequest, db: Session
    ) -> MemberLoginResponse:
        member = self.member_repo.get_member_by_name(db, member_login.name)
        if not member or not check_password(member_login.password, member.password):
            logger.warning(f"Invalid credentials for: {member_login.name}")
            raise InvalidMemberCredentialsError(member_login.name)

        token = signJWT(member.name, member.member_id, is_admin=False)
        self.member_repo.create_member_login(db, member.member_id, member.name)
        db.commit()

        logger.info(f"User {member_login.name} logged in successfully.")

        return MemberLoginResponse(
            message="Login successful",
            member_id=member.member_id,
            token=token,
        )

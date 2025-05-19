from sqlalchemy.orm import Session
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from entrypoints.api.admin.response import MemberResponse
from modules.domain.exceptions.admin.exception import MemberNotFoundError


class ViewMemberByIdUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def get_member_by_id(self, db: Session, member_id: str) -> dict:
        member = self.admin_repo.get_member_by_id(db, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        return MemberResponse(
            name=member.name,
            role=member.role,
            member_id=member.member_id,
        ).dict()

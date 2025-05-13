from sqlalchemy.orm import Session
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.interfaces.response.admin_response import MembersListResponse


class ViewMembersUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session) -> dict:
        members = self.admin_repo.get_all_members(db)
        if not members:
            return {"message": "No members found"}

        member_data = [
            {"name": m.name, "role": m.role, "member_id": m.member_id} for m in members
        ]
        return MembersListResponse(filtered_members=member_data).dict()

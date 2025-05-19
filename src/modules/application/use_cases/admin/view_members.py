from sqlalchemy.orm import Session
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from entrypoints.api.admin.response import MembersListResponse


class ViewMembersUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def view_members(
        self, db: Session, limit: int, offset: int, page: int, page_size: int
    ) -> dict:
        members, total_count = self.admin_repo.get_all_members(db, limit, offset)
        if not members:
            return {"message": "No members found"}

        member_data = [
            {"name": m.name, "role": m.role, "member_id": m.member_id} for m in members
        ]
        result = {
            "total": total_count,
            "count": len(member_data),
            "page": page,
            "page_size": page_size,
            "filtered_members": member_data,
        }

        return result

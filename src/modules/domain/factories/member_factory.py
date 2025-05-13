import uuid
from modules.infrastructure.database.models.admin import Member


class MemberFactory:
    @staticmethod
    def create_member(name: str, role: str, password: str) -> Member:
        return Member(
            member_id=str(uuid.uuid4()),
            name=name,
            role=role,
            password=password,
        )

from fastapi import Depends

from modules.infrastructure.repositories.member.member_repository_impl import (
    MemberRepository,
)
from modules.infrastructure.services.member_services import LibraryMemberService


def get_member_service(member_repo: MemberRepository = Depends(MemberRepository)):
    return LibraryMemberService(member_repo)

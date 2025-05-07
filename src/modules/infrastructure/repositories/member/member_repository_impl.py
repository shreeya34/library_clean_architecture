from modules.infrastructure.repositories.member.member_repositories import IMemberRepository
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID

from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Book, Member
from modules.infrastructure.database.models.member import MemberLogins as MemberLoginsDB

class MemberRepository(IMemberRepository):
    def get_member_by_name(self, db, name):
        return db.query(Member).filter(Member.name == name).first()

    def create_member_login(self, db, member_id, name):
        new_login = MemberLoginsDB(
            name=name,
            status="success",
            login_time=datetime.utcnow(),
            member_id=member_id,
        )
        commit_and_refresh(db, new_login)
        return new_login

    def get_book_by_title(self, db, title):
        return db.query(Book).filter(Book.title == title).first()

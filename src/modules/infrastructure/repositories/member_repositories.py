from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID

from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Book, Member
from modules.infrastructure.database.models.member import MemberLogins as MemberLoginsDB



def get_member_by_name(db: Session, name: str) -> Member:
    return db.query(Member).filter(Member.name == name).first()


def create_member_login(db: Session, member_id: UUID, name: str) -> MemberLoginsDB:
   
    new_login = MemberLoginsDB(
        name=name,
        status="success",
        login_time=datetime.utcnow(),
        member_id=member_id,
    )
    commit_and_refresh(db, new_login)
    return new_login


def get_book_by_title(db: Session, title: str) -> Book:
    return db.query(Book).filter(Book.title == title).first()

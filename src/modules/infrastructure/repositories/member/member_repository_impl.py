from typing import List
from modules.domain.repositories.member.member_repositories import (
    IMemberRepository,
)
from sqlalchemy.orm import Session

from datetime import datetime
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Book, Member
from modules.infrastructure.database.models.member import BorrowedBooks, MemberLogins as MemberLoginsDB


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

    def get_available_books_by_title(self, db: Session, title: str) -> List[Book]:
        return (
            db.query(Book)
            .filter(Book.title == title, Book.stock > 0)
            .all()
        )

    def has_already_borrowed(self, db: Session, book_id: int, member_id: str) -> bool:
        return (
            db.query(BorrowedBooks)
            .filter(BorrowedBooks.book_id == book_id, BorrowedBooks.member_id == member_id)
            .first()
            is not None
        )

    def save_borrowed_book(self, db: Session, borrowed_book: BorrowedBooks):
        db.add(borrowed_book)
        db.commit()
        db.refresh(borrowed_book)
        
    def get_member_by_id(self, db: Session, member_id: str) -> Member:
        return db.query(Member).filter(Member.member_id == member_id).first()
    
    def get_borrowed_book(self, db: Session, book_id: int, member_id: str) -> BorrowedBooks | None:
        return (
        db.query(BorrowedBooks)
        .filter(BorrowedBooks.book_id == book_id, BorrowedBooks.member_id == member_id)
        .first()
    )

    def delete_borrowed_book(self, db: Session, borrowed_book: BorrowedBooks):
        db.delete(borrowed_book)
        db.commit()
        
    def get_user_by_id(self, db: Session, user_id: str) -> Member:
        return db.query(Member).filter(Member.member_id == user_id).first()


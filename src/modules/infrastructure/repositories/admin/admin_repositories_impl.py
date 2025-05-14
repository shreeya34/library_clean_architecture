from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import (
    Admin,
    Book,
    BookAvailability,
    Member,
    ViewMembers,
)
from modules.domain.repositories.admin.admin_repositories import (
    IAdminRepository,
)


class AdminRepository(IAdminRepository):

    def get_admin_by_username(self, db: Session, username: str) -> Admin:
        return db.query(Admin).filter(Admin.username == username).first()

    def get_member_by_name(self, db: Session, name: str) -> Member:
        return db.query(Member).filter(Member.name == name).first()

    def get_all_members(self, db: Session, limit: int, offset: int) -> tuple[list[Member], int]:
        members = db.query(Member).offset(offset).limit(limit).all()
        total_count = db.query(Member).count()
        return members, total_count

    def get_view_member_by_id(self, db: Session, member_id: str) -> ViewMembers:
        return db.query(ViewMembers).filter(ViewMembers.member_id == member_id).first()

    def get_all_view_members(self, db: Session) -> list[ViewMembers]:
        return db.query(ViewMembers).all()

    def get_member_by_id(self, db: Session, member_id: str) -> Member:
        return db.query(Member).filter(Member.member_id == member_id).first()

    def get_existing_book(self, db: Session, newbook: Book) -> Book:
        return (
            db.query(Book)
            .filter(Book.title == newbook.title, Book.author == newbook.author)
            .first()
        )

    def get_books_by_title(self, db: Session, title: str):
        return db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()

    def get_all_books(self, db: Session):
        return db.query(Book).all()

    def get_availability_by_book_id(self, db: Session, book_id: int):
        return (
            db.query(BookAvailability)
            .filter(BookAvailability.book_id == book_id)
            .first()
        )

    def add_availability(self, db: Session, availability: BookAvailability):
        return db.add(availability)

    def upsert_availability(
        self, db: Session, book_id: int, title: str, available: bool
    ):
        record = self.get_availability_by_book_id(db, book_id)
        if record:
            record.available = available
        else:
            new_record = BookAvailability(
                book_id=book_id, title=title, available=available
            )
            db.add(new_record)

    def commit(self, db: Session):
        return db.commit()

    def rollback(self, db: Session):
        return db.rollback()

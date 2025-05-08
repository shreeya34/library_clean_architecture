from sqlalchemy.orm import Session
from modules.infrastructure.database.models.admin import (
    Admin,
    Book,
    BookAvailability,
    Member,
    ViewMembers,
)
from modules.infrastructure.repositories.admin.admin_repositories import (
    IAdminRepository,
)


class AdminRepository(IAdminRepository):
    def get_admin_by_username(self, db: Session, username: str) -> Admin:
        return db.query(Admin).filter(Admin.username == username).first()

    def get_member_by_name(self, db: Session, name: str) -> Member:
        return db.query(Member).filter(Member.name == name).first()

    def get_all_members(self, db: Session) -> list[Member]:
        return db.query(Member).all()

    def get_view_member_by_id(self, db: Session, member_id: str) -> ViewMembers:
        return db.query(ViewMembers).filter(ViewMembers.member_id == member_id).first()

    def get_all_view_members(self, db: Session) -> list[ViewMembers]:
        return db.query(ViewMembers).all()

    def get_member_by_id(self, db: Session, member_id: str) -> Member:
        return db.query(Member).filter(Member.member_id == member_id).first()

    def get_book_availability_by_book_id(
        self, db: Session, book_id: int
    ) -> BookAvailability:
        return (
            db.query(BookAvailability)
            .filter(BookAvailability.book_id == book_id)
            .first()
        )

    def get_existing_book(self, db: Session, newbook: Book) -> Book:
        return (
            db.query(Book)
            .filter(Book.title == newbook.title, Book.author == newbook.author)
            .first()
        )

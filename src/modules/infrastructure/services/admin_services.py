from datetime import datetime
from sqlalchemy.orm import Session
from modules.application.interfaces.admin_services import AdminServiceInterface
from modules.application.models.request.admin_request import (
    CreateModel,
    AdminLogins,
    NewMember,
    NewBooks,
)
from modules.application.models.response.admin_response import (
    BookResponseModel,
    MemberResponse,
    MembersListResponse,
)
from modules.infrastructure.database.models.admin import (
    Admin,
    AdminLogin,
    Book,
    BookAvailability,
    Member,
)
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.infrastructure.security.auth_handler import signJWT
from modules.infrastructure.database.utils import commit_and_refresh


from modules.infrastructure.security.password_utils import (
    generate_random_password,
    hash_password,
    check_password,
)
from modules.infrastructure.logger import get_logger
import uuid
from modules.domain.exceptions.admin.exception import (
    AdminAccessDeniedError,
    AdminAlreadyExistsError,
    InvalidAdminCredentialsError,
    MemberAlreadyExistsError,
    MemberNotFoundError,
)


logger = get_logger()


class AdminService(AdminServiceInterface):

    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def _check_admin(self, current_user: dict):
        if not current_user.get("is_admin"):
            raise AdminAccessDeniedError()

    def create_admin(self, admin: CreateModel, db: Session) -> dict:
        try:
            existing_admin = self.admin_repo.get_admin_by_username(db, admin.username)
            if existing_admin:
                logger.warning(f"Admin {admin.username} already exists.")
                raise AdminAlreadyExistsError(admin.username)

            admin_id = str(uuid.uuid4())
            hashed_password = hash_password(admin.password)

            new_admin = Admin(
                admin_id=admin_id,
                username=admin.username,
                password=hashed_password,
                role="admin",
            )

            commit_and_refresh(db, new_admin)

            logger.info(f"Created new admin {admin.username}")

            return {"admin_id": new_admin.admin_id, "username": new_admin.username}

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create admin {admin.username}: {str(e)}")
            raise

    def login_admin(self, admin_data: AdminLogins, db: Session) -> dict:
        try:
            admin = self.admin_repo.get_admin_by_username(db, admin_data.username)
            if not admin or not check_password(admin_data.password, admin.password):
                logger.warning(f"Failed login attempt for admin {admin_data.username}")
                raise InvalidAdminCredentialsError(admin_data.username)

            access_token = signJWT(admin.username, admin.admin_id, is_admin=True)
            new_login = AdminLogin(
                username=admin_data.username,
                status="success",
                login_time=datetime.utcnow(),
                password=admin_data.password,
                member_id=admin.admin_id,
            )

            commit_and_refresh(db, new_login)

            logger.info(f"Admin {admin_data.username} logged in successfully.")

            return {
                "message": "Login successful",
                "token": access_token,
                "admin_id": admin.admin_id,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create admin {admin.username}: {str(e)}")
            raise

    def add_member(self, newuser: NewMember, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        try:
            existing_member = self.admin_repo.get_member_by_name(db, newuser.name)
            if existing_member:
                logger.warning(f"Member {newuser.name} already exists.")
                raise MemberAlreadyExistsError(newuser.name)

            new_member_id = str(uuid.uuid4())
            plain_password = generate_random_password()
            hashed_password = hash_password(plain_password)

            new_member = Member(
                member_id=new_member_id,
                name=newuser.name,
                password=hashed_password,
                role=newuser.role,
            )

            commit_and_refresh(db, new_member)

            new_member_response = MemberResponse.from_orm(new_member)

            logger.info(f"New member {newuser.name} added successfully.")

            return {
                "message": "Member added successfully",
                "new_member": new_member_response.dict(),
                "plain_password": plain_password,
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add member {newuser.name,}: {str(e)}")
            raise

    def add_books(self, newbook: NewBooks, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        try:
            existing_book = self.admin_repo.get_existing_book(db, newbook)
            if existing_book:
                existing_book.stock += newbook.stock
                existing_book.available = existing_book.stock > 0
                db.commit()

                existing_book_response = BookResponseModel.from_orm(existing_book)

                return {
                    "message": "Book updated successfully",
                    "new_book": existing_book_response.dict(),
                }

            new_book = Book(
                title=newbook.title,
                author=newbook.author,
                stock=newbook.stock,
                available=True,
                id=str(uuid.uuid4()),
            )

            commit_and_refresh(db, new_book)

            new_book_response = BookResponseModel.from_orm(new_book)

            logger.info(f"New book {newbook.title} added successfully.")

            return {
                "message": "Book added successfully",
                "new_book": new_book_response.dict(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add book {newbook.title}: {str(e)}")
            raise

    def view_available_books(self, title: str, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        try:
            if title:
                books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
            else:
                books = db.query(Book).all()

            if not books:
                return {"message": "No books found with that title"}

            book_data = []
            for book in books:
                availability_record = (
                    db.query(BookAvailability)
                    .filter(BookAvailability.book_id == book.id)
                    .first()
                )
                is_available = book.stock > 0
                if availability_record:
                    availability_record.available = is_available
                else:
                    new_availability = BookAvailability(
                        book_id=book.id, title=book.title, available=is_available
                    )
                    db.add(new_availability)

                if is_available:
                    book_data.append(
                        {
                            "title": book.title,
                            "author": book.author,
                            "available": is_available,
                        }
                    )

            db.commit()

            return {"message": "Books available", "books": book_data}
        except Exception as e:
            db.rollback()
            logger.error(f"Error while viewing available books: {str(e)}")
            raise

    def view_all_members(self, db: Session, current_user: dict) -> MembersListResponse:
        self._check_admin(current_user)

        members = self.admin_repo.get_all_members(db)
        if not members:
            return {"message": "No members found"}

        member_data = [
            {"name": member.name, "role": member.role, "member_id": member.member_id}
            for member in members
        ]

        return MembersListResponse(filtered_members=member_data)

    def view_member_by_id(
        self, member_id: str, db: Session, current_user: dict
    ) -> MemberResponse:
        self._check_admin(current_user)

        member = self.admin_repo.get_member_by_id(db, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        return {"name": member.name, "role": member.role, "member_id": member.member_id}

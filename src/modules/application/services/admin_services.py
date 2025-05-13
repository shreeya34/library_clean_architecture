from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from modules.domain.services.admin_services import AdminServiceInterface
from modules.interfaces.request.admin_request import (
    CreateModel,
    AdminLogins,
    NewMember,
    NewBooks,
)
from modules.interfaces.response.admin_response import (
    AdminLoginResponse,
    AdminResponseModel,
    BookAddResponse,
    BookAvailabilityResponse,
    BookResponseModel,
    BookViewResponse,
    MemberAddResponse,
    MemberResponse,
    MembersListResponse,
)
from modules.infrastructure.database.models.admin import (
    Admin,
    AdminLogin,
    Book,
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
from modules.shared.decorators.db_exception_handler import db_exception_handler
from dataclasses import asdict



logger = get_logger()


class AdminService(AdminServiceInterface):

    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def _check_admin(self, current_user: dict):
        if not current_user.get("is_admin"):
            raise AdminAccessDeniedError()

    @db_exception_handler("add new admin")
    def create_admin(self, admin: CreateModel, db: Session) -> dict:
        if self.admin_repo.get_admin_by_username(db, admin.username):
            logger.warning(f"Admin {admin.username} already exists.")
            raise AdminAlreadyExistsError(admin.username)

        new_admin = Admin(
            admin_id=str(uuid.uuid4()),
            username=admin.username,
            password=hash_password(admin.password),
            role="admin",
        )
        commit_and_refresh(db, new_admin)

        new_member = Member(
            member_id=str(uuid.uuid4()), 
            name=admin.username,
            password=hash_password(admin.password),
            role="admin",
        )

        commit_and_refresh(db, new_member)
        logger.info(f"Created new admin {admin.username}")

        admin_response = AdminResponseModel(
        admin_id=new_admin.admin_id,
        username=new_admin.username
    )
    
        return asdict (admin_response)

    @db_exception_handler("login admin")
    def login_admin(self, admin_data: AdminLogins, db: Session) -> dict:
        admin = self.admin_repo.get_admin_by_username(db, admin_data.username)

        if not admin:
            logger.warning(f"Admin {admin_data.username} does not exist.")
            raise AdminAccessDeniedError(admin_data.username)

        if not check_password(admin_data.password, admin.password):
            logger.warning(f"Invalid password for admin {admin_data.username}")
            raise InvalidAdminCredentialsError(admin_data.username)

        token_response = signJWT(admin.username, admin.admin_id, is_admin=True)
        access_token = token_response.get('access_token') 

        commit_and_refresh(
            db,
            AdminLogin(
                username=admin_data.username,
                status="success",
                login_time=datetime.utcnow(),
                password=admin_data.password,
                member_id=admin.admin_id,
            ),
        )

        logger.info(f"Admin {admin_data.username} logged in successfully.")
        return asdict (AdminLoginResponse(
            message="Login successful",
            token=access_token, 
            admin_id=admin.admin_id
        ))

    @db_exception_handler("add new member")
    def add_member(self, newuser: NewMember, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)

        if self.admin_repo.get_member_by_name(db, newuser.name):
            logger.warning(f"Member {newuser.name} already exists.")
            raise MemberAlreadyExistsError(newuser.name)

        plain_password = generate_random_password()
        new_member = Member(
            member_id=str(uuid.uuid4()),
            name=newuser.name,
            password=hash_password(plain_password),
            role=newuser.role,
        )

        commit_and_refresh(db, new_member)

        logger.info(f"New member {newuser.name} added successfully.")
        return  (MemberAddResponse(
            message="Member added successfully",
            new_member=MemberResponse.from_orm(new_member),
            plain_password=plain_password,
        )).dict()

    @db_exception_handler("add new book")
    def add_books(self, newbook: NewBooks, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)

        book = self.admin_repo.get_existing_book(db, newbook)
        if book:
            book.stock += newbook.stock
            book.available = book.stock > 0
            self.admin_repo.commit(db)
            message = "Book updated successfully"
        else:
            book = Book(
                id=str(uuid.uuid4()),
                title=newbook.title,
                author=newbook.author,
                stock=newbook.stock,
                available=True,
            )
            commit_and_refresh(db, book)
            message = "Book added successfully"
            logger.info(f"New book {newbook.title} added successfully.")

        return (BookAddResponse(
            message=message,
            new_book=BookResponseModel.from_orm(book),
        )).dict()
        
    @db_exception_handler("view books")
    def view_available_books(self, title: str, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)

        books = (
            self.admin_repo.get_books_by_title(db, title)
            if title
            else self.admin_repo.get_all_books(db)
        )

        if not books:
            return BookViewResponse(message="No books found with that title", books=[]).dict()

        book_data = []
        for book in books:
            is_available = book.stock > 0
            self.admin_repo.upsert_availability(db, book.id, book.title, is_available)

            if is_available:
                book_data.append(
                    BookAvailabilityResponse(
                        title=book.title,
                        author=book.author,
                        available=is_available,
                    )
                )

        self.admin_repo.commit(db)

       
        return  BookViewResponse(
            message="Books available",
            books=book_data,
        ).dict()

    def view_all_members(self, db: Session, current_user: dict) -> MembersListResponse:
        self._check_admin(current_user)

        members = self.admin_repo.get_all_members(db)
        if not members:
            return {"message": "No members found"}

        member_data = [
            {"name": member.name, "role": member.role, "member_id": member.member_id}
            for member in members
        ]

        return MembersListResponse(filtered_members=member_data).dict()

    def view_member_by_id(
        self, member_id: str, db: Session, current_user: dict
    ) -> MemberResponse:
        self._check_admin(current_user)

        member = self.admin_repo.get_member_by_id(db, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        return  (MemberResponse(name=member.name, role=member.role, member_id=member.member_id)).dict()

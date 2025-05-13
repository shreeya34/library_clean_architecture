from sqlalchemy.orm import Session
from modules.domain.services.admin_services import AdminServiceInterface
from modules.application.use_cases.admin.add_books import AddBooksUseCase
from modules.application.use_cases.admin.add_member import AddMemberUseCase
from modules.application.use_cases.admin.create_admin import CreateAdminUseCase
from modules.application.use_cases.admin.login_admin import LoginAdminUseCase
from modules.application.use_cases.admin.view_books import ViewBooksUseCase
from modules.application.use_cases.admin.view_member_by_id import ViewMemberByIdUseCase
from modules.application.use_cases.admin.view_members import ViewMembersUseCase
from modules.interfaces.request.admin_request import (
    CreateModel,
    AdminLogins,
    NewMember,
    NewBooks,
)
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.domain.exceptions.admin.exception import (
    AdminAccessDeniedError,
)
from modules.shared.decorators.db_exception_handler import db_exception_handler


class AdminService(AdminServiceInterface):

    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def _check_admin(self, current_user: dict):
        if not current_user.get("is_admin"):
            raise AdminAccessDeniedError()

    @db_exception_handler("add new admin")
    def create_admin(self, admin: CreateModel, db: Session) -> dict:
        return CreateAdminUseCase(self.admin_repo).execute(db, admin)


    @db_exception_handler("login admin")
    def login_admin(self, admin_data: AdminLogins, db: Session) -> dict:
        return LoginAdminUseCase(self.admin_repo).execute(db, admin_data)

    @db_exception_handler("add new member")
    def add_member(self, newuser: NewMember, db: Session, current_user: dict) -> dict:
        
        self._check_admin(current_user)
        use_case = AddMemberUseCase(self.admin_repo)
        response = use_case.execute(db, newuser)
        return response.dict()

    @db_exception_handler("add books")
    def add_books(self, newbook: NewBooks, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        return AddBooksUseCase(self.admin_repo).execute(db, newbook)

    @db_exception_handler("view books")
    def view_available_books(self, title: str, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        return ViewBooksUseCase(self.admin_repo).execute(db, title)
    
    
    @db_exception_handler("view members")
    def view_all_members(self, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        return ViewMembersUseCase(self.admin_repo).execute(db)
    
    @db_exception_handler("view member by ID")
    def view_member_by_id(self, member_id: str, db: Session, current_user: dict) -> dict:
        self._check_admin(current_user)
        return ViewMemberByIdUseCase(self.admin_repo).execute(db, member_id)

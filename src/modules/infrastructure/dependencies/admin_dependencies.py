from fastapi import Depends
from modules.infrastructure.repositories.admin.admin_repositories_impl import (
    AdminRepository,
)
from modules.application.services.admin_services import AdminService


def get_admin_service() -> AdminService:
    admin_repo = AdminRepository()  
    return AdminService(admin_repo)

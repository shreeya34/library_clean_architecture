from fastapi import Depends
from modules.infrastructure.repositories.admin.admin_repositories_impl import (
    AdminRepository,
)
from modules.infrastructure.services.admin_services import AdminService


def get_admin_service(admin_repo: AdminRepository = Depends(AdminRepository)):
    return AdminService(admin_repo)

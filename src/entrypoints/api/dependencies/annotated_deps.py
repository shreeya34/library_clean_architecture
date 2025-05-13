
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from modules.infrastructure.database.dependency import get_db_from_app
from modules.infrastructure.security.auth_handler import get_current_user
from modules.infrastructure.dependencies.admin_dependencies import get_admin_service
from modules.application.services.admin_services import AdminService


DBSessionDep = Annotated[Session, Depends(get_db_from_app)]
CurrentUserDep = Annotated[dict, Depends(get_current_user)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]



from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from modules.infrastructure.database.dependency import get_db_from_app
from modules.infrastructure.security.auth_berarer import JWTBearer
from modules.infrastructure.security.auth_handler import get_current_user
from modules.application.models.request.admin_request import (
    CreateModel,
    AdminLogins,
    NewMember,
    NewBooks,
)
from entrypoints.api.utils.response_utils import json_response
from modules.infrastructure.services.admin_services import AdminService
from modules.application.models.response.admin_response import (
    MemberResponse,
    MembersListResponse,
)
from fastapi.encoders import jsonable_encoder

router = APIRouter()
admin_service = AdminService()


@router.post("/")
def create_admin(admin: CreateModel, db: Session = Depends(get_db_from_app)):
    try:
        result = admin_service.create_admin(admin, db)
        return json_response(status_code=201, content=result)
    except Exception as e:
        return json_response(status_code=400, content={"error": str(e)})


@router.post("/login")
def login_admin(admin_data: AdminLogins, db: Session = Depends(get_db_from_app)):
    try:
        login_result = admin_service.login_admin(admin_data, db)
        return JSONResponse(content=login_result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@router.post("/add_member", dependencies=[Depends(JWTBearer())])
def add_member(
    request: Request,
    newuser: NewMember,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    try:
        result = admin_service.add_member(newuser, db, user)
        return json_response(status_code=201, content=result)
    except Exception as e:
        return json_response(status_code=400, content={"error": str(e)})


@router.post("/add_books", dependencies=[Depends(JWTBearer())])
def add_books(
    request: Request,
    newbook: NewBooks,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    try:
        result = admin_service.add_books(newbook, db, user)
        return json_response(status_code=201, content=jsonable_encoder(result))
    except Exception as e:
        return json_response(status_code=400, content={"error": str(e)})


@router.get("/view_available_books", dependencies=[Depends(JWTBearer())])
def view_books(
    request: Request,
    title: str = Query(None),
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    try:
        result = admin_service.view_available_books(title, db, user)
        return json_response(status_code=200, content=result)
    except Exception as e:
        return json_response(status_code=400, content={"error": str(e)})


@router.get(
    "/view_members",
    response_model=MembersListResponse,
    dependencies=[Depends(JWTBearer())],
)
def view_members(
    request: Request,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    try:
        result = admin_service.view_all_members(db, user)
        return json_response(status_code=200, content=result.dict())
    except Exception as e:
        return json_response(status_code=400, content={"error": str(e)})


@router.get(
    "/view_members/{member_id}",
    response_model=MemberResponse,
    dependencies=[Depends(JWTBearer())],
)
def view_members_by_id(
    member_id: str,
    request: Request,
    db: Session = Depends(get_db_from_app),
    user: dict = Depends(get_current_user),
):
    try:
        result = admin_service.view_member_by_id(member_id, db, user)
        return json_response(status_code=200, content=result)
    except Exception as e:
        return json_response(status_code=400, content={"error": str(e)})

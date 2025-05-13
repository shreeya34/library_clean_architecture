from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request, logger
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from entrypoints.api.dependencies.annotated_deps import (
    AdminServiceDep,
    CurrentUserDep,
    DBSessionDep,
)
from modules.domain.exceptions.admin.exception import (
    AdminAlreadyExistsError,
    InvalidAdminCredentialsError,
    MemberAlreadyExistsError,
)
from modules.domain.exceptions.member.exception import AdminAccessDeniedError
from modules.infrastructure.security.auth_berarer import JWTBearer
from modules.interfaces.request.admin_request import (
    CreateModel,
    AdminLogins,
    NewMember,
    NewBooks,
)
from entrypoints.api.utils.response_utils import json_response
from modules.application.services.admin_services import AdminService
from modules.interfaces.response.admin_response import (
    MemberResponse,
    MembersListResponse,
)
from fastapi.encoders import jsonable_encoder

router = APIRouter()


@router.post("/")
def create_admin(
    admin: CreateModel,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
):
    try:
        result = admin_service.create_admin(admin, db)
        return JSONResponse(status_code=201, content=result)
    except AdminAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login_admin(
    admin_data: AdminLogins,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
):
    try:
        login_result = admin_service.login_admin(admin_data, db)
        return JSONResponse(status_code=201, content=login_result)
    except InvalidAdminCredentialsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AdminAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/add_member", dependencies=[Depends(JWTBearer())])
def add_member(
    request: Request,
    newuser: NewMember,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
    user: CurrentUserDep,
):
    try:

        result = admin_service.add_member(newuser, db, user)
        return json_response(status_code=201, content=result)
    except MemberAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AdminAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/add_books", dependencies=[Depends(JWTBearer())])
def add_books(
    request: Request,
    newbook: NewBooks,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
    user: CurrentUserDep,
):
    try:
        result = admin_service.add_books(newbook, db, user)
        return json_response(status_code=201, content=jsonable_encoder(result))
    except AdminAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/view_available_books", dependencies=[Depends(JWTBearer())])
def view_books(
    request: Request,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
    user: CurrentUserDep,
    title: str = Query(None),
):
    try:
        result = admin_service.view_available_books(title, db, user)
        return json_response(status_code=200, content=result)
    except AdminAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/view_members",
    response_model=MembersListResponse,
    dependencies=[Depends(JWTBearer())],
)
def view_members(
    request: Request,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
    user: CurrentUserDep,
):
    try:
        result = admin_service.view_all_members(db, user)
        return json_response(status_code=200, content=result.dict())
    except AdminAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/view_members/{member_id}",
    response_model=MemberResponse,
    dependencies=[Depends(JWTBearer())],
)
def view_members_by_id(
    member_id: str,
    request: Request,
    db: DBSessionDep,
    admin_service: AdminServiceDep,
    user: CurrentUserDep,
):
    try:
        result = admin_service.view_member_by_id(member_id, db, user)
        return json_response(status_code=200, content=result)
    except AdminAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

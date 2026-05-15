from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.params import Depends

from api.core.deps import get_user_service
from api.core.jwt import get_current_user
from api.database import User
from api.schemas import UserGet, UserPatch, UserPost
from api.services import UserService

router_user = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router_user.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router_user.get("/get", response_model=list[UserGet])
async def get_all_users(service: Annotated[UserService, Depends(get_user_service)]):
    users = await service.get_all_users()
    return users


@router_user.get("/get/{user_id}", response_model=UserGet)
async def get_user_by_id(
    service: Annotated[UserService, Depends(get_user_service)],
    user_id: int,
):
    user = await service.get_user_by_id(user_id=user_id)
    return user


@router_user.post("/create", response_model=UserPost)
async def create_user(
    service: Annotated[UserService, Depends(get_user_service)],
    user_data: UserPost,
):
    user = await service.create_user(user_data=user_data)
    return user


@router_user.patch("/{user_id}", response_model=UserPatch)
async def update_user(
    service: Annotated[UserService, Depends(get_user_service)],
    user_id: int,
    user_data: UserPatch,
):
    user = await service.update_user(user_id=user_id, user_data=user_data)
    return user


@router_user.delete("/{user_id}", status_code=204)
async def delete_user(
    service: Annotated[UserService, Depends(get_user_service)],
    user_id: int,
):
    await service.delete_user(user_id=user_id)
    return Response(status_code=204)

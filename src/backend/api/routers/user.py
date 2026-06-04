from typing import Annotated

from fastapi import APIRouter, Cookie, Response
from fastapi.exceptions import HTTPException
from fastapi.params import Depends

from ...services.schemas.user import UserGet, UserPatch, UserPost
from ...services.user import UserService
from ..core.deps import get_user_service

router_user = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router_user.get("/me")
async def read_users_me(
    service: Annotated[UserService, Depends(get_user_service)],
    access_token: str | None = Cookie(default=None),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No token")

    user = await service.get_current_user(token=access_token)
    return user


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

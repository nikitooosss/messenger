from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from backend.services.auth import AuthService
from backend.services.jwt import JWTService
from backend.services.schemas import TokenData
from backend.services.schemas.user import UserPublic

from ..core.deps import get_auth_service, get_jwt_service
from ..schemas.auth import UserRegister

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router_auth.post("/register", response_model=UserPublic)
async def register_user(
    service: Annotated[AuthService, Depends(get_auth_service)],
    user_data: UserRegister,
):
    user = await service.register_user(user_data=user_data)
    if user is None:
        raise HTTPException(
            status_code=409, detail="A user with that name already exists"
        )

    return user


@router_auth.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> JSONResponse:
    user = await auth_service.authenticate_user(
        uniq_name=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = TokenData(id=user.id, uniq_name=user.uniq_name)
    token = await jwt_service.get_access_token(data=data)

    response = JSONResponse(content={"status": status.HTTP_200_OK})

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
    )

    return response

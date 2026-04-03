from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.auth.service import (
    authenticate_user,
    count_users,
    create_user,
    generate_token_response,
)
from app.core.security import get_current_active_user, get_current_user_optional


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.senha)
    return generate_token_response(user)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(get_current_user_optional),
) -> UserResponse:
    if count_users(db) == 0:
        if payload.perfil != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The first registered user must be an admin.",
            )
        return create_user(db, payload)

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
    return create_user(db, payload)


@router.get("/me", response_model=UserResponse)
def read_me(current_user=Depends(get_current_active_user)) -> UserResponse:
    return current_user

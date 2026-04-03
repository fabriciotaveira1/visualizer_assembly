from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    exp: int


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload.model_validate(payload)
    except (InvalidTokenError, ValueError) as exc:
        raise credentials_exception from exc

    return token_data


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    from app.auth.service import get_user_by_id

    token_data = decode_access_token(token)
    user = get_user_by_id(db, token_data.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_optional(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Depends(oauth2_optional_scheme)],
):
    if token is None:
        return None

    token_data = decode_access_token(token)

    from app.auth.service import get_user_by_id

    user = get_user_by_id(db, token_data.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )
    return current_user


def require_role(role: str) -> Callable:
    def role_dependency(current_user=Depends(get_current_active_user)):
        if current_user.perfil != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return role_dependency


def require_roles(*roles: str) -> Callable:
    allowed_roles = set(roles)

    def roles_dependency(current_user=Depends(get_current_active_user)):
        if current_user.perfil not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return roles_dependency

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.permissions import ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER, has_role_level
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.repositories.user_repository import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credentials_error
    user = get_user(db, user_id)
    if not user or not user.is_active:
        raise credentials_error
    return user


def _require_role(user: User, minimum_role: str) -> User:
    if not has_role_level(user.role, minimum_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    return _require_role(current_user, ROLE_ADMIN)


def require_operator_or_admin(current_user: User = Depends(get_current_user)) -> User:
    return _require_role(current_user, ROLE_OPERATOR)


def require_viewer_or_above(current_user: User = Depends(get_current_user)) -> User:
    return _require_role(current_user, ROLE_VIEWER)

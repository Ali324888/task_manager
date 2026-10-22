import aiosqlite
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError

from app.dependencies.database import get_db
from app.core.security import decode_token
from app.schemas.user import UserPublic

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: aiosqlite.Connection = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_token(token)
        if payload.get("type") != 'access':
            raise credentials_exception

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit():
            raise credentials_exception

        user_id = int(subject)

    except (InvalidTokenError, ValueError) as exc:
        logger.warning("JWT validation failed: %s", type(exc).__name__)
        raise credentials_exception from exc

    async with db.execute("Select id, username, email, created_at From users Where id=?", (user_id,)) as cursor:
        row = await cursor.fetchone()

    if row is None:
        raise credentials_exception

    return UserPublic(**dict(row))

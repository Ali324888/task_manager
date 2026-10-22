from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from app.core.config import settings
import jwt


password_hash = PasswordHash.recommended()
ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_token(subject: str, token_type: str, expire_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now+expire_delta
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int) -> str:
    return create_token(
        str(user_id),
        "access",
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(user_id: int) -> str:
    return create_token(
        str(user_id),
        "refresh",
        expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "iat", "type"]},
        )
    except jwt.exceptions.DecodeError as exc:
        print("JWT decode error:", str(exc))
        raise

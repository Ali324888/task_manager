import aiosqlite

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from app.dependencies.database import get_db
from app.schemas.auth import TokenResponse, AccessTokenResponse, RefreshRequest
from app.services.auth_service import authenticate_user
from app.core.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: aiosqlite.Connection = Depends(get_db)
):
    # 1. Authenticate user
    user = await authenticate_user(db, credentials.username, credentials.password)
    # 2. If invalid, raise HTTPException(status_code=401, ...)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or password",
            headers={"WWW-Authenticate": "Bearer"},
            )
    # 3. Create access token
    access_token = create_access_token(user["id"]) 
    # 4. Create refresh token
    refresh_token = create_refresh_token(user["id"]) 
    # 5. Return TokenResponse-compatible dictionary
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    request: RefreshRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != 'refresh':
            raise credentials_exception

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit():
            raise credentials_exception

        user_id = int(subject)

    except (InvalidTokenError, ValueError) as exc:
        raise credentials_exception from exc

    async with db.execute("Select id From users Where id=?", (user_id,)) as cursor:
        user = await cursor.fetchone()

    if user is None:
        raise credentials_exception

    new_access_token = create_access_token(user_id)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
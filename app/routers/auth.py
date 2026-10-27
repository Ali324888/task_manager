import aiosqlite
from datetime import datetime, timezone

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
    refresh_token, jti, expires_at = create_refresh_token(user["id"]) 

    try:
        await db.execute(
            """
            Insert Into refresh_tokens (jti,user_id,expires_at) Values (?,?,?,)
            """,
            (jti, user['id'], expires_at,)
        )
        await db.commit()

    except aiosqlite.IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )
    # 5. Return TokenResponse-compatible dictionary
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=TokenResponse)
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

    except (InvalidTokenError, ValueError) as exc:
            raise credentials_exception from exc
    
    if payload.get("type") != 'refresh':
        raise credentials_exception

    subject = payload.get("sub")
    jti = payload.get("jti")

    if not isinstance(subject, str) or not subject.isdigit() or not isinstance(jti,str) or not jti:
        raise credentials_exception

    user_id = int(subject)
    now = int(datetime.now(timezone.utc).timestamp())

    # async with db.execute("Select id From users Where id=?", (user_id,)) as cursor:
    #     user = await cursor.fetchone()

    # if user is None:
    #     raise credentials_exception

    new_access_token = create_access_token(user_id)
    new_refresh_token, new_jti, new_expires_at = create_refresh_token(user_id)

    try:
        await db.execute("BEGIN IMMEDIATE")

        cursor = await db.execute(
            """
            Update refresh_tokens Set revoked_at=?, replaced_by=?
            Where jti=? And user_id=? And revoked_at is NULL And expires_at > ?
            """,
            (now, new_jti, jti, user_id, now)
        )

        if cursor.rowcount != 1:
            await db.rollback()
            raise credentials_exception

        await cursor.close()

        await db.execute(
                    """
                    Insert Into refresh_tokens (jti,user_id,expires_at) Values (?,?,?,)
                    """,
                    (new_jti, user_id, new_expires_at)
                )
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not rotate refresh token",
        )


    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }



@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_access_token(
    request: RefreshRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expire refresh tokens",
        )
    
    try:
        payload = decode_token(request.refresh_token)

    except (InvalidTokenError, ValueError) as exc:
            raise credentials_exception from exc
    
    if payload.get("type") != 'refresh':
        raise credentials_exception

    subject = payload.get("sub")
    jti = payload.get("jti")

    if not isinstance(subject, str) or not subject.isdigit() or not isinstance(jti,str) or not jti:
        raise credentials_exception

    user_id = int(subject)
    now = int(datetime.now(timezone.utc).timestamp())

    async with db.execute(
        """
        Update refresh_tokens Set revoked_at=?
        Where jti=? And user_id=? And revoked_at is NULL
        """,
        (now, jti, user_id)
    ) as cursor:
        revoked = await cursor.rowcount

    await db.commit()

    if revoked != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is already revoked or unknown",
        )
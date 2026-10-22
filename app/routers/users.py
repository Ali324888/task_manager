import sqlite3
import aiosqlite

from fastapi import APIRouter,Depends, HTTPException, status
from app.schemas.user import UserPublic, UserCreate
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.services.user_service import create_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        return await create_user(db, user_data)

    except sqlite3.IntegrityError as exc:
        await db.rollback()
        message = str(exc).lower()
        print(message)
        if "users.username" in message:
            detail = "Username already exist"
        elif "users.email" in  message:
            detail = "Email already exist"
        else:
            detail = "User could not be created due to a database constraint"

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


@router.get("/me", response_model=UserPublic)
async def read_current_user(current_user: UserPublic = Depends(get_current_user)):
    return current_user
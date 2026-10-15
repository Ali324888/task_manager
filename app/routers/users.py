from fastapi import APIRouter
from app.schemas.user import UserPublic, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
async def get_users(user_data: UserCreate):
    return {
        "users": user_data
    }
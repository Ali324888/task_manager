from fastapi import APIRouter, Depends
import aiosqlite
from app.db.database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/")
async def list_tasks():
    return {
        "message": "Task router is working",
        "tasks": []
    }

@router.get("/db-check")
async def check_db(db: aiosqlite.Connection = Depends(get_db)):
    return {
        "database": "connected"
    }

@router.get("/{task_id}")
async def get_task_by_id(task_id: int):
    return{
        "task_id": task_id
    }


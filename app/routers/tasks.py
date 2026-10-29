import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.task import TaskCreate, TaskPublic, TaskUpdate
from app.schemas.user import UserPublic
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskCreate,
                      db: aiosqlite.Connection = Depends(get_db),
                      current_user: UserPublic = Depends(get_current_user),
                      ):
    return await task_service.create_task(db=db, 
                                          user_id=current_user.id, 
                                          title=request.title, 
                                          description=request.description)

@router.get("/", response_model=list[TaskPublic])
async def list_tasks(db: aiosqlite.Connection = Depends(get_db),
                      current_user: UserPublic = Depends(get_current_user)):
    return await task_service.list_tasks(db=db, user_id=current_user.id)

@router.get("/db-check")
async def check_db(db: aiosqlite.Connection = Depends(get_db)):
    return {
        "database": "connected"
    }

@router.get("/{task_id}", response_model=TaskPublic)
async def get_task_by_id(task_id: int,
                         db: aiosqlite.Connection = Depends(get_db),
                         current_user: UserPublic = Depends(get_current_user)
                         ):
    task = await task_service.get_task(db=db, user_id=current_user.id, task_id=task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task



@router.patch("/{task_id}", response_model=TaskPublic)
async def update_task_by_id(
    task_id: int,
    request: TaskUpdate,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    changes = request.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one field to update"
        )

    if "title" in changes and changes["title"] is None:
        raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="title cannot be null"
                )

    if "completed" in changes and changes["completed"] is None:
            raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="completed cannot be null"
                    )

    task = await task_service.update_task(
        db=db, 
        user_id=current_user.id, 
        task_id=task_id,
        changes=changes
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task not found"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(task_id: int,
                         db: aiosqlite.Connection = Depends(get_db),
                         current_user: UserPublic = Depends(get_current_user)
                         ):
    deleted = await task_service.delete_task(db=db, user_id=current_user.id, task_id=task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return None
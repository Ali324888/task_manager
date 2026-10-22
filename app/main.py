from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import health,tasks,users, dashboard, auth
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
     title="Task Management API",
    description="A production-style async Task Management API",
    version="1.0.0",
    lifespan=lifespan)

app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to task management API"
    }
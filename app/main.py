from fastapi import FastAPI,HTTPException, Depends
from app.routers import health,tasks,users, dashboard

app = FastAPI(
     title="Task Management API",
    description="A production-style async Task Management API",
    version="1.0.0",)

app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to task management API"
    }
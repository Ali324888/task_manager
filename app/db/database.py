import aiosqlite

DATABASE_URL = "task_manager.db"

async def get_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("PRAGMA foreign_key=ON")
        db.row_factory = aiosqlite.Row
        yield db

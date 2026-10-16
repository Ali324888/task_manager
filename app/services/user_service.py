import aiosqlite

from app.core.security import hash_password
from app.schemas.user import UserCreate


async def create_user(db: aiosqlite.Connection, user_data: UserCreate) -> dict:
    hashed_password = hash_password(user_data.password)
    cursor = await db.execute("""INSERT INTO users (username,email,hashed_password) 
                            Values (?,?,?)""",
                            (
                                user_data.username,
                                user_data.email,
                                hashed_password
                            ))
    user_id = cursor.lastrowid
    await cursor.close()
    await db.commit()

    async with db.execute("""
    SELECT id, username, email, created_at from users
    Where id = ?            
    """, (user_id,)) as cursor:
        row = await cursor.fetchone()

    if row is None:
        raise RuntimeError("Created user could not be retrieved")

    return dict(row)

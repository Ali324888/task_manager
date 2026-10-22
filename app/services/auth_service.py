import aiosqlite
from app.core.security import verify_password

async def authenticate_user(
        db: aiosqlite.Connection,
        username: str,
        password: str
) -> dict | None:
    async with db.execute(
        """
        SELECT id, username, email, hashed_password, created_at From users Where username=? OR email=?
        """,
        (username, username,)
    ) as cursor:
        user = await cursor.fetchone()

    if user is None:
        return None

    user = dict(user)

    if not verify_password(password, user["hashed_password"]):
        return None

    return user
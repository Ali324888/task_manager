import aiosqlite

def serialize_task(row: aiosqlite.Row) -> dict:
    task = dict(row)
    task['completed'] = bool(task['completed'])
    return task

async def create_task(db: aiosqlite.Connection,user_id: int,title: str,description: str | None) -> dict:
    async with db.execute(
        """
        INSERT INTO tasks (user_id,title,description)
        VALUES (?,?,?)
        """,
        (user_id, title, description)
    ) as cursor:
        task_id = cursor.lastrowid

    await db.commit()

    async with db.execute(
        """
        SELECT id, user_id, title, description, completed, created_at
        FROM tasks WHERE id=? AND user_id=?
        """,
        (task_id, user_id)
    ) as cursor:
        row = await cursor.fetchone()

    return serialize_task(row)

async def list_tasks(db: aiosqlite.Connection, user_id: int) -> list[dict]:
    async with db.execute(
        """
        SELECT id, user_id, title, description, completed, created_at
        FROM tasks WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    ) as cursor:
        rows = await cursor.fetchall()

    return [serialize_task(row) for row in rows]

async def get_task(db: aiosqlite.Connection, user_id: int, task_id: int) -> dict | None:
    async with db.execute(
            """
            SELECT id, user_id, title, description, completed, created_at
            FROM tasks WHERE id=? AND user_id=?
            """,
            (task_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
    
    return serialize_task(row) if row is not None else None

async def update_task(db: aiosqlite.Connection, user_id: int, task_id: int, changes: dict) -> dict | None:
    allowed_fields = {"title", "description", "completed"}

    changes = {key : value for key, value in changes.items() if key in allowed_fields}

    if not changes:
        return await get_task(db, user_id, task_id)

    if "completed" in changes:
        changes["completed"] = int(changes["completed"])

    set_clause = ", ".join(f"{column} = ?" for column in changes)
    values = list(changes.values()) + [task_id, user_id]

    async with db.execute(
        f"""
        UPDATE tasks
        SET {set_clause} WHERE
        id =? AND user_id=? 
        """,
        values
    ) as cursor:
        updated = cursor.rowcount

    await db.commit()

    if updated != 1:
        return None

    return await get_task(db, user_id, task_id)


async def delete_task(db: aiosqlite.Connection, user_id: int, task_id: int) -> bool:
    async with db.execute(
        """
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, user_id)
    ) as cursor:
        deleted = cursor.rowcount
    await db.commit()

    return deleted == 1
     


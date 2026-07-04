import aiosqlite
from config import DATABASE, START_BALANCE


async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DATABASE) as db:
        user = await db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        if not await user.fetchone():
            await db.execute(
                "INSERT INTO users (user_id, username, full_name, balance) VALUES (?, ?, ?, ?)",
                (user_id, username, full_name, START_BALANCE)
            )
            await db.commit()


async def is_banned(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute("SELECT banned FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row and row[0] == 1


async def get_balance(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0


async def maintenance_enabled():
    return False

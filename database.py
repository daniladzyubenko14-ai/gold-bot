import aiosqlite
import time

from config import DATABASE, START_BALANCE


# =========================
# INIT DB
# =========================
async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance REAL DEFAULT 0.00,
            banned INTEGER DEFAULT 0,
            last_bonus REAL DEFAULT 0
        )
        """)
        await db.commit()


# =========================
# ADD USER
# =========================
async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (user_id,)
        )
        if not await cur.fetchone():
            await db.execute(
                """
                INSERT INTO users (user_id, username, full_name, balance, last_bonus)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, username, full_name, float(START_BALANCE), 0.0)
            )
            await db.commit()


# =========================
# BALANCE
# =========================
async def get_balance(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            return 0.00

        return round(float(row[0]), 2)


async def add_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id=?",
            (float(amount), user_id)
        )
        await db.commit()


# =========================
# BONUS SYSTEM
# =========================
BONUS_AMOUNT = 0.5
BONUS_COOLDOWN = 12 * 60 * 60  # 12 часов


async def can_take_bonus(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute(
            "SELECT last_bonus FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            return True, 0

        last_bonus = float(row[0] or 0)
        now = time.time()

        remaining = BONUS_COOLDOWN - (now - last_bonus)

        if remaining <= 0:
            return True, 0

        return False, int(remaining)


async def give_bonus(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            UPDATE users
            SET balance = balance + ?,
                last_bonus = ?
            WHERE user_id=?
            """,
            (BONUS_AMOUNT, time.time(), user_id)
        )
        await db.commit()

import asyncpg
import os
import time

from config import START_BALANCE

pool = None


# =========================
# INIT DB
# =========================
async def init_db():
    global pool

    DATABASE_URL = os.getenv("DATABASE_URL")
    print("DATABASE_URL =", DATABASE_URL)

    if not DATABASE_URL:
        raise RuntimeError("❌ DATABASE_URL не найден!")

    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:

        # USERS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance DOUBLE PRECISION DEFAULT 0,
            banned INT DEFAULT 0,
            last_bonus DOUBLE PRECISION DEFAULT 0
        )
        """)

        # PROMOCODES
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            reward DOUBLE PRECISION NOT NULL,
            max_uses INTEGER DEFAULT 1,
            uses INTEGER DEFAULT 0
        )
        """)

        # ACTIVATIONS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS promo_activations (
            user_id BIGINT,
            code TEXT,
            PRIMARY KEY (user_id, code)
        )
        """)


# =========================
# ADD USER
# =========================
async def add_user(user_id, username, full_name):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users(user_id, username, full_name, balance, last_bonus)
        VALUES($1,$2,$3,$4,$5)
        ON CONFLICT (user_id) DO NOTHING
        """,
        user_id,
        username,
        full_name,
        float(START_BALANCE),
        0.0
        )


# =========================
# BALANCE
# =========================
async def get_balance(user_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT balance FROM users WHERE user_id=$1",
            user_id
        )
        return float(row["balance"]) if row else 0.0


# =========================
# BONUS
# =========================
BONUS_AMOUNT = 0.5
BONUS_COOLDOWN = 12 * 60 * 60


async def can_take_bonus(user_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT last_bonus FROM users WHERE user_id=$1",
            user_id
        )

        if not row:
            return False, 0

        last = float(row["last_bonus"])
        now = time.time()

        remaining = BONUS_COOLDOWN - (now - last)

        if remaining <= 0:
            return True, 0

        return False, int(remaining)


async def give_bonus(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE users
        SET balance = balance + $1,
            last_bonus = $2
        WHERE user

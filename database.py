import asyncpg
import time
import os

from config import START_BALANCE

pool = None

BONUS_AMOUNT = 0.5
BONUS_COOLDOWN = 12 * 60 * 60


# =========================
# INIT DB
# =========================
async def init_db():
    global pool

    DATABASE_URL = os.getenv("DATABASE_URL")
    print("DATABASE_URL =", DATABASE_URL)

    if not DATABASE_URL:
        raise RuntimeError("❌ DATABASE_URL не найден! Проверь Variables Railway.")

    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:

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

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            reward DOUBLE PRECISION NOT NULL,
            uses_left INTEGER NOT NULL
        )
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses (
            user_id BIGINT NOT NULL,
            code TEXT NOT NULL,
            PRIMARY KEY (user_id, code)
        )
        """)


# =========================
# USERS
# =========================
async def add_user(user_id, username, full_name):

    async with pool.acquire() as conn:

        await conn.execute("""
        INSERT INTO users (
            user_id,
            username,
            full_name,
            balance,
            last_bonus
        )
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (user_id) DO NOTHING
        """,
        user_id,
        username,
        full_name,
        float(START_BALANCE),
        0.0)


async def get_balance(user_id):

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            "SELECT balance FROM users WHERE user_id=$1",
            user_id
        )

        if not row:
            return 0.0

        return round(float(row["balance"]), 2)


async def add_balance(user_id, amount):

    async with pool.acquire() as conn:

        await conn.execute("""
        UPDATE users
        SET balance = balance + $1
        WHERE user_id=$2
        """,
        float(amount),
        user_id)


# =========================
# BONUS
# =========================
async def can_take_bonus(user_id):

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


async def give_bonus(user_id):

    async with pool.acquire() as conn:

        await conn.execute("""
        UPDATE users
        SET
            balance = balance + $1,
            last_bonus = $2
        WHERE user_id=$3
        """,
        BONUS_AMOUNT,
        time.time(),
        user_id) 
# =========================
# PROMOCODES
# =========================

async def create_promo(code: str, reward: float, uses: int):

    code = code.upper()

    async with pool.acquire() as conn:

        exists = await conn.fetchrow(
            "SELECT code FROM promocodes WHERE code=$1",
            code
        )

        if exists:
            return False

        await conn.execute("""
        INSERT INTO promocodes (
            code,
            reward,
            uses_left
        )
        VALUES ($1,$2,$3)
        """,
        code,
        float(reward),
        int(uses)
        )

        return True


async def delete_promo(code: str):

    code = code.upper()

    async with pool.acquire() as conn:

        result = await conn.execute(
            "DELETE FROM promocodes WHERE code=$1",
            code
        )

        return result != "DELETE 0"


async def get_promos():

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
        SELECT *
        FROM promocodes
        ORDER BY code
        """)

        return rows


async def activate_promo(user_id: int, code: str):

    code = code.upper()

    async with pool.acquire() as conn:

        promo = await conn.fetchrow(
            "SELECT * FROM promocodes WHERE code=$1",
            code
        )

        if not promo:
            return "not_found", 0

        used = await conn.fetchrow("""
        SELECT *
        FROM promo_uses
        WHERE user_id=$1
        AND code=$2
        """,
        user_id,
        code
        )

        if used:
            return "already_used", 0

        if promo["uses_left"] <= 0:
            return "no_uses", 0

        reward = float(promo["reward"])

        await conn.execute("""
        UPDATE users
        SET balance = balance + $1
        WHERE user_id=$2
        """,
        reward,
        user_id
        )

        await conn.execute("""
        INSERT INTO promo_uses (
            user_id,
            code
        )
        VALUES ($1,$2)
        """,
        user_id,
        code
        )

        await conn.execute("""
        UPDATE promocodes
        SET uses_left = uses_left - 1
        WHERE code=$1
        """,
        code
        )

        return "success", reward

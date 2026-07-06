import asyncpg
import time
import os

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
        raise RuntimeError(
            "❌ DATABASE_URL не найден!"
        )

    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:

        # =========================
        # USERS
        # =========================
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

        # =========================
        # PROMOCODES
        # =========================
        await conn.execute("""
CREATE TABLE IF NOT EXISTS promocodes (

    code TEXT PRIMARY KEY,

    reward DOUBLE PRECISION NOT NULL,

    max_uses INTEGER DEFAULT 1,

    uses INTEGER DEFAULT 0

)
""")

        # =========================
        # USED PROMOS
        # =========================
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
        INSERT INTO users (

            user_id,
            username,
            full_name,
            balance,
            last_bonus

        )
        VALUES ($1,$2,$3,$4,$5)

        ON CONFLICT (user_id)
        DO NOTHING

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

        if not row:
            return 0.0

        return round(float(row["balance"]), 2)


async def add_balance(user_id: int, amount: float):

    async with pool.acquire() as conn:

        await conn.execute("""

        UPDATE users

        SET balance = balance + $1

        WHERE user_id=$2

        """,

        float(amount),
        user_id
        )


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

        SET

            balance = balance + $1,

            last_bonus = $2

        WHERE user_id=$3

        """,

        BONUS_AMOUNT,
        time.time(),
        user_id
                          )
# =========================
# СОЗДАНИЕ ПРОМОКОДА
# =========================
async def create_promo(
    code: str,
    reward: float,
    max_uses: int
):

    code = code.upper()

    async with pool.acquire() as conn:

        await conn.execute("""
        INSERT INTO promocodes(
            code,
            reward,
            max_uses
        )
        VALUES($1,$2,$3)
        ON CONFLICT (code)
        DO UPDATE SET
            reward=EXCLUDED.reward,
            max_uses=EXCLUDED.max_uses
        """,
        code,
        reward,
        max_uses
        )


# =========================
# УДАЛЕНИЕ ПРОМОКОДА
# =========================
async def delete_promo(code: str):

    code = code.upper()

    async with pool.acquire() as conn:

        await conn.execute(
            "DELETE FROM promocodes WHERE code=$1",
            code
        )


# =========================
# АКТИВАЦИЯ ПРОМОКОДА
# =========================
async def activate_promo(
    user_id: int,
    code: str
):

    code = code.upper()

    async with pool.acquire() as conn:

        promo = await conn.fetchrow("""

        SELECT *

        FROM promocodes

        WHERE code=$1

        """, code)

        if not promo:
            return "not_found", 0

        already = await conn.fetchrow("""

        SELECT *

        FROM promo_activations

        WHERE user_id=$1
        AND code=$2

        """, user_id, code)

        if already:
            return "already_used", 0

        if promo["uses"] >= promo["max_uses"]:
            return "no_uses", 0

        await conn.execute("""

        INSERT INTO promo_activations(
            user_id,
            code
        )

        VALUES($1,$2)

        """, user_id, code)

        await conn.execute("""

        UPDATE promocodes

        SET uses=uses+1

        WHERE code=$1

        """, code)

        await conn.execute("""

        UPDATE users

        SET balance=balance+$1

        WHERE user_id=$2

        """,

        promo["reward"],
        user_id
        )

        return "success", float(promo["reward"])


# =========================
# СПИСОК ПРОМОКОДОВ
# =========================
async def get_promos():

    async with pool.acquire() as conn:

        return await conn.fetch("""

        SELECT *

        FROM promocodes

        ORDER BY code

        """)

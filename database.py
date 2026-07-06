import asyncpg
import os
import time

from config import START_BALANCE

pool = None

# =========================
# НАСТРОЙКИ
# =========================

BONUS_AMOUNT = 0.5
BONUS_COOLDOWN = 12 * 60 * 60


# =========================
# INIT DATABASE
# =========================

async def init_db():
    global pool

    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL не найден!")

    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:

# =========================
# USERS
# =========================

await conn.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    balance DOUBLE PRECISION DEFAULT 0,
    banned BOOLEAN DEFAULT FALSE,
    last_bonus DOUBLE PRECISION DEFAULT 0,

    referrer_id BIGINT,
    referrals INTEGER DEFAULT 0,
    ref_rewarded BOOLEAN DEFAULT FALSE
)
""")

# Если таблица уже существует — добавляем недостающие столбцы
await conn.execute("""
ALTER TABLE users
ADD COLUMN IF NOT EXISTS referrer_id BIGINT
""")

await conn.execute("""
ALTER TABLE users
ADD COLUMN IF NOT EXISTS referrals INTEGER DEFAULT 0
""")

await conn.execute("""
ALTER TABLE users
ADD COLUMN IF NOT EXISTS ref_rewarded BOOLEAN DEFAULT FALSE
""") 

        # =========================
        # PROMOCODES
        # =========================
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS promocodes(
            code TEXT PRIMARY KEY,
            reward DOUBLE PRECISION NOT NULL,
            max_uses INTEGER DEFAULT 1,
            uses INTEGER DEFAULT 0
        )
        """)

        # =========================
        # АКТИВАЦИИ ПРОМОКОДОВ
        # =========================
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS promo_activations(
            user_id BIGINT,
            code TEXT,
            PRIMARY KEY(user_id, code)
        )
        """)


# =========================
# СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
# =========================

async def add_user(user_id, username, full_name):

    async with pool.acquire() as conn:

        await conn.execute("""
        INSERT INTO users(
            user_id,
            username,
            full_name,
            balance,
            last_bonus
        )

        VALUES($1,$2,$3,$4,$5)

        ON CONFLICT(user_id)
        DO NOTHING
        """,
        user_id,
        username,
        full_name,
        float(START_BALANCE),
        0
                          )
        # =========================
# БАЛАНС
# =========================

async def get_balance(user_id):

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            "SELECT balance FROM users WHERE user_id=$1",
            user_id
        )

        if not row:
            return 0.0

        return float(row["balance"])


async def add_balance(user_id, amount):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users
            SET balance = balance + $1
            WHERE user_id=$2
            """,
            float(amount),
            user_id
        )


async def set_balance(user_id, amount):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users
            SET balance=$1
            WHERE user_id=$2
            """,
            float(amount),
            user_id
        )


# =========================
# БОНУС
# =========================

async def can_take_bonus(user_id):

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT last_bonus
            FROM users
            WHERE user_id=$1
            """,
            user_id
        )

        if not row:
            return False, 0

        last_bonus = float(row["last_bonus"])
        now = time.time()

        left = BONUS_COOLDOWN - (now - last_bonus)

        if left <= 0:
            return True, 0

        return False, int(left)


async def give_bonus(user_id):

    async with pool.acquire() as conn:

        await conn.execute(
            """
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
# ПРОМОКОДЫ
# =========================

async def create_promo(code, reward, max_uses):

    code = code.upper()

    async with pool.acquire() as conn:

        await conn.execute(
            """
            INSERT INTO promocodes(
                code,
                reward,
                max_uses,
                uses
            )
            VALUES($1,$2,$3,0)

            ON CONFLICT(code)
            DO UPDATE SET
                reward = EXCLUDED.reward,
                max_uses = EXCLUDED.max_uses,
                uses = 0
            """,
            code,
            float(reward),
            int(max_uses)
        )


async def delete_promo(code):

    async with pool.acquire() as conn:

        await conn.execute(
            "DELETE FROM promocodes WHERE code=$1",
            code.upper()
        )


async def activate_promo(user_id, code):

    code = code.upper()

    async with pool.acquire() as conn:

        promo = await conn.fetchrow(
            "SELECT * FROM promocodes WHERE code=$1",
            code
        )

        if not promo:
            return "not_found", 0

        activated = await conn.fetchrow(
            """
            SELECT 1
            FROM promo_activations
            WHERE user_id=$1
            AND code=$2
            """,
            user_id,
            code
        )

        if activated:
            return "already_used", 0

        if promo["uses"] >= promo["max_uses"]:
            return "no_uses", 0

        await conn.execute(
            """
            INSERT INTO promo_activations(user_id, code)
            VALUES($1,$2)
            """,
            user_id,
            code
        )

        await conn.execute(
            """
            UPDATE promocodes
            SET uses = uses + 1
            WHERE code=$1
            """,
            code
        )

        await conn.execute(
            """
            UPDATE users
            SET balance = balance + $1
            WHERE user_id=$2
            """,
            float(promo["reward"]),
            user_id
        )

        return "success", float(promo["reward"])


async def get_promos():

    async with pool.acquire() as conn:

        return await conn.fetch(
            """
            SELECT *
            FROM promocodes
            ORDER BY code
            """
        )


# =========================
# БАНЫ
# =========================

async def ban_user(user_id):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users
            SET banned = TRUE
            WHERE user_id=$1
            """,
            user_id
        )


async def unban_user(user_id):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users
            SET banned = FALSE
            WHERE user_id=$1
            """,
            user_id
        )


async def is_banned(user_id):

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT banned
            FROM users
            WHERE user_id=$1
            """,
            user_id
        )

        if not row:
            return False

        return bool(row["banned"])

# =========================
# РЕФЕРАЛЬНАЯ СИСТЕМА
# =========================

REF_REWARD = 0.5


async def set_referrer(user_id: int, referrer_id: int):

    if user_id == referrer_id:
        return

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT referrer_id
            FROM users
            WHERE user_id=$1
            """,
            user_id
        )

        if not row:
            return

        if row["referrer_id"] is not None:
            return

        await conn.execute(
            """
            UPDATE users
            SET referrer_id=$1
            WHERE user_id=$2
            """,
            referrer_id,
            user_id
        )


async def reward_referrer(user_id: int):

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT referrer_id, ref_rewarded
            FROM users
            WHERE user_id=$1
            """,
            user_id
        )

        if not row:
            return

        if row["ref_rewarded"]:
            return

        if row["referrer_id"] is None:
            return

        await conn.execute(
            """
            UPDATE users
            SET balance = balance + $1,
                referrals = referrals + 1
            WHERE user_id=$2
            """,
            REF_REWARD,
            row["referrer_id"]
        )

        await conn.execute(
            """
            UPDATE users
            SET ref_rewarded=TRUE
            WHERE user_id=$1
            """,
            user_id
        )


async def get_ref_info(user_id: int):

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT referrals
            FROM users
            WHERE user_id=$1
            """,
            user_id
        )

        if not row:
            return 0

        return row["referrals"]

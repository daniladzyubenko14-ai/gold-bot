import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE = "database.db"

START_BALANCE = 0

ADMINS = [7894106165]

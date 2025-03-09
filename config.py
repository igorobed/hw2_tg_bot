import os
from dotenv import load_dotenv
import sqlite3


load_dotenv()


TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не установлена!")

import os
from dotenv import load_dotenv


load_dotenv()


TOKEN = os.getenv("TOKEN")


if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не установлена!")

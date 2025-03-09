from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import router
from middlewares import LoggingMiddleware
import asyncio
from utils import create_users_table


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)
dp.message.middleware(LoggingMiddleware())


async def main():
    print("Бот запущен!")
    create_users_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
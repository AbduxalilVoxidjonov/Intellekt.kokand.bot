import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from database.database_user import create_table
from database import course_database, course_description,channel

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    create_table()
    course_database.create_table_course()
    course_description.create_table_description()
    channel.create_channel_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
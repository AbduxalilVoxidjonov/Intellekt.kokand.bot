import sqlite3
from aiogram import Bot
import asyncio
import config  # Token config fayldan olinadi

DB_NAME = "bot_database.db"
bot = Bot(token=config.TOKEN)

async def send_notification(message: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Barcha foydalanuvchilarning IDlarini olish
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    conn.close()

    for user in users:
        user_id = user[0]
        try:
            await bot.send_message(chat_id=user_id, text=message)
            await asyncio.sleep(0.1)  # Antiflood uchun ozgina kutish
        except Exception as e:
            print(f"Xatolik {user_id} ga yuborishda: {e}")

# Notifikatsiya jo‘natish uchun chaqirish:
# asyncio.run(send_notification("📢 Yangi e'lon: Bizning yangi kursimiz boshlandi! 🚀"))

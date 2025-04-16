from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.course_database import get_courses
from database.channel import get_channels

main_keybord = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Ro‘yxatdan o‘tish"),
            #about me
            KeyboardButton(text="Shaxsiy kabinet")
        ],
        [
            # kurs haqida malumot
            KeyboardButton(text="📚 Kurslarimiz"),
            KeyboardButton(text="Shartnoma olish")
        ]
    ],
    resize_keyboard=True
)

async def main_channels():
    channels = get_channels()  # 📌 Bazadan kanal URL'larini olish

    if not channels:
        return None  # Agar kanallar bo‘lmasa, `None` qaytariladi

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"📢 {url.split('/')[-1]}", url=url)]
            for url in channels
        ] +
        [[InlineKeyboardButton(text="✅ A’zo bo‘ldim", callback_data="check_subscription")]]
    )

    return keyboard


async def kurslar_haqida():
    keyboard = []
    row = []

    courses = get_courses()  # 📌 Funksiya chaqirilishi kerak

    for course in courses:
        course_id, course_name = course  # 📌 Tupleni ajratamiz
        row.append(InlineKeyboardButton(text=course_name, callback_data=f"course_{course_id}"))  # 🔹 ID ni callback_data sifatida beramiz

        if len(row) == 2:  # Har 2 ta tugmadan keyin yangi qator
            keyboard.append(row)
            row = []

    if row:  # Agar oxirgi qator to‘lib ulgurmagan bo‘lsa, uni ham qo‘shamiz
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

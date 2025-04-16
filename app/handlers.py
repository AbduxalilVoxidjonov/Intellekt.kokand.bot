import os

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram import Bot, types
from aiogram.utils.markdown import code
from aiogram.types import FSInputFile
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app import keybords as kb
from database import database_user
from database import course_database, course_description
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from app.register import RegistrationHandler, RegistrationState
from database.database_user import get_users, get_user_shartnoma
from app.sendNotification import send_notification
from app.generate_shartnoma import generate_contract
from app.update_user import updateHandler, UpdateState
from database.channel import get_channels, add_channel, update_channel, delete_channel
from app.keybords import main_channels, main_keybord
import config  # Token config fayldan olinadi
from config import SHARTNOMA

router = Router()
bot = Bot(token=config.TOKEN)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    channels = get_channels()  # 📌 Kanallarni bazadan olish

    all_subscribed = True  # Foydalanuvchi barcha kanallarga obuna bo‘lganmi?

    for channel_name in channels:
        try:
            chat_member = await bot.get_chat_member(chat_id=f"@{channel_name}", user_id=user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                all_subscribed = False
                break  # Bitta kanalga ham obuna bo‘lmasa, tsiklni to‘xtatamiz
        except:
            all_subscribed = False
            break

    if all_subscribed:
        await message.answer("✅ Siz barcha kanallarga obuna bo‘lgansiz! Xush kelibsiz!", reply_markup=main_keybord)
    else:
        keyboard = await main_channels()  # 📌 Kanallarga obuna bo‘lish tugmalarini olish
        await message.answer(
            "❌ Siz hali barcha kanallarga a'zo bo‘lmadingiz. Davom etish uchun obuna bo‘ling!",
            reply_markup=keyboard
        )


@router.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    channels = get_channels()  # 📌 Bazadan kanal URL'larini olish
    all_subscribed = True  # Foydalanuvchi barcha kanallarga obuna bo‘lganmi?

    for url in channels:
        channel_username = url.split("/")[-1]  # URL dan username ajratib olish

        try:
            chat_member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                all_subscribed = False
                break  # Bitta kanalga ham obuna bo‘lmasa, tsiklni to‘xtatamiz
        except Exception as e:
            all_subscribed = False
            print(f"❌ Xatolik: {e}")  # Xatolikni konsolga chiqarish
            break

    if all_subscribed:
        await callback.message.answer("✅ Ajoyib! Siz barcha kanallarga a'zo bo‘lgansiz. Davom etishingiz mumkin!",
                                      reply_markup=kb.main_keybord)
    else:
        keyboard = await main_channels()
        if keyboard:  # 📌 Agar keyboard mavjud bo‘lsa, `edit_reply_markup()` bajariladi
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await callback.message.answer("❌ Kanal ro‘yxati mavjud emas!")

    await callback.answer()


# Ro‘yxatdan o‘tish tugmasi bosilganda
@router.message(lambda message: message.text == "📝 Ro‘yxatdan o‘tish")
async def start_registration(message: Message, state: FSMContext):
    if (database_user.chech_user(message.from_user.id)):
        await message.answer("Siz ro'yxatdan o'tib bo'lgansiz.")
        return
    else:
        await RegistrationHandler.start_registration(message, state)


# FSM bosqichlarini boshqarish
router.message.register(RegistrationHandler.ask_age, RegistrationState.full_name)
router.message.register(RegistrationHandler.ask_address, RegistrationState.age)
router.message.register(RegistrationHandler.ask_phone, RegistrationState.address)
router.message.register(RegistrationHandler.finish_registration, RegistrationState.phone_number)


@router.message(Command("help"))
async def get_command(message: types.Message):
    await message.answer("Bu /help buyrug'i")


@router.message(Command("menu"))
async def get_command(message: types.Message):
    await message.answer("Bu /menu buyrug'i")


@router.message(Command("send"))
async def admin_send_notification(message: types.Message):
    if message.from_user.id == config.ADMIN:  # Admin ID sini yozish kerak
        args = message.text.split(" ", 1)
        if len(args) < 2:
            await message.answer("❗ Xabar matnini yozing: /send [xabar]")
            return

        text = args[1]
        await send_notification(text)
        await message.answer("✅ Xabar barcha foydalanuvchilarga yuborildi!")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("users"))
async def all_users(message: types.Message):
    if message.from_user.id == config.ADMIN:
        users = get_users()
        response = "Foydalanuvchilar ro'yxati:\n\n"
        for one_user in users:
            response += f"🆔 ID: {one_user[0]}\n👤 F.I.Sh: {one_user[1]}\n📞 Telefon: {one_user[2]}\n\n"
        await message.answer(response)
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("addcourse"))
async def add_course(message: types.Message):
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=1)  # Kurs nomini olish

        if len(args) < 2 or not args[1].strip():
            await message.answer("❗ Kurs nomini yozing:\n" + code("/addcourse [kurs_nomi]"))
            return

        course_name = args[1].strip()  # Keraksiz bo‘sh joylarni olib tashlaymiz
        course_database.add_courses(name=course_name)  # Kursni bazaga qo‘shish

        await message.answer(f"✅ {course_name} kursi qo‘shildi!")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("updatecourse"))
async def update_course_command(message: types.Message):
    """ Admin kurs nomini yangilashi uchun """
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=2)

        if len(args) < 3:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/updatecourse [course_id] [new_name]`")
            return

        course_id, new_name = args[1], args[2]

        course_database.update_course(course_id, new_name)  # 📌 Kurs nomini yangilash
        await message.answer(f"✅ Kurs nomi {new_name} ga o‘zgartirildi!")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("deletecourse"))
async def delete_course_command(message: types.Message):
    """ Admin kursni o‘chirishi uchun """
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/deletecourse [course_id]`")
            return

        course_id = args[1]

        course_database.delete_course(course_id)  # 📌 Kursni o‘chirish
        await message.answer(f"✅ Kurs (ID: {course_id}) o‘chirildi!")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("getcourse"))
async def get_course(message: types.Message):
    if message.from_user.id == config.ADMIN:
        courses = course_database.get_courses()  # 📌 Kurslarni bazadan olish

        if courses:  # Kurslar mavjudligini tekshiramiz
            course_text = "📚 <b>Kurslar ro‘yxati:</b>\n\n"  # Xabar matni
            for course_id, course_name in courses:
                course_text += f"🔹 <b>{course_name}</b> (ID: {course_id})\n"

            await message.answer(course_text, parse_mode="HTML")
        else:
            await message.answer("❗ Hozircha kurslar mavjud emas.")

    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("add_description"))
async def add_description_handler(message: types.Message):
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=2)

        if len(args) < 3:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/add_description [course_id] [description]`",
                                 parse_mode="Markdown")
            return

        course_id, description = args[1], args[2]

        if course_description.add_description(course_id, description):
            await message.answer(f"✅ Kurs ({course_id}) uchun tavsif qo‘shildi!", parse_mode="Markdown")
        else:
            await message.answer(
                f"❗ Bu kurs ({course_id}) uchun tavsif allaqachon mavjud!\n"
                f"🔄 Uni o‘zgartirish uchun: `/edit_description {course_id} [yangi tavsif]`",
                parse_mode="Markdown"
            )
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("edit_description"))
async def edit_description_handler(message: types.Message):
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=2)

        if len(args) < 3:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/edit_description [course_id] [yangi_tavsif]`",
                                 parse_mode="Markdown")
            return

        course_id, new_description = args[1], args[2]

        if course_description.update_description(course_id, new_description):
            await message.answer(f"✅ Kurs ({course_id}) uchun tavsif yangilandi!", parse_mode="Markdown")
        else:
            await message.answer("❌ Tavsif yangilashda xatolik yuz berdi!", parse_mode="Markdown")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("delete_description"))
async def delete_description_handler(message: types.Message):
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/delete_description [course_id]`",
                                 parse_mode="Markdown")
            return

        course_id = args[1]

        if course_description.delete_description(course_id):
            await message.answer(f"✅ Kurs ({course_id}) uchun tavsif o‘chirildi!", parse_mode="Markdown")
        else:
            await message.answer(f"❌ {course_id} ID li kurs uchun tavsif topilmadi!", parse_mode="Markdown")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.callback_query(F.data.startswith("course_"))
async def get_course_info(callback: CallbackQuery):
    """ Kurs haqida ma'lumot chiqarish """
    course_id = callback.data.split("_")[1]  # Masalan: "course_2" => "2"

    description = course_description.get_description(course_id)  # Kurs tavsifini olish
    if not description:
        description = "❌ Bu kurs uchun tavsif mavjud emas!"

    response = f"📚 *Kurs ID:* {course_id}\n📝 *Tavsif:* {description}"

    await callback.message.answer(response, parse_mode="Markdown")
    await callback.answer()


@router.message(F.text == "Shartnoma olish")
async def send_contract(message: types.Message):
    user_id = message.from_user.id

    full_name_tuple = get_user_shartnoma(user_id)

    if not full_name_tuple:
        await message.answer("❌ Siz ro‘yxatdan o‘tmagansiz.")
        return

    full_name = full_name_tuple[0]
    file_path = generate_contract(user_id, full_name)  # 📌 Shartnoma yaratish

    if file_path:
        try:
            # ✅ Faylni InputFile sifatida ochamiz
            document = FSInputFile(file_path)

            # ✅ 1. Faylni foydalanuvchiga yuboramiz
            await message.answer_document(document, caption="📄 Sizning shartnomangiz!")

            # ✅ 2. Faylni kanalga yuboramiz
            await bot.send_document(chat_id=SHARTNOMA, document=document,
                                    caption=f"📄 {full_name} uchun shartnoma yuklandi.")

        finally:

            # ✅ Faylni faqat .docx yoki .pdf bo'lsa o'chirib tashlaymiz

            if file_path.endswith((".docx", ".pdf")):  # .docx va .pdf kengaytmalarini tekshirish

                if os.path.exists(file_path):

                    os.remove(file_path)
                    os.remove(file_path.replace(".pdf", ".docx"))  # .pdf faylni o‘chirishda .docx ham o‘chiriladi

                    print(f"{file_path} o‘chirildi ✅")

                else:

                    print(f"{file_path} topilmadi ❌")

            else:

                print(f"Fayl kengaytmasi mos emas: {file_path} ❌")

    else:
        await message.answer("❌ Shartnomani yaratishda xatolik yuz berdi.")


@router.message(F.text == "Shaxsiy kabinet")
async def get_user_info(message: types.Message, state: FSMContext):
    user = database_user.get_user(message.from_user.id)  # 📌 Statik metod chaqirish

    if user:
        response = (
            f"🆔 ID:      {user[0]}\n"
            f"👤 F.I.Sh:  {user[1]}\n"
            f"📅 Yosh:    {user[2]}\n"
            f"📍 Manzil:  {user[3]}\n"
            f"📞 Telefon: {user[4]}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Ma'lumotlarni o‘zgartirish", callback_data="edit_info")],
            ]
        )

        await message.answer(response, reply_markup=keyboard)
    else:
        await message.answer("❌ Siz ro‘yxatdan o‘tmagansiz. Ro‘yxatdan o‘ting!")


@router.callback_query(F.data == "edit_info")
async def edit_user_info(callback: CallbackQuery, state: FSMContext):
    await updateHandler.start_update(callback.message, state)
    await callback.answer()


router.message.register(updateHandler.ask_age, UpdateState.full_name)
router.message.register(updateHandler.ask_address, UpdateState.age)
router.message.register(updateHandler.ask_phone, UpdateState.address)
router.message.register(updateHandler.finish_update, UpdateState.phone_number)


@router.message(F.text == "📚 Kurslarimiz")
async def kurslar(message: types.Message, state: FSMContext):
    await message.answer("Bizning mavjud kurslar", reply_markup=await kb.kurslar_haqida())


@router.message(Command("add_channel"))
async def add_channel_command(message: types.Message):
    """Admin kanal qo‘shishi uchun funksiya"""
    if message.from_user.id == config.ADMIN:  # Faqat admin qo‘shishi mumkin
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/add_channel [kanal_nomi]`")
            return

        name = args[1].lstrip("@")  # @ belgisini olib tashlash

        if add_channel(name):
            await message.answer(f"✅ @{name} kanali bazaga qo‘shildi!")
        else:
            await message.answer("❌ Bu kanal avval qo‘shilgan!")
    else:
        await message.answer("❌ Siz admin emassiz!")


@router.message(Command("update_channel"))
async def update_channel_command(message: types.Message):
    """Admin kanalni yangilashi uchun funksiya"""
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=2)

        if len(args) < 3:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/update_channel [Old_channel] [New_channel]`")
            return

        channel_id, new_name = args[1], args[2]

        update_channel(channel_id, new_name)


@router.message(Command("delete_channel"))
async def delete_channel_command(message: types.Message):
    """Admin kanalni o‘chirishi uchun funksiya"""
    if message.from_user.id == config.ADMIN:
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            await message.answer("❗ To‘g‘ri formatda kiriting:\n`/delete_channel [channel_name]`")
            return

        channel_name = args[1]

        delete_channel(channel_name)
        await message.answer(f"✅ @{channel_name} kanali o‘chirildi!")
    else:
        await message.answer("❌ Siz admin emassiz!")

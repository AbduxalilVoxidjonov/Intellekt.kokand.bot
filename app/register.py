from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import hbold
from database.database_user import add_user


class RegistrationState(StatesGroup):
    id = State()
    full_name = State()
    age = State()
    address = State()
    phone_number = State()


class RegistrationHandler:
    @staticmethod
    async def start_registration(message: types.Message, state: FSMContext):
        await state.update_data(id=message.from_user.id)  # Telegram ID saqlaymiz
        await message.answer("Ma'lumotlarni kiritishda etiborli bo'ling: \n👤 Iltimos, familiya, ism va sharifingizni kiriting:")
        await state.set_state(RegistrationState.full_name)

    @staticmethod
    async def ask_age(message: types.Message, state: FSMContext):
        await state.update_data(full_name=message.text)
        await message.answer("📅 Yoshingizni kiriting: (Misol: 20)")
        await state.set_state(RegistrationState.age)

    @staticmethod
    async def ask_address(message: types.Message, state: FSMContext):
        await state.update_data(age=message.text)
        await message.answer("📍 Manzilingizni kiriting:")
        await state.set_state(RegistrationState.address)

    @staticmethod
    async def ask_phone(message: types.Message, state: FSMContext):
        await state.update_data(address=message.text)
        await message.answer("📞 Telefon raqamingizni kiriting (Misol: +998901234567):")
        await state.set_state(RegistrationState.phone_number)

    @staticmethod
    async def finish_registration(message: types.Message, state: FSMContext):
        await state.update_data(phone_number=message.text)
        data = await state.get_data()

        add_user(
            user_id=data["id"],
            full_name=data["full_name"],
            age=data["age"],
            address=data["address"],
            phone_number=data["phone_number"]
        )

        response = (
            f"✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!\n\n"
            f"🆔 {hbold('ID:')}      {data['id']}\n"
            f"👤 {hbold('F.I.Sh:')}  {data['full_name']}\n"
            f"📅 {hbold('Yosh:')}    {data['age']}\n"
            f"📍 {hbold('Manzil:')}  {data['address']}\n"
            f"📞 {hbold('Telefon:')} {data['phone_number']}"
        )

        await message.answer(response, parse_mode="HTML")
        await state.clear()

    @staticmethod
    async def is_registering(state: FSMContext):
        """ Agar foydalanuvchi ro‘yxatdan o‘tish jarayonida bo‘lsa, True qaytaradi """
        current_state = await state.get_state()
        return current_state is not None

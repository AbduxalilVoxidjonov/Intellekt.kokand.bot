from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import hbold
from database.database_user import update_user


class UpdateState(StatesGroup):
    id = State()
    full_name = State()
    age = State()
    address = State()
    phone_number = State()

class updateHandler():
    @staticmethod
    async def start_update(message: types.Message, state: FSMContext):
        await state.update_data(id=message.from_user.id)  # Telegram ID saqlaymiz
        await message.answer(
            "Ma'lumotlarni kiritishda etiborli bo'ling: \n👤 Iltimos, familiya, ism va sharifingizni kiriting:")
        await state.set_state(UpdateState.full_name)

    @staticmethod
    async def ask_age(message: types.Message, state: FSMContext):
        await state.update_data(full_name=message.text)
        await message.answer("📅 Yoshingizni kiriting: (Misol: 20)")
        await state.set_state(UpdateState.age)

    @staticmethod
    async def ask_address(message: types.Message, state: FSMContext):
        await state.update_data(age=message.text)
        await message.answer("📍 Manzilingizni kiriting:")
        await state.set_state(UpdateState.address)

    @staticmethod
    async def ask_phone(message: types.Message, state: FSMContext):
        await state.update_data(address=message.text)
        await message.answer("📞 Telefon raqamingizni kiriting (Misol: +998901234567):")
        await state.set_state(UpdateState.phone_number)

    @staticmethod
    async def finish_update(message: types.Message, state: FSMContext):
        await state.update_data(phone_number=message.text)
        data = await state.get_data()

        update_user(
            user_id=message.from_user.id,
            full_name=data["full_name"],
            age=data["age"],
            address=data["address"],
            phone_number=data["phone_number"]
        )

        response = (
            f"✅ Siz muvaffaqiyatli ma'lumotlaringizni yangiladingiz!\n\n"
            f"🆔 {hbold('ID:')}      {message.from_user.id}\n"
            f"👤 {hbold('F.I.Sh:')}  {data['full_name']}\n"
            f"📅 {hbold('Yosh:')}    {data['age']}\n"
            f"📍 {hbold('Manzil:')}  {data['address']}\n"
            f"📞 {hbold('Telefon:')} {data['phone_number']}"
        )
        await message.answer(response, parse_mode="HTML")
        await state.clear()
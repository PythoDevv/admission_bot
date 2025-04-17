from aiogram import Router, F, types
from aiogram.filters import Command
from database.repositories import UserRepository
from database.base import AsyncSessionLocal
from keyboards.user import main_menu, cancel_keyboard
from config import Config

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_user(message.from_user.id)

        if not user:
            await message.answer(
                "Assalamu alaykum va rahmatulloh.\n\n"
                "Al-Buxoriy nomidagi Xalqaro ilmlar markaziga qabuldan o'tish botiga hush kelibsiz.\n\n"
                "Bu botdan shaxsiy arizangizni topshira olasiz.",
                reply_markup=main_menu()
            )
            await repo.create_user(message.from_user.id)
        else:
            await message.answer("Siz allaqachon ro'yxatdan o'tgansiz!", reply_markup=main_menu())


@router.message(F.text == "Biz haqimizda")
async def about_handler(message: types.Message):
    text = (
        "Al-Buxoriy Xalqaro Ilmlar Markazi haqida ma'lumot:\n\n"
        "Bizning manzil: Toshkent shahar, Yunusobod tumani\n"
        "Telefon: +998 71 123 45 67\n"
        "Ish vaqti: 09:00 - 18:00"
    )
    await message.answer(text)
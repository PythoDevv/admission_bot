from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import asyncpg
import pandas as pd
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from .env
BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_CONFIG = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT'),
    "database": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD')
}


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)


# ====================== KEYBOARDS ======================

def start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Ariza topshirish"),
        KeyboardButton(text="Biz haqimizda")
    )
    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Bekor qilish")]],
        resize_keyboard=True
    )


def passport_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Pasport yuklash"),
        KeyboardButton(text="Pasport olaman")
    )
    builder.row(KeyboardButton(text="Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Barchaga xabar yuborish"))
    builder.row(
        KeyboardButton(text="Admin qo'shish"),
        KeyboardButton(text="Admin o'chirish")
    )
    builder.row(KeyboardButton(text="Foydalanuvchilarni eksport qilish"))
    builder.row(KeyboardButton(text="Admin panelini yopish"))
    return builder.as_markup(resize_keyboard=True)


def confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Qayta yozish", callback_data="cancel")
    )
    return builder.as_markup()


# ====================== STATE CLASSES ======================

class Form(StatesGroup):
    full_name = State()
    birth_date = State()
    phone = State()
    telegram_username = State()
    passport = State()
    attestat = State()
    motivation = State()
    confirm = State()


class AdminBroadcast(StatesGroup):
    message = State()


class AdminAddRemove(StatesGroup):
    add_admin = State()
    remove_admin = State()


# ====================== DATABASE FUNCTIONS ======================

async def create_pool():
    return await asyncpg.create_pool(**DB_CONFIG)


async def create_tables():
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                full_name TEXT,
                birth_date TEXT,
                phone TEXT,
                telegram_username TEXT,
                passport TEXT,
                attestat TEXT,
                motivation TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')


# ====================== HANDLERS ======================

@router.message(Command("start"))
async def start(message: types.Message):
    pool = await create_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            message.from_user.id
        )

    if not user:
        await message.answer(
            "Assalamu alaykum va rahmatulloh.\n\n"
            "Al-Buxoriy nomidagi Xalqaro ilmlar markaziga qabuldan o'tish botiga hush kelibsiz.\n\n"
            "Bu botdan shaxsiy savollar hamda IQ teslaridan o'tasiz va ariza topshirgan bo'lasiz.",
            reply_markup=start_keyboard()
        )
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (telegram_id) VALUES ($1)",
                message.from_user.id
            )
    else:
        await message.answer("Siz allaqachon ro'yxatdan o'tgansiz!", reply_markup=start_keyboard())


@router.message(F.text == "Ariza topshirish")
async def start_application(message: types.Message, state: FSMContext):
    await message.answer(
        "1-bosqich\n\n1. Ism familiya ota ismi ona ismi:\n"
        "(To'liq ismingizni kiriting, masalan: Abdullayev Abdulla Abdulla o'g'li)",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(Form.full_name)


@router.message(Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        await message.answer("Ariza bekor qilindi.", reply_markup=start_keyboard())
        return

    await state.update_data(full_name=message.text)
    await message.answer("2. Tug'ilgan sana (KK.OO.YYYY):")
    await state.set_state(Form.birth_date)


@router.message(Form.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        await message.answer("Ariza bekor qilindi.", reply_markup=start_keyboard())
        return

    await state.update_data(birth_date=message.text)
    await message.answer("3. Telefon raqamingiz (998XXYYYYYYY):")
    await state.set_state(Form.phone)


@router.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        await message.answer("Ariza bekor qilindi.", reply_markup=start_keyboard())
        return

    await state.update_data(phone=message.text)
    await message.answer("4. Telegram foydalanuvchi nomi (@sizning_nomiz):")
    await state.set_state(Form.telegram_username)


@router.message(Form.telegram_username)
async def process_telegram_username(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        await message.answer("Ariza bekor qilindi.", reply_markup=start_keyboard())
        return

    await state.update_data(telegram_username=message.text)
    await message.answer("5. Qizil pasportingizni yuklang (PDF) yoki 'Pasport olaman' tugmasini bosing:",
                         reply_markup=passport_keyboard())
    await state.set_state(Form.passport)


@router.message(Form.passport, F.document | F.text)
async def process_passport(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        await message.answer("Ariza bekor qilindi.", reply_markup=start_keyboard())
        return

    if message.text == "Pasport olaman":
        await state.update_data(passport="Pasport olmoqda")
        await message.answer("6. Maktab attestatingizni yuklang (PDF):", reply_markup=cancel_keyboard())
        await state.set_state(Form.attestat)
    elif message.document:
        if message.document.mime_type == "application/pdf":
            file_id = message.document.file_id
            await state.update_data(passport=file_id)
            await message.answer("6. Maktab attestatingizni yuklang (PDF):", reply_markup=cancel_keyboard())
            await state.set_state(Form.attestat)
        else:
            await message.answer("Faqat PDF fayl yuklang!")
    else:
        await message.answer("Iltimos, pasportingizni yuklang yoki 'Pasport olaman' tugmasini bosing!")


# Continue with attestat and motivation handlers similarly...

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    pool = await create_pool()
    async with pool.acquire() as conn:
        is_admin = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM admins WHERE telegram_id = $1)",
            message.from_user.id
        )

    if is_admin:
        await message.answer("Admin panel:", reply_markup=admin_keyboard())
    else:
        await message.answer("Sizga ruxsat yo'q!")


@router.message(F.text == "Barchaga xabar yuborish")
async def start_broadcast(message: types.Message, state: FSMContext):
    pool = await create_pool()
    async with pool.acquire() as conn:
        is_admin = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM admins WHERE telegram_id = $1)",
            message.from_user.id
        )

    if is_admin:
        await message.answer("Xabarni yuboring (HTML formatida):", reply_markup=cancel_keyboard())
        await state.set_state(AdminBroadcast.message)
    else:
        await message.answer("Sizga ruxsat yo'q!")


@router.message(AdminBroadcast.message)
async def send_broadcast(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        await message.answer("Xabar yuborish bekor qilindi.", reply_markup=admin_keyboard())
        return

    pool = await create_pool()
    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT telegram_id FROM users")

    success = 0
    for user in users:
        try:
            await bot.send_message(
                chat_id=user['telegram_id'],
                text=message.html_text,
                parse_mode="HTML"
            )
            success += 1
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")

    await message.answer(f"Xabar {success} ta foydalanuvchiga yetkazildi.", reply_markup=admin_keyboard())
    await state.clear()


# ====================== MAIN FUNCTION ======================

async def main():
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
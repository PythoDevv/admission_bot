from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
from database.repositories import UserRepository
from database.base import AsyncSessionLocal
from keyboards.user import (
    cancel_keyboard,
    passport_choice,
    confirm_application_keyboard
)
import re
import datetime
import uuid

router = Router()


class ApplicationStates(StatesGroup):
    full_name = State()
    birth_date = State()
    phone = State()
    telegram_username = State()
    passport = State()
    attestat = State()
    motivation = State()
    confirmation = State()


# ====================== VALIDATION HELPERS ======================

async def validate_full_name(name: str) -> bool:
    return len(name.split()) >= 3  # At least 3 components: family name, first name, patronymic


async def validate_birth_date(date: str) -> bool:
    try:
        day, month, year = map(int, date.split('.'))
        datetime.datetime(year=year, month=month, day=day)
        return True
    except:
        return False


async def validate_phone(phone: str) -> bool:
    return phone.startswith('998') and len(phone) == 12 and phone.isdigit()


async def validate_username(username: str) -> bool:
    return username.startswith('@') and len(username) > 1 and ' ' not in username


# ====================== HANDLERS ======================

@router.message(F.text == "Ariza topshirish")
async def start_application(message: types.Message, state: FSMContext):
    await message.answer(
        "1-bosqich\n\nIsm familiya ota ismi ona ismi:\n"
        "(To'liq ismingizni kiriting, masalan: Abdullayev Abdulla Abdulla o'g'li)",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(ApplicationStates.full_name)


@router.message(ApplicationStates.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if not await validate_full_name(message.text):
        await message.answer("Iltimos to'liq ism familiyangizni kiriting!\n\n"
                             "Masalan: Abdullayev Abdulla Abdulla o'g'li")
        return

    await state.update_data(full_name=message.text)
    await message.answer("2. Tug'ilgan sanangiz (KK.OO.YYYY):")
    await state.set_state(ApplicationStates.birth_date)


@router.message(ApplicationStates.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    if not await validate_birth_date(message.text):
        await message.answer("Noto'g'ri sana formati! Iltimos KK.OO.YYYY formatida kiriting.\n"
                             "Masalan: 31.12.2000")
        return

    await state.update_data(birth_date=message.text)
    await message.answer("3. Telefon raqamingiz (998XXYYYYYYY):")
    await state.set_state(ApplicationStates.phone)


@router.message(ApplicationStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if not await validate_phone(message.text):
        await message.answer("Noto'g'ri telefon raqam formati!\n"
                             "Iltimos 998XXXXXXXXX formatida kiriting.\n"
                             "Masalan: 998901234567")
        return

    await state.update_data(phone=message.text)
    await message.answer("4. Telegram foydalanuvchi nomi (@sizning_nomiz):")
    await state.set_state(ApplicationStates.telegram_username)


@router.message(ApplicationStates.telegram_username)
async def process_telegram_username(message: types.Message, state: FSMContext):
    if not await validate_username(message.text):
        await message.answer("Noto'g'ri Telegram nomi!\n"
                             "Iltimos @ belgisi bilan boshlangan foydalanuvchi nomini kiriting.\n"
                             "Masalan: @Ilyosbek_Kv")
        return

    await state.update_data(telegram_username=message.text)
    await message.answer(
        "5. Qizil pasportingizni yuklang (PDF hujjat shaklida):",
        reply_markup=passport_choice()
    )
    await state.set_state(ApplicationStates.passport)


@router.message(ApplicationStates.passport, F.text | F.document)
async def process_passport(message: types.Message, state: FSMContext):
    if message.text == "Pasport olaman":
        await state.update_data(passport="pasport_olaman")
        await message.answer("6. Maktab attestatingizni yuklang (PDF):", reply_markup=cancel_keyboard())
        await state.set_state(ApplicationStates.attestat)
    elif message.document:
        if message.document.mime_type != "application/pdf":
            await message.answer("Iltimos faqat PDF fayl yuklang!")
            return
        file_id = message.document.file_id
        await state.update_data(passport=file_id)
        await message.answer("6. Maktab attestatingizni yuklang (PDF):", reply_markup=cancel_keyboard())
        await state.set_state(ApplicationStates.attestat)
    else:
        await message.answer("Iltimos pasportingizni yuklang yoki tugmalardan birini tanlang!")


@router.message(ApplicationStates.attestat, F.document)
async def process_attestat(message: types.Message, state: FSMContext):
    if message.document.mime_type != "application/pdf":
        await message.answer("Iltimos faqat PDF fayl yuklang!")
        return

    file_id = message.document.file_id
    await state.update_data(attestat=file_id)
    await message.answer(
        "7. Motivatsion xat:\n"
        "1. Dorilulumga nega topshiryapsiz?\n"
        "2. Oliy maqsadingiz nima?\n"
        "(Kamida 200 ta belgidan iborat bo'lsin)",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(ApplicationStates.motivation)


@router.message(ApplicationStates.motivation)
async def process_motivation(message: types.Message, state: FSMContext):
    if len(message.text) < 200:
        await message.answer("Iltimos kamida 200 ta belgidan iborat motivatsion xat yozing!")
        return

    await state.update_data(motivation=message.text)

    # Compile all data
    data = await state.get_data()

    # Format confirmation message
    attestat = 'Yuklangan' if data.get('attestat') else 'Yo\'q'
    passport_text = 'Pasport olaman' if data['passport'] == 'pasport_olaman' else 'Yuklangan'
    confirmation_text = (
        "📄 Arizangizni tasdiqlaysizmi?\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"🎂 Tug'ilgan sana: {data['birth_date']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"📲 Telegram: {data['telegram_username']}\n"
        f"🛂 Pasport holati: {passport_text}\n"
        f"📜 Attestat: {attestat}\n"
        f"📝 Motivatsion xat: {data['motivation'][:100]}...")
    await message.answer(confirmation_text, reply_markup=confirm_application_keyboard())
    await state.set_state(ApplicationStates.confirmation)


@router.callback_query(ApplicationStates.confirmation, F.data == "confirm_application")
async def confirm_application_end(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        await repo.update_user(
            callback.from_user.id,
            full_name=data['full_name'],
            birth_date=data['birth_date'],
            phone=data['phone'],
            telegram_username=data['telegram_username'],
            passport=data['passport'],
            attestat=data.get('attestat'),
            motivation=data['motivation']
        )

    await callback.message.answer("✅ Arizangiz muvaffaqiyatli qabul qilindi!\n"
                                  "Adminlarimiz tez orada siz bilan bog'lanishadi.")
    await state.clear()


@router.callback_query(ApplicationStates.confirmation, F.data == "restart_application")
async def restart_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Ariza bekor qilindi. Yangi ariza boshlashingiz mumkin.")
    await callback.message.answer(
        "1-bosqich\n\nIsm familiya ota ismi ona ismi:\n"
        "(To'liq ismingizni kiriting, masalan: Abdullayev Abdulla Abdulla o'g'li)",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(ApplicationStates.full_name)


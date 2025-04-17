from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repositories import AdminRepository, UserRepository
from database.base import AsyncSessionLocal
from keyboards.admin import admin_panel, broadcast_confirmation
from config import Config
# import pandas as pd
from aiogram.filters import Command

router = Router()


class BroadcastStates(StatesGroup):
    message = State()


@router.message(Command("admin"))
async def admin_command(message: types.Message):
    async with AsyncSessionLocal() as session:
        repo = AdminRepository(session)
        if message.from_user.id not in Config.ADMIN_IDS and not await repo.is_admin(message.from_user.id):
            await message.answer("Sizga ruxsat yo'q!")
            return

        await message.answer("Admin paneli", reply_markup=admin_panel())


@router.message(F.text == "Barchaga xabar yuborish")
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer("Xabarni yuboring (HTML formatida):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(BroadcastStates.message)


@router.message(BroadcastStates.message)
async def process_broadcast(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        users = await repo.get_all_users()

        success = 0
        for user in users:
            try:
                await message.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message.html_text,
                    parse_mode="HTML"
                )
                success += 1
            except Exception as e:
                print(f"Xatolik: {e}")

        await message.answer(f"Xabar {success} ta foydalanuvchiga yetkazildi!", reply_markup=admin_panel())
        await state.clear()


# @router.message(F.text == "Foydalanuvchilarni eksport qilish")
# async def export_users(message: types.Message):
#     async with AsyncSessionLocal() as session:
#         repo = UserRepository(session)
#         users = await repo.get_all_users()
#
#         data = [{
#             "ID": user.id,
#             "Telegram ID": user.telegram_id,
#             "Ism": user.full_name,
#             "Telefon": user.phone,
#             "Ro'yxatdan o'tgan sana": user.created_at
#         } for user in users]
#
#         df = pd.DataFrame(data)
#         df.to_excel("users.xlsx", index=False)
#
#         await message.answer_document(
#             types.FSInputFile("users.xlsx"),
#             caption="Foydalanuvchilar ro'yxati"
#         )
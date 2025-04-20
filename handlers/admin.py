from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repositories import AdminRepository, UserRepository
from database.base import AsyncSessionLocal
from keyboards.admin import admin_panel, broadcast_confirmation
from config import Config
import pandas as pd
from aiogram.filters import Command
from main import bot
from database.base import AsyncSessionLocal, Base
from sqlalchemy.ext.asyncio import create_async_engine
from aiogram.fsm.state import State, StatesGroup

class CheckDocsState(StatesGroup):
    waiting_for_telegram_id = State()

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


@router.message(BroadcastStates.message, F.content_type.in_({
    'text', 'photo', 'video', 'document', 'audio', 'voice'
}))
async def process_broadcast(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        users = await repo.get_all_users()

        success = 0
        for user in users:
            try:
                if message.text:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=message.html_text if message.html_text else message.text,
                        parse_mode="HTML" if message.html_text else None
                    )
                elif message.photo:
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption,
                        parse_mode="HTML" if message.caption and '<' in message.caption else None
                    )
                elif message.document:
                    await bot.send_document(
                        chat_id=user.telegram_id,
                        document=message.document.file_id,
                        caption=message.caption,
                        parse_mode="HTML" if message.caption and '<' in message.caption else None
                    )
                # Add similar handlers for other content types
                success += 1
            except Exception as e:
                print(f"Xatolik {user.telegram_id} ga: {e}")

        await message.answer(
            f"✅ Xabar {success}/{len(users)} ta foydalanuvchiga yetkazildi!",
            reply_markup=admin_panel()
        )
        await state.clear()

@router.message(F.text == "Foydalanuvchilarni eksport qilish")
async def export_users(message: types.Message):
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        users = await repo.get_all_users()

        data = [{
            "ID": user.id,
            "Telegram ID": user.telegram_id,
            "Ism": user.full_name,
            "Telefon": user.phone,
            "Telegram Username": user.telegram_username,
            "Motivatsion xat": user.motivation,
            "Ro'yxatdan o'tgan sana": user.created_at
        } for user in users]

        df = pd.DataFrame(data)
        df.to_excel("users.xlsx", index=False)

        await message.answer_document(
            types.FSInputFile("users.xlsx"),
            caption="Foydalanuvchilar ro'yxati"
        )


class AddAdminStates(StatesGroup):
    waiting_for_id = State()


class RemoveAdminStates(StatesGroup):
    waiting_for_id = State()


# Admin management handlers
@router.message(F.text == "Admin qo'shish")
async def add_admin_command(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = AdminRepository(session)
        if repo.is_admin(message.from_user.id):
            await message.answer(
                "Yangi adminning Telegram ID sini yuboring:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.set_state(AddAdminStates.waiting_for_id)
        else:
            await message.answer('Bu buyruq faqat adminlar uchun')

@router.message(AddAdminStates.waiting_for_id)
async def process_add_admin(message: types.Message, state: FSMContext):
    try:
        new_admin_id = int(message.text)
        async with AsyncSessionLocal() as session:
            repo = AdminRepository(session)
            user_repo = UserRepository(session)

            # Check if user exists
            user = await user_repo.get_user(new_admin_id)
            if not user:
                await message.answer("Bu ID ga ega foydalanuvchi topilmadi!\n\nIltimos boshqa id qo'shing yoki /admin kamandani berib asosiy menuga qayting")
                return

            # Add admin
            await repo.add_admin(new_admin_id, message.from_user.username)
            await message.answer(
                f"✅ Yangi admin qo'shildi (ID: {new_admin_id})",
                reply_markup=admin_panel()
            )
            await state.clear()
    except Exception as err:
        await message.answer("Iltimos, faqat raqam bilan bazada mavjud bo'lmagan foydalanuvhci id raqamini yuboring!")

@router.message(F.text == "Adminlar ro'yxati")
async def get_admins_list(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = AdminRepository(session)
        admins = await repo.get_all_admins()

        if not admins:
            await message.answer("Adminlar ro'yxati bo'sh!")
            return

        admins_list = "\n".join([f"{admin.telegram_id}" for admin in admins])
        await message.answer(
            f"Adminlar ro'yxati:\n{admins_list}"
        )
@router.message(F.text == "Admin o'chirish")
async def remove_admin_command(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = AdminRepository(session)
        admins = await repo.get_all_admins()

        if not admins:
            await message.answer("Adminlar ro'yxati bo'sh!")
            return

        admins_list = "\n".join([f"{admin.telegram_id}" for admin in admins])
        await message.answer(
            f"Adminlar ro'yxati:\n{admins_list}\n\nO'chirish uchun ID ni yuboring:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(RemoveAdminStates.waiting_for_id)


@router.message(RemoveAdminStates.waiting_for_id)
async def process_remove_admin(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text)
        async with AsyncSessionLocal() as session:
            repo = AdminRepository(session)
            success = await repo.remove_admin(admin_id)

            if success:
                await message.answer(
                    f"✅ Admin o'chirildi (ID: {admin_id})",
                    reply_markup=admin_panel()
                )
            else:
                await message.answer("Bunday ID ga ega admin topilmadi!")
    except ValueError:
        await message.answer("Iltimos, faqat raqam yuboring!")
    finally:
        await state.clear()


@router.message(F.text == "dropppp_users")
async def drop_users_table(message: types.Message):
    # Only allow admins to execute this command
    async with AsyncSessionLocal() as session:
        admin_repo = AdminRepository(session)
        if not await admin_repo.is_admin(message.from_user.id):
            await message.answer("❌ Only admins can execute this command!")
            return

    try:
        engine = create_async_engine(AsyncSessionLocal().bind.url)

        async with engine.begin() as conn:
            # Drop the users table
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            await message.answer("✅ Users table dropped successfully!")

            # Recreate the users table
            await conn.run_sync(Base.metadata.create_all, tables=[User.__table__])
            await message.answer("✅ Users table recreated successfully!")

    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")
    finally:
        await engine.dispose()


from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile
from database.repositories import UserRepository
from database.base import AsyncSessionLocal

@router.message(F.text == "🗂 Hujjatlarni ko‘rish")
async def ask_for_user_id(message: types.Message, state: FSMContext):
    await message.answer("Foydalanuvchining Telegram ID raqamini yuboring:")
    await state.set_state(CheckDocsState.waiting_for_telegram_id)


@router.message(CheckDocsState.waiting_for_telegram_id)
async def send_user_docs(message: types.Message, state: FSMContext):
    try:
        telegram_id = int(message.text)
    except ValueError:
        await message.answer("Noto‘g‘ri format! Faqat raqamlardan iborat Telegram ID yuboring.")
        return

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_user(telegram_id)

    if not user:
        await message.answer("Bu Telegram ID bo‘yicha foydalanuvchi topilmadi.")
        await state.clear()
        return

    # Passport
    if user.passport and user.passport != "pasport_olaman":
        await message.answer_document(user.passport, caption="🛂 Pasport fayli")
    else:
        await message.answer("🛂 Pasport mavjud emas.")

    # Attestat
    if user.attestat:
        await message.answer_document(user.attestat, caption="📜 Attestat fayli")
    else:
        await message.answer("📜 Attestat mavjud emas.")

    await state.clear()

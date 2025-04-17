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
        "Al-buxoriy nomidagi Dorululum Dorulfununi Turkiyada 10 yil mobaynida faoliyat qilib kelmoqda. Muhammadodil Hamid tomonlaridan tashkil qilingan ushbu dargohda qanday uslubda va nimalardan dars o’tilishini ko’rib chiqamiz.\n\n1-kursda katta e’tiborni arab tiliga beriladi. 1 yil ichida arab tilida kamida B2 darajasigacha o’qitiladi chunki undan keyingi yillarda darslar faqat arab tilida bo’lgani va barcha mo’tabar kitoblar arab tilida bo’lgani uchun bu tilni yaxshi darajada o’rganishingiz kerak bo’ladi. Bunga qo’shimcha tariqasida boshlang’ich fiqh va aqida fanlari ham o’qitiladi.\n\n2-kursda\n\nFiqh\nAqida\nTafsir\nQur’on (yodlash)\nTajvid, maqom\nXitoba (notiqlik san’ati)\nSiyrat\nXadis\nSahobalar tarixi\nSarf\nNahv\n\nFanlari o’tiladi\n\n3-kursda yuqoridagi fanlar va Usuli fiqh\n\nMustalah ul-hadis mantiq fanlari qo’shiladi\n\n4-kursda shu fanlarga chuqur yondashilinadi va shu dasturga islom moliyasi fani ham qo’shiladi.\n\nTelefonlar hafta davomida yeg’ib olinadi talaba darslariga yanada yaxshiroq e’tibor qaratishi uchun ijtimoiy tarmoq va gadjetlardan uzoq tutiladi. Hafta oxiri kunlari telefonlari qaytarib beriladi.\n\nDorululum - farzandingiz eng yaxshisiga loyiq.\n\n<a href='https://www.instagram.com/buxoriy_dorululum?igsh=MXg1cHdtN2Z5MW8zOA=='>Instagram</a> | <a href='https://t.me/dorululumofficial'>Telegram</a>"
    )
    await message.answer(text,parse_mode="HTML")
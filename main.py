import asyncio
from aiogram import Bot, Dispatcher
from handlers import user, admin, application
from database.base import init_db
from config import Config
from database.repositories import AdminRepository
from database.base import AsyncSessionLocal


async def main():
    await init_db()

    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    # Include routers
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(application.router)
    async with AsyncSessionLocal() as session:
        repo = AdminRepository(session)
        user_admin = await repo.get_admin(935795577)
    if not user_admin:
        await repo.create_admin(935795577)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Admin


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int):
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalars().first()

    async def get_all_users(self):
        result = await self.session.execute(
            select(User)
        )
        return result.scalars().all()

    async def create_user(self, telegram_id: int):
        user = User(telegram_id=telegram_id)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update_user(self, telegram_id: int, **kwargs):
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(**kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_admin(self, telegram_id: int):
        result = await self.session.execute(
            select(Admin).where(Admin.telegram_id == telegram_id)
        )
        return result.scalars().first() is not None

    async def get_all_users(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def create_admin(self, telegram_id: int):
        admin = Admin(telegram_id=telegram_id)
        self.session.add(admin)
        await self.session.commit()
        return admin

    async def get_admin(self, telegram_id: int):
        result = await self.session.execute(
            select(Admin).where(Admin.telegram_id == telegram_id)
        )
        return result.scalars().first()

    async def add_admin(self, telegram_id: int, username: str = None):
        admin = Admin(telegram_id=telegram_id, username=username)
        self.session.add(admin)
        await self.session.commit()
        return admin

    async def remove_admin(self, telegram_id: int) -> bool:
        stmt = delete(Admin).where(Admin.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount and result.rowcount > 0

    async def get_all_admins(self):
        result = await self.session.execute(select(Admin))
        return result.scalars().all()

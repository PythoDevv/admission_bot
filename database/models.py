from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime,BigInteger
from database.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    full_name = Column(String)
    birth_date = Column(String)
    phone = Column(String)
    telegram_username = Column(String)
    passport = Column(String)
    attestat = Column(String)
    motivation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
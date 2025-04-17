from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
import sys
import os
from alembic import context

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.base import Base
from database.models import User, Admin
from config import Config

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = f"postgresql+asyncpg://{Config.DB_CONFIG['user']}:{Config.DB_CONFIG['password']}@{Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}/{Config.DB_CONFIG['database']}"
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_async_engine(
        f"postgresql+asyncpg://{Config.DB_CONFIG['user']}:{Config.DB_CONFIG['password']}@{Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}/{Config.DB_CONFIG['database']}"
    )

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(
                lambda sync_conn: context.configure(
                    connection=sync_conn,
                    target_metadata=target_metadata
                )
            )
            await connection.run_sync(lambda conn: context.run_migrations())

    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
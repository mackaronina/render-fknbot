from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import uuid4

from asyncpg import Connection
from sqlalchemy import BigInteger, func, JSON
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


engine = create_async_engine(
    settings.db.get_url(),
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "connection_class": CConnection,
    }
)
# 'sqlite+aiosqlite:///db.sqlite3'
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    type_annotation_map = {
        dict[str, Any]: JSON
    }
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str]
    toxic_level: Mapped[int] = mapped_column(default=1)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str]
    toxic_level: Mapped[int] = mapped_column(default=1)
    today_toxic_level: Mapped[int] = mapped_column(default=1)
    max_toxic_percent: Mapped[float] = mapped_column(default=0)
    max_toxic_text: Mapped[str | None]
    reactions_count: Mapped[dict[str, Any] | None]


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def connection(method: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> Any:
        async with async_session() as session:
            try:
                result = await method(*args, session=session, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e

    return wrapper

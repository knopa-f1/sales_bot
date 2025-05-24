from datetime import datetime

from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

from db.connection import Database


async def register_models() -> None:
    async with Database().engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Base(AsyncAttrs, DeclarativeBase): # pylint: disable=too-few-public-methods
    __abstract__ = True

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False, default=func.now())
    # updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False, default=func.now(),
    #                                              onupdate=func.now())

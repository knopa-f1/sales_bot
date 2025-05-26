from sqlalchemy import select
from db.models import User
from db.connection import database


async def save_user(chat_id: int, name: str):
    async with database.session as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

        if user:
            if user.name != name:
                user.name = name
        else:
            user = User(chat_id=chat_id, name=name)
            session.add(user)

        await session.commit()


async def get_user_by_chat_id(chat_id: int) -> User | None:
    async with database.session as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        return result.scalar_one_or_none()
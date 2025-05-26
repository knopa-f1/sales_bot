import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.connection import database
from db.models import Cart
from db.requests.users import get_user_by_chat_id

logger = logging.getLogger(__name__)


async def add_to_cart(chat_id: int, product_id: int, count: int):
    async with database.session as session:
        user = await get_user_by_chat_id(session, chat_id)

        if not user:
            logger.error("Пользователь с chat_id=%s не найден при добавлении в корзину", chat_id)
            return

        result = await session.execute(
            select(Cart).where(Cart.user_id == user.id, Cart.product_id == product_id)
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:
            cart_item.count = count
        else:
            cart_item = Cart(user_id=user.id, product_id=product_id, count=count)
            session.add(cart_item)

        await session.commit()



async def remove_from_cart(chat_id: int, product_id: int):
    async with database.session as session:
        user = await get_user_by_chat_id(session, chat_id)

        if not user:
            return

        result = await session.execute(
            select(Cart).where(Cart.user_id == user.id, Cart.product_id == product_id)
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:
            await session.delete(cart_item)
            await session.commit()


async def get_cart_items(chat_id: int):
    async with database.session as session:
        user = await get_user_by_chat_id(session, chat_id)

        if not user:
            return [], 0

        result = await session.execute(
            select(Cart)
            .options(selectinload(Cart.product))
            .where(Cart.user_id == user.id)
        )
        cart_items = result.scalars().all()

        total = sum(float(item.product.price) * item.count for item in cart_items)
        return cart_items, total

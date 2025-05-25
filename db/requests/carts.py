from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload

from db.models import Cart, User
from db.connection import database


async def add_to_cart(chat_id: int, product_id: int, count: int):
    async with database.session as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"Пользователь с chat_id={chat_id} не найден")

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

async def remove_from_cart(user_id: int, product_id: int):
    async with database.session as session:
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:
            if cart_item.count > 1:
                cart_item.count -= 1
            else:
                await session.delete(cart_item)

            await session.commit()


async def get_cart_items(chat_id: int):
    async with database.session as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

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

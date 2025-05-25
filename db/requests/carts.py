from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload

from db.models import Cart
from db.connection import database


async def add_to_cart(user_id: int, product_id: int):
    async with database.session as session:
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:
            cart_item.count += 1
        else:
            cart_item = Cart(user_id=user_id, product_id=product_id, count=1)
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

async def get_cart_items(user_id: int):
    async with database.session as session:
        result = await session.execute(
            select(Cart)
            .options(selectinload(Cart.product))
            .where(Cart.user_id == user_id)
        )
        cart_items = result.scalars().all()

        total = 0
        for item in cart_items:
            subtotal = float(item.product.price) * item.count
            total += subtotal

        return cart_items, total
import logging

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from db.models import User, Cart, Order, OrderItem
from db.connection import database
from decimal import Decimal


logger = logging.getLogger(__name__)

async def create_order_from_cart(chat_id: int, address: str) -> Order:
    async with database.session as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.error(f"Пользователь с chat_id={chat_id} не найден")

        result = await session.execute(
            select(Cart).where(Cart.user_id == user.id).options(selectinload(Cart.product))
        )
        cart_items = result.scalars().all()
        if not cart_items:
            logger.error(f"Корзина пуста, chat_id={chat_id}")

        total = sum(Decimal(item.product.price) * item.count for item in cart_items)

        order = Order(
            user_id=user.id,
            amount=total,
            address=address,
            transaction_id="",
            status="unpaid"
        )
        session.add(order)
        await session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                count=item.count,
                amount=Decimal(item.product.price) * item.count
            )
            session.add(order_item)

        await session.execute(
            delete(Cart).where(Cart.user_id == user.id)
        )

        await session.commit()
        await session.refresh(order)
        return order

async def mark_order_as_paid(order_id: int, transaction_id: str):
    async with database.session as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            logger.error(f"Заказ с id={order_id} не найден")

        order.status = "paid"
        order.transaction_id = transaction_id

        await session.commit()


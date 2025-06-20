import logging
from decimal import Decimal

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from db.connection import database
from db.models import Cart, Order, OrderItem
from db.requests.users import get_user_by_chat_id

logger = logging.getLogger(__name__)


async def create_order_from_cart(chat_id: int, address: str) -> Order:
    async with database.session as session:
        user = await get_user_by_chat_id(session, chat_id)
        if not user:
            logger.error("Пользователь с chat_id=%s не найден", chat_id)

        result = await session.execute(
            select(Cart).where(Cart.user_id == user.id).options(selectinload(Cart.product))
        )
        cart_items = result.scalars().all()
        if not cart_items:
            logger.error("Корзина пуста, chat_id=%s", chat_id)

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
            logger.error("Заказ с id=%s не найден", order_id)

        order.status = "paid"
        order.transaction_id = transaction_id

        await session.commit()

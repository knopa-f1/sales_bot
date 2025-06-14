import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    BigInteger, ForeignKey, Integer, String, Text, DECIMAL, Table, Column, Enum, DateTime
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.base_model import Base


class Catalog(Base): # pylint: disable=too-few-public-methods
    __tablename__ = 'bot_admin_catalog'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('bot_admin_catalog.id'))

    parent: Mapped[Optional["Catalog"]] = relationship(
        "Catalog", remote_side=[id], backref="subcategories"
    )


class Product(Base): # pylint: disable=too-few-public-methods
    __tablename__ = 'bot_admin_product'

    id: Mapped[int] = mapped_column(primary_key=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_catalog.id'))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String)  # путь к изображению
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))

    catalog: Mapped["Catalog"] = relationship("Catalog", backref="products")


class User(Base): # pylint: disable=too-few-public-methods
    __tablename__ = 'bot_admin_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(255))


class Cart(Base): # pylint: disable=too-few-public-methods
    __tablename__ = 'bot_admin_cart'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_user.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_product.id'))
    count: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship("User", backref="cart_items")
    product: Mapped["Product"] = relationship("Product")


class Order(Base): # pylint: disable=too-few-public-methods
    __tablename__ = 'bot_admin_order'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_user.id'))
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    address: Mapped[str] = mapped_column(Text)
    transaction_id: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))

    user: Mapped["User"] = relationship("User", backref="orders")


class OrderItem(Base): # pylint: disable=too-few-public-methods
    __tablename__ = 'bot_admin_orderitem'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_order.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_product.id'))
    count: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))

    order: Mapped["Order"] = relationship("Order", backref="items")
    product: Mapped["Product"] = relationship("Product")


class BroadcastStatus(PyEnum):
    pending = "pending"
    sent = "sent"
    error = "error"


broadcast_recipients = Table(
    "bot_admin_broadcast_recipients",
    Base.metadata,
    Column("broadcast_id", ForeignKey("bot_admin_broadcast.id"), primary_key=True),
    Column("user_id", ForeignKey("bot_admin_user.id"), primary_key=True)
)


class Broadcast(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "bot_admin_broadcast"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Enum(BroadcastStatus), default=BroadcastStatus.pending)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.UTC))
    sent_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    recipients: Mapped[list["User"]] = relationship(
        "User",
        secondary=broadcast_recipients,
        backref="broadcasts"
    )

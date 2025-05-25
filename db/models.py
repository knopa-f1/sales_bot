from sqlalchemy import (
    BigInteger, ForeignKey, Integer, String, Text, DECIMAL
)

from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional

from db.base_model import Base

class Catalog(Base):
    __tablename__ = 'bot_admin_catalog'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('bot_admin_catalog.id'))

    parent: Mapped[Optional["Catalog"]] = relationship(
        "Catalog", remote_side=[id], backref="subcategories"
    )


class Product(Base):
    __tablename__ = 'bot_admin_product'

    id: Mapped[int] = mapped_column(primary_key=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_catalog.id'))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String)  # путь к изображению
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))

    catalog: Mapped["Catalog"] = relationship("Catalog", backref="products")


class User(Base):
    __tablename__ = 'bot_admin_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(255))


class Cart(Base):
    __tablename__ = 'bot_admin_cart'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_user.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_product.id'))
    count: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship("User", backref="cart_items")
    product: Mapped["Product"] = relationship("Product")


class Order(Base):
    __tablename__ = 'bot_admin_order'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_user.id'))
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    address: Mapped[str] = mapped_column(Text)
    transaction_id: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))

    user: Mapped["User"] = relationship("User", backref="orders")


class OrderItem(Base):
    __tablename__ = 'bot_admin_orderitem'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_order.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('bot_admin_product.id'))
    count: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))

    order: Mapped["Order"] = relationship("Order", backref="items")
    product: Mapped["Product"] = relationship("Product")

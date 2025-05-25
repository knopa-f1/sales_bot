from db.requests.carts import get_cart_items


def format_cart_message(cart_items, total) -> str:
    if not cart_items:
        return "🛒 Ваша корзина пуста."

    lines = ["🛒 <b>Ваша корзина:</b>\n"]

    for item in cart_items:
        name = item.product.name
        price = float(item.product.price)
        count = item.count
        subtotal = price * count
        lines.append(f"• {name} — {count} x {price:.2f} ₽ = <b>{subtotal:.2f} ₽</b>")

    lines.append(f"\n<b>Итого:</b> {total:.2f} ₽")

    return "\n".join(lines)

def format_order_confirmation_message(order) -> str:
    return (
        f"✅ <b>Заказ №{order.id}</b> успешно оформлен!\n\n"
        f"💰 Сумма: <b>{order.amount:.2f} ₽</b>\n"
        f"📦 Доставка по адресу:\n<pre>{order.address}</pre>\n\n"
    )

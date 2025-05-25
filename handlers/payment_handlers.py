import logging

from aiogram.enums import ContentType
from aiogram.types import Message, SuccessfulPayment, PreCheckoutQuery
from aiogram import Router

from db.requests.orders import mark_order_as_paid

router = Router()

logger = logging.getLogger(__name__)

@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(lambda msg: msg.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message):
    payment = message.successful_payment

    payload = payment.invoice_payload
    total_amount = payment.total_amount / 100
    currency = payment.currency
    telegram_transaction_id = payment.telegram_payment_charge_id
    provider_transaction_id = payment.provider_payment_charge_id

    if payload.startswith("order_"):
        order_id = int(payload.split("_")[1])
        await mark_order_as_paid(order_id, transaction_id=provider_transaction_id)
        logger.info(f"Order {order_id} has been paid")
        await message.answer(
            text=f"✅ Оплата успешна!\n"
            f"Заказ #{order_id} на сумму {total_amount:.2f} {currency} оплачен.\n"
            f"Спасибо за покупку!",
            parse_mode = "HTML"
        )
    else:
        await message.answer("Платёж принят, но не удалось определить заказ.")

import logging
from datetime import datetime

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.types import Message, PreCheckoutQuery

from db.requests.orders import mark_order_as_paid
from lexicon.lexicon import LEXICON_RU
from services.utils import append_payment_to_excel

router = Router()

logger = logging.getLogger(__name__)


@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot):
    logger.info("Поступило подтверждение оплаты %s",pre_checkout_query.id)
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(lambda msg: msg.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message):
    payment = message.successful_payment

    payload = payment.invoice_payload
    total_amount = payment.total_amount / 100
    currency = payment.currency
    provider_transaction_id = payment.provider_payment_charge_id

    if payload.startswith("order_"):
        order_id = int(payload.split("_")[1])
        await mark_order_as_paid(order_id, transaction_id=provider_transaction_id)
        logger.info("Заказ %s оплачен", order_id)

        await append_payment_to_excel(
            order_id=order_id,
            user_id=message.chat.id,
            username=message.from_user.full_name,
            amount=total_amount,
            currency=currency,
            provider_tx_id=provider_transaction_id,
            timestamp=datetime.now()
        )

        await message.answer(
            text=f"Оплата успешна!\n"
                 f"Заказ #{order_id} на сумму {total_amount:.2f} {currency} оплачен.\n"
                 f"Спасибо за покупку!",
            parse_mode="HTML"
        )
    else:
        logger.warning("Заказ с payload %s оплачен, но не удалось разобрать номер.", payload)
        await message.answer(LEXICON_RU['error_payment'])

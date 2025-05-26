import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import PreCheckoutQuery, SuccessfulPayment, Message
from handlers.payment_handlers import handle_pre_checkout_query, process_successful_payment


@pytest.mark.asyncio
async def test_pre_checkout_query_ok():
    mock_query = MagicMock(spec=PreCheckoutQuery)
    mock_query.id = "test_query_123"
    mock_bot = MagicMock()
    mock_bot.answer_pre_checkout_query = AsyncMock()

    await handle_pre_checkout_query(mock_query, mock_bot)

    mock_bot.answer_pre_checkout_query.assert_called_once_with("test_query_123", ok=True)

@pytest.mark.asyncio
@patch("handlers.payment_handlers.mark_order_as_paid", new_callable=AsyncMock)
@patch("handlers.payment_handlers.append_payment_to_excel", new_callable=AsyncMock)
async def test_successful_payment(mock_excel, mock_paid):
    mock_payment = MagicMock(spec=SuccessfulPayment)
    mock_payment.invoice_payload = "order_42"
    mock_payment.total_amount = 9900
    mock_payment.currency = "RUB"
    mock_payment.telegram_payment_charge_id = "tg_tx_001"
    mock_payment.provider_payment_charge_id = "prv_tx_001"

    mock_chat = MagicMock()
    mock_chat.id = 123456789

    mock_from_user = MagicMock()
    mock_from_user.full_name = "Тестовый Юзер"

    mock_message = MagicMock(spec=Message)
    mock_message.chat = mock_chat
    mock_message.from_user = mock_from_user
    mock_message.content_type = "successful_payment"
    mock_message.successful_payment = mock_payment
    mock_message.answer = AsyncMock()

    await process_successful_payment(mock_message)

    mock_paid.assert_awaited_once_with(42, transaction_id="prv_tx_001")
    mock_excel.assert_awaited_once()
    mock_message.answer.assert_called_once()


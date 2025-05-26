from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from aiogram import Bot
from aiogram.types import Message

from handlers.user_handlers import process_start_command, process_help_command
from db.requests.users import get_user_by_chat_id
from lexicon.lexicon import LEXICON_RU


@patch("handlers.user_handlers.save_user", new_callable=AsyncMock)
@patch("db.requests.users.get_user_by_chat_id", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_start_command_creates_user(mock_get_user, mock_save_user):
    mock_chat = MagicMock()
    mock_chat.id = 123456789

    mock_from_user = MagicMock()
    mock_from_user.full_name = "Тестовый Юзер"

    mock_message = MagicMock(spec=Message)
    mock_message.chat = mock_chat
    mock_message.from_user = mock_from_user
    mock_message.answer = AsyncMock()

    mock_bot = MagicMock(spec=Bot)

    mock_get_user.return_value = MagicMock(name="UserMock", name_field="Тестовый Юзер")

    await process_start_command(mock_message, mock_bot)

    mock_save_user.assert_called_once_with(chat_id=123456789, name="Тестовый Юзер")
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_help_command_sends_text():
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()

    await process_help_command(mock_message)

    mock_message.answer.assert_called_once_with(text=LEXICON_RU['/help'])

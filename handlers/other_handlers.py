from aiogram import Router
from aiogram.types import Message

from keyboards.inline_keyboards import start_keyboard
from lexicon.lexicon import LEXICON_RU


router = Router()


# any commands, except "/start" и "/help"
@router.message()
async def send_message(message: Message):
    keyboard = start_keyboard()
    await message.reply(text=LEXICON_RU["no_answer"],
                        reply_markup=keyboard)

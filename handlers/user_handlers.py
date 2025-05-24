import os
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Document, Message, CallbackQuery

from config_data.constants import page_size
from db.requests import get_paginated_categories, get_subcategories_by_category
from lexicon.lexicon import LEXICON_RU

from keyboards.inline_keyboards import start_keyboard, category_keyboard, pagination_keyboard, subcategory_keyboard
from services.utils import get_selected_data, get_selected_data_subcat

router = Router()

KEYBOARD = start_keyboard()

@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=start_keyboard()
    )

@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.edit_text(text=LEXICON_RU['/help'])

@router.callback_query(F.data == 'button_catalog')
async def process_button_catalog(callback: CallbackQuery):
    categories, count = await get_paginated_categories(page=1, page_size=page_size)
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, 1, count))

@router.callback_query(F.data.startswith('button_cat_choose_page'))
async def process_button_cat_choose_page(callback: CallbackQuery):
    page_number = int(get_selected_data(callback.data))
    categories, count = await get_paginated_categories(page=page_number, page_size=page_size)
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, page_number, count))

@router.callback_query(F.data.startswith('button_current_cat'))
async def process_button_current_cat(callback: CallbackQuery):
    category_id = int(get_selected_data(callback.data))
    subcategories, count = await get_subcategories_by_category(category_id, page=1, page_size=page_size)
    await callback.message.edit_text(text=LEXICON_RU['choose_subcategory'], reply_markup=subcategory_keyboard(subcategories, category_id, 1, count))

@router.callback_query(F.data.startswith('button_subcat_choose_page'))
async def process_button_subcat_choose_page(callback: CallbackQuery): #TODO объединить с методом выше
    page_number, category_id = get_selected_data_subcat(callback.data)
    subcategories, count = await get_subcategories_by_category(int(category_id), page=int(page_number), page_size=page_size)
    await callback.message.edit_text(text=LEXICON_RU['choose_subcategory'], reply_markup=subcategory_keyboard(subcategories, int(category_id), int(page_number), count))
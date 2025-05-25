import os
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Document, Message, CallbackQuery, InputMediaPhoto, BufferedInputFile, FSInputFile

from config_data import config
from config_data.config import config_settings
from db.requests import get_paginated_categories, get_subcategories_by_category, get_products_by_catalog
from lexicon.lexicon import LEXICON_RU

from keyboards.inline_keyboards import start_keyboard, category_keyboard, subcategory_keyboard, \
    product_keyboard
from services.utils import ButtonCallbackParams

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

@router.callback_query(F.data == 'button-catalog')
async def process_button_catalog(callback: CallbackQuery):
    categories, count = await get_paginated_categories(page=1)
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, 1, count))

@router.callback_query(F.data.startswith('button-cat-page'))
async def process_button_cat_choose_page(callback: CallbackQuery):
    button_info = ButtonCallbackParams.from_callback(callback.data)
    categories, count = await get_paginated_categories(page=button_info['page'])
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, button_info.page, count))

@router.callback_query(F.data.startswith('button-cur-cat') | F.data.startswith('button-subcat-page'))
async def process_subcategory_navigation(callback: CallbackQuery):
    button_info = ButtonCallbackParams.from_callback(callback.data)
    subcategories, count = await get_subcategories_by_category(button_info.cat, page=button_info.page)

    await callback.message.edit_text(
        text=LEXICON_RU['choose_subcategory'],
        reply_markup=subcategory_keyboard(subcategories, button_info.cat, button_info.page, count)
    )

@router.callback_query(F.data.startswith('button-cur-subcat') | F.data.startswith('button-product-page'))
async def process_product_navigation(callback: CallbackQuery):
    button_info= ButtonCallbackParams.from_callback(callback.data)

    product, count = await get_products_by_catalog(button_info.subcat, page=button_info.page)
    if not product:
        await callback.answer(LEXICON_RU['no_products'])
        return

    image_path = config_settings.db.image_path + product.image
    input_file = FSInputFile(image_path, filename="product.jpg")

    media = InputMediaPhoto(
        media=input_file,
        caption=f"<b>{product.name}</b>\n\n{product.description}\n\nЦена: {product.price} ₽",
        parse_mode="HTML"
    )

    await callback.message.edit_media(
        media,
        reply_markup=product_keyboard(product, button_info.subcat, button_info.page, count)
    )

@router.callback_query(F.data.startswith('button-start-menu'))
async def process_button_start_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['/start'],
        reply_markup=start_keyboard()
    )

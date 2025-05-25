from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile

from keyboards.callback_factories import ProductsCallbackFactory
from config_data.config import config_settings
from db.requests.categories_products import get_paginated_categories, get_subcategories_by_category, get_products_by_catalog
from db.requests.users import save_user
from lexicon.lexicon import LEXICON_RU

from keyboards.inline_keyboards import start_keyboard, category_keyboard, subcategory_keyboard, \
    product_keyboard

router = Router()

KEYBOARD = start_keyboard()

@router.message(CommandStart())
async def process_start_command(message: Message):
    await save_user(
        chat_id=message.chat.id,
        name=message.from_user.full_name
    )

    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=start_keyboard()
    )

@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.edit_text(text=LEXICON_RU['/help'])

@router.callback_query(F.data.startswith('button-catalog'))
async def process_button_catalog(callback: CallbackQuery):
    categories, count = await get_paginated_categories(page=1)
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, 1, count))

@router.callback_query(ProductsCallbackFactory.filter(F.button_name=='cat-page'))
async def process_category_navigation(callback: CallbackQuery, callback_data: ProductsCallbackFactory):
    categories, count = await get_paginated_categories(page=callback_data.page_id)
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, callback_data.page_id, count))

@router.callback_query(ProductsCallbackFactory.filter(F.button_name == 'cur-cat'))
@router.callback_query(ProductsCallbackFactory.filter(F.button_name == 'subcat-page'))
async def process_subcategory_navigation(callback: CallbackQuery, callback_data: ProductsCallbackFactory):
    subcategories, count = await get_subcategories_by_category(callback_data.category_id, page=callback_data.page_id)

    keyboard = subcategory_keyboard(subcategories, callback_data.category_id, callback_data.page_id, count)

    if callback.message.content_type != ContentType.TEXT:
        await callback.message.delete()
        await callback.message.answer(
            text=LEXICON_RU['choose_subcategory'],
            reply_markup=keyboard
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_RU['choose_subcategory'],
            reply_markup=keyboard
        )

# @router.callback_query(ProductsCallbackFactory.filter(F.button_name=='subcat-page'))
# async def process_subcategory_navigation(callback: CallbackQuery, callback_data: ProductsCallbackFactory):
#     subcategories, count = await get_subcategories_by_category(callback_data.category_id, page=callback_data.page_id)
#
#     keyboard = subcategory_keyboard(subcategories, callback_data.category_id, callback_data.page_id, count)
#
#     if callback.message.content_type != ContentType.TEXT:
#         await callback.message.delete()
#         await callback.message.answer(
#             text=LEXICON_RU['choose_subcategory'],
#             reply_markup=keyboard
#         )
#     else:
#         await callback.message.edit_text(
#             text=LEXICON_RU['choose_subcategory'],
#             reply_markup=keyboard
#         )

@router.callback_query(ProductsCallbackFactory.filter(F.button_name=='cur-subcat'))
@router.callback_query(ProductsCallbackFactory.filter(F.button_name=='product-page'))
async def process_product_navigation(callback: CallbackQuery, callback_data: ProductsCallbackFactory):
    product, count = await get_products_by_catalog(callback_data.subcategory_id, page=callback_data.page_id)
    if not product:
        await callback.answer(text=LEXICON_RU['no_products'])
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
        reply_markup=product_keyboard(product, callback_data.category_id, callback_data.subcategory_id, callback_data.page_id, count)
    )

@router.callback_query(F.data == 'button-start-menu')
async def process_button_back_to_start_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['/start'],
        reply_markup=start_keyboard()
    )

# @router.callback_query(F.data == 'button-add-cart')
# async def process_button_upload(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(text=LEXICON_RU['input_count'])
#     await state.set_state(UploadExcel.waiting_for_file)


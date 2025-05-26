import logging

from aiogram import Router, F, Bot
from aiogram.enums import ContentType, ChatMemberStatus
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile, LabeledPrice

from db.requests.carts import add_to_cart, get_cart_items, remove_from_cart
from db.requests.orders import create_order_from_cart
from keyboards.callback_factories import ProductsCallbackFactory, CartCallbackFactory
from config_data.config import config_settings
from db.requests.categories_products import get_paginated_categories, get_subcategories_by_category, get_products_by_catalog
from db.requests.users import save_user
from lexicon.lexicon import LEXICON_RU

from keyboards.inline_keyboards import start_keyboard, category_keyboard, subcategory_keyboard, \
    product_keyboard, add_to_cart_keyboard, cart_keyboard, check_subscription_keyboard
from services.utils import format_cart_message, format_order_confirmation_message
from states.states import AddToCart, PayTheCart

router = Router()

KEYBOARD = start_keyboard()

STATES = [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def process_start_command(message: Message, bot: Bot):

    await save_user(
        chat_id=message.chat.id,
        name=message.from_user.full_name
    )

    try:
        member = await bot.get_chat_member(chat_id=config_settings.tg_bot.required_channel, user_id=message.chat.id)
        if member.status not in STATES:
            await message.answer(LEXICON_RU['error_unsubscribe_channel'],
                                 reply_markup=check_subscription_keyboard())
            return
    except Exception as e:
        logger.error(e)
        await message.answer(LEXICON_RU['error_check_channel'])
        return

    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=start_keyboard()
    )

@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

@router.callback_query(F.data.startswith("button-check-subscription"))
async def check_subscription(callback: CallbackQuery, bot: Bot):
    try:
        member = await bot.get_chat_member(chat_id=config_settings.tg_bot.required_channel, user_id=callback.message.chat.id)
        if member.status in STATES:
            await callback.message.edit_text(
                text=LEXICON_RU['/start'],
                reply_markup=start_keyboard()
            )
        else:
            text = LEXICON_RU['error_unsubscribe']
            if callback.message.text != text:
                await callback.message.edit_text(text,
                                             reply_markup=check_subscription_keyboard())
            else:
                return
    except Exception as e:
        logger.error(e)
        await callback.message.edit_text(LEXICON_RU['error_check_channel'])
        return

@router.callback_query(F.data.startswith('button-catalog'))
async def process_button_catalog(callback: CallbackQuery):
    categories, count = await get_paginated_categories(page=1)
    await callback.message.edit_text(text=LEXICON_RU['choose_category'], reply_markup=category_keyboard(categories, 1, count))

@router.callback_query(F.data.startswith('button-cart'))
async def process_button_cart(callback: CallbackQuery):
    cart_items, total = await get_cart_items(callback.message.chat.id)
    await callback.message.edit_text(text=format_cart_message(cart_items, total),
                                     parse_mode="HTML",
                                     reply_markup=cart_keyboard(cart_items))

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

@router.callback_query(ProductsCallbackFactory.filter(F.button_name=='input_count'))
async def process_button_input_count(callback: CallbackQuery, callback_data: ProductsCallbackFactory, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON_RU['input_count'],
        # reply_markup=keyboard
    )
    await state.update_data(item_id=callback_data.item_id,
                            category_id=callback_data.category_id,
                            subcategory_id=callback_data.subcategory_id)
    await state.set_state(AddToCart.waiting_count)


@router.message(StateFilter(AddToCart.waiting_count),
                lambda x: x.text.isdigit() and 0 < int(x.text))
async def process_count_sent(message: Message, state: FSMContext):
    await state.update_data(count=int(message.text))
    state_data = await state.get_data()
    await message.answer(
        text=LEXICON_RU['add_to_cart'],
        reply_markup=add_to_cart_keyboard(state_data)
    )
    await state.clear()

@router.message(StateFilter(AddToCart.waiting_count))
async def warning_count(message: Message):
    await message.answer(
        text=LEXICON_RU['error_incorrect_count']
    )

@router.callback_query(ProductsCallbackFactory.filter(F.button_name=='add-cart'))
async def process_button_approve_cart(callback: CallbackQuery, callback_data: ProductsCallbackFactory):
    await add_to_cart(callback.message.chat.id, callback_data.item_id, callback_data.count)
    await process_button_cart(callback)

@router.callback_query(CartCallbackFactory.filter(F.button_name=='del-item'))
async def process_button_del_item(callback: CallbackQuery, callback_data: CartCallbackFactory):
    await remove_from_cart(callback.message.chat.id, callback_data.item_id)
    await process_button_cart(callback)


@router.callback_query(F.data.startswith('button-input-address'))
async def process_button_input_address(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['input_address'],
    )
    await state.set_state(PayTheCart.waiting_address)

@router.message(StateFilter(PayTheCart.waiting_address))
async def process_address_sent(message: Message, state: FSMContext, bot: Bot):
    order = await create_order_from_cart(message.chat.id, message.text)

    await state.clear()

    prices = [LabeledPrice(label="К оплате", amount=int(order.amount * 100))]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title=f"Заказ №{order.id}",
        description=format_order_confirmation_message(order),
        payload=f"order_{order.id}",
        provider_token=config_settings.tg_bot.yukassa_token,
        currency="RUB",
        prices=prices,
        start_parameter="test"
    )

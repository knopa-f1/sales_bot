from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.config import config_settings
from config_data.constants import PAGE_SIZE
from keyboards.callback_factories import ProductsCallbackFactory, CartCallbackFactory
from lexicon.lexicon import LEXICON_BUTTONS_RU


def create_inline_kb(width: int,
                     *args: str,
                     last_row: Optional[dict[str, str]] = None,
                     **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON_BUTTONS_RU[button] if button in LEXICON_BUTTONS_RU else button,
                callback_data=button
            ))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    kb_builder.row(*buttons, width=width)

    if last_row:
        last_buttons = [
            InlineKeyboardButton(
                text=LEXICON_BUTTONS_RU.get(text, text),
                callback_data=callback_data
            ) for callback_data, text in last_row.items()
        ]
        kb_builder.row(*last_buttons)

    return kb_builder.as_markup()


def start_keyboard():
    return create_inline_kb(3, 'button-catalog', 'button-cart')


def category_keyboard(categories, page_number, count):
    buttons = {ProductsCallbackFactory(button_name='cur-cat', category_id=cat.id).pack(): cat.name for cat in
               categories}

    last_row = {}
    if page_number > 1:
        last_row[ProductsCallbackFactory(button_name='cat-page', page_id=page_number - 1).pack()] = (
            LEXICON_BUTTONS_RU)["button-back"]

    last_row['button-start-menu'] = LEXICON_BUTTONS_RU["button-step-back"]

    if page_number * PAGE_SIZE < count:
        last_row[ProductsCallbackFactory(button_name='cat-page', page_id=page_number + 1).pack()] = (
            LEXICON_BUTTONS_RU)["button-forward"]

    return create_inline_kb(2, last_row=last_row, **buttons)


def subcategory_keyboard(subcategories, category_id, page_number, count):
    buttons = {
        ProductsCallbackFactory(button_name='cur-subcat', category_id=category_id, subcategory_id=subcat.id).pack():
            subcat.name for subcat in subcategories}
    last_row = {}
    if page_number > 1:
        last_row[ProductsCallbackFactory(button_name='subcat-page', category_id=category_id,
                                         page_id=page_number - 1).pack()] = LEXICON_BUTTONS_RU["button-back"]

    last_row['button-catalog'] = LEXICON_BUTTONS_RU["button-step-back"]

    if page_number * PAGE_SIZE < count:
        last_row[ProductsCallbackFactory(button_name='subcat-page', category_id=category_id,
                                         page_id=page_number + 1).pack()] = LEXICON_BUTTONS_RU["button-forward"]

    return create_inline_kb(2, last_row=last_row, **buttons)


def product_keyboard(product, category_id, subcategory_id, page_number, count):
    buttons = {}
    if page_number > 1:
        buttons[
            ProductsCallbackFactory(button_name='product-page', category_id=category_id, subcategory_id=subcategory_id,
                                    page_id=page_number - 1).pack()] = LEXICON_BUTTONS_RU["button-back"]

    buttons[ProductsCallbackFactory(button_name='subcat-page', category_id=category_id,
                                    subcategory_id=subcategory_id).pack()] = \
        LEXICON_BUTTONS_RU["button-step-back"]

    buttons[ProductsCallbackFactory(button_name='input_count', item_id=product.id).pack()] = \
        LEXICON_BUTTONS_RU["button-add-cart"]

    if page_number < count:
        buttons[
            ProductsCallbackFactory(button_name='product-page', category_id=category_id, subcategory_id=subcategory_id,
                                    page_id=page_number + 1).pack()] = LEXICON_BUTTONS_RU["button-forward"]

    return create_inline_kb(4, **buttons)


def add_to_cart_keyboard(state_data):
    buttons = {
        'button-catalog': LEXICON_BUTTONS_RU["button-decline-add-cart"],
        ProductsCallbackFactory(button_name='add-cart', item_id=state_data['item_id'],
                                count=state_data['count']).pack():
            LEXICON_BUTTONS_RU[
                "button-approve-add-cart"]}
    return create_inline_kb(2, **buttons)


def cart_keyboard(cart_items):
    buttons = {
        CartCallbackFactory(button_name='del-item', item_id=item.product_id).pack():
            LEXICON_BUTTONS_RU["button-del-item"] + item.product.name for item in cart_items}

    cart_size = len(cart_items)
    last_row = {'button-catalog': LEXICON_BUTTONS_RU["button-catalog"]}
    if cart_size > 0:
        last_row['button-input-address'] = LEXICON_BUTTONS_RU["button-input-address"]

    return create_inline_kb(1, last_row=last_row, **buttons)


def check_subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS_RU["button-go-to-channel"],
                              url=f"https://t.me/{config_settings.tg_bot.required_channel.lstrip('@')}")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS_RU["button-check-subscription"],
                              callback_data="button-check-subscription")]
    ])

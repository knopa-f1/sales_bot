from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.config import config_settings
from keyboards.callback_factories import ProductsCallbackFactory, PaymentCallbackFactory
from config_data.constants import PAGE_SIZE
from lexicon.lexicon import LEXICON_BUTTONS_RU


def create_inline_kb(width: int,
                     *args: str,
                     last_btn: str | None = None,
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
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON_BUTTONS_RU[last_btn] if button in LEXICON_BUTTONS_RU else last_btn,
            callback_data=last_btn
        ))

    return kb_builder.as_markup()

def start_keyboard():
    return create_inline_kb(3, 'button-catalog', 'button-cart', 'button-faq')

def category_keyboard(categories, page_number, count):
    buttons = {ProductsCallbackFactory(button_name='cur-cat', category_id=cat.id).pack(): cat.name for cat in categories}
    if page_number > 1:
        buttons[ProductsCallbackFactory(button_name='cat-page',page_id=page_number-1).pack()] = (
            LEXICON_BUTTONS_RU)["button-back"]

    buttons['button-start-menu'] = LEXICON_BUTTONS_RU["button-step-back"]

    if page_number*PAGE_SIZE < count:
        buttons[ProductsCallbackFactory(button_name='cat-page',page_id=page_number+1).pack()] = (
            LEXICON_BUTTONS_RU)["button-forward"]

    return create_inline_kb(2, **buttons)


def subcategory_keyboard(subcategories, category_id, page_number, count):
    buttons = {ProductsCallbackFactory(button_name='cur-subcat', category_id=category_id, subcategory_id=subcat.id).pack():
                                        subcat.name for subcat in subcategories}

    if page_number > 1:
        buttons[ProductsCallbackFactory(button_name='subcat-page',category_id=category_id,
                                     page_id=page_number-1).pack()] = LEXICON_BUTTONS_RU["button-back"]

    buttons['button-catalog'] = LEXICON_BUTTONS_RU["button-step-back"]

    if page_number*PAGE_SIZE < count:
        buttons[ProductsCallbackFactory(button_name='subcat-page', category_id=category_id,
                                     page_id=page_number+1).pack()] = LEXICON_BUTTONS_RU["button-forward"]

    return create_inline_kb(2, **buttons)

def product_keyboard(product, category_id, subcategory_id, page_number, count):
    buttons = {}
    if page_number > 1:
        buttons[ProductsCallbackFactory(button_name='product-page', category_id=category_id, subcategory_id=subcategory_id,
                                     page_id=page_number-1).pack()] = LEXICON_BUTTONS_RU["button-back"]

    buttons[ProductsCallbackFactory(button_name='subcat-page', category_id=category_id, subcategory_id=subcategory_id).pack()] =\
                                    LEXICON_BUTTONS_RU["button-step-back"]

    buttons[ProductsCallbackFactory(button_name='input_count', item_id=product.id).pack()] = \
        LEXICON_BUTTONS_RU["button-add-cart"]

    if page_number < count:
        buttons[ProductsCallbackFactory(button_name='product-page', category_id=category_id, subcategory_id=subcategory_id,
                                 page_id=page_number+1).pack()] = LEXICON_BUTTONS_RU["button-forward"]
    return create_inline_kb(2, **buttons)

def add_to_cart_keyboard(state_data):
    buttons = {
        ProductsCallbackFactory(button_name='button-catalog').pack(): LEXICON_BUTTONS_RU["button-decline-add-cart"],
        ProductsCallbackFactory(button_name='add-cart', item_id=state_data['item_id'], count=state_data['count']).pack():
            LEXICON_BUTTONS_RU[
                "button-approve-add-cart"]}
    return create_inline_kb(2, **buttons)

def cart_keyboard():
    return create_inline_kb(3, 'button-catalog', 'button-input-address')

def check_subscription():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS_RU["button-go-to-channel"], url=f"https://t.me/{config_settings.tg_bot.required_channel.lstrip('@')}")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS_RU["button-check-subscription"], callback_data="button-check-subscription")]
    ])

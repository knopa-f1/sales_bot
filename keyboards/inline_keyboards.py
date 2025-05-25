import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.constants import PAGE_SIZE
from lexicon.lexicon import LEXICON_BUTTONS_RU
from services.utils import ButtonCallbackParams


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
    buttons = {ButtonCallbackParams('button-cur-cat', cat.id).to_json_string(): cat.name for cat in categories}
    if page_number > 1:
        buttons[ButtonCallbackParams('button-cat-page',page=page_number-1).to_json_string()] = (
            LEXICON_BUTTONS_RU)["button-back"]

    buttons[ButtonCallbackParams('button-start-menu').to_json_string()] = LEXICON_BUTTONS_RU["button-step-back"]

    if page_number*PAGE_SIZE < count:
        buttons[ButtonCallbackParams('button-cat-page',page=page_number+1).to_json_string()] = (
            LEXICON_BUTTONS_RU)["button-forward"]

    return create_inline_kb(2, **buttons)

# def category_keyboard(categories, page_number, count):
#     buttons = {f'button-current-cat_cat:{cat.id}':cat.name for cat in categories}
#     if page_number > 1:
#         buttons[f'button-cat-choose-page_page:{page_number-1}'] = LEXICON_BUTTONS_RU["button-back"]
#     buttons[f'button-start-menu'] = LEXICON_BUTTONS_RU["button-step-back"]
#     if page_number*PAGE_SIZE < count:
#         buttons[f'button-cat-choose-page_page:{page_number+1}'] = LEXICON_BUTTONS_RU["button-forward"]
#     return create_inline_kb(2, **buttons)

def subcategory_keyboard(subcategories, category_id, page_number, count):
    buttons = {ButtonCallbackParams('button-cur-subcat', subcat=subcat.id).to_json_string():
                                        subcat.name for subcat in subcategories}

    if page_number > 1:
        buttons[ButtonCallbackParams('button-subcat-page',cat=category_id,
                                     page=page_number-1).to_json_string()] = LEXICON_BUTTONS_RU["button-back"]

    if page_number*PAGE_SIZE < count:
        buttons[ButtonCallbackParams('button-subcat-page', cat=category_id,
                                     page=page_number+1).to_json_string()] = LEXICON_BUTTONS_RU["button-forward"]

    return create_inline_kb(2, **buttons)

def product_keyboard(product, subcategory_id, page_number, count):
    buttons = {}
    if page_number > 1:
        buttons[ButtonCallbackParams('button-product-page', subcat=subcategory_id,
                                     page=page_number-1).to_json_string()] = LEXICON_BUTTONS_RU["button-back"]
    if page_number < count:
        buttons[ButtonCallbackParams('button-product-page', subcat=subcategory_id,
                                 page=page_number+1).to_json_string()] = LEXICON_BUTTONS_RU["button-forward"]
    return create_inline_kb(2, **buttons)
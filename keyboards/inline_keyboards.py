from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.constants import page_size
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
    return create_inline_kb(3, 'button_catalog', 'button_cart', 'button_faq')

def pagination_keyboard(type_, categories, page_number, count):
    buttons = {
        f'button_current_{type_}_{cat.id}': cat.name for cat in categories
    }

    if page_number > 1:
        buttons[f'button_{type_}_choose_page_{page_number - 1}'] = LEXICON_BUTTONS_RU["button_back"]
    if page_number * page_size < count:
        buttons[f'button_{type_}_choose_page_{page_number + 1}'] = LEXICON_BUTTONS_RU["button_forward"]

    return create_inline_kb(2, **buttons)

def category_keyboard(categories, page_number, count):
    buttons = {f'button_current_cat_{cat.id}':cat.name for cat in categories}
    if page_number > 1:
        buttons[f'button_cat_choose_page_{page_number-1}'] = LEXICON_BUTTONS_RU["button_back"]
    if page_number*page_size < count:
        buttons[f'button_cat_choose_page_{page_number+1}'] = LEXICON_BUTTONS_RU["button_forward"]
    return create_inline_kb(2, **buttons)

def subcategory_keyboard(subcategories, category_id, page_number, count):
    buttons = {f'button_current_subcat_{subcat.id}':subcat.name for subcat in subcategories}
    if page_number > 1:
        buttons[f'button_subcat_choose_page_{category_id}_{page_number-1}'] = LEXICON_BUTTONS_RU["button_back"]
    if page_number*page_size < count:
        buttons[f'button_subcat_choose_page_{category_id}_{page_number+1}'] = LEXICON_BUTTONS_RU["button_forward"]
    return create_inline_kb(2, **buttons)
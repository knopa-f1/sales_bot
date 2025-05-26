from aiogram.filters.callback_data import CallbackData


class ProductsCallbackFactory(CallbackData, prefix='button'):
    button_name: str
    category_id: int|None = None
    subcategory_id: int|None = None
    item_id: int|None = None
    page_id: int = 1
    count: int|None = None

class CartCallbackFactory(CallbackData, prefix='cart'):
    button_name: str
    item_id: int|None = None

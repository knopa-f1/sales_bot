from aiogram.fsm.state import StatesGroup, State

class AddToCart(StatesGroup):# pylint: disable=too-few-public-methods
    waiting_count = State()

class PayTheCart(StatesGroup):# pylint: disable=too-few-public-methods
    waiting_address = State()

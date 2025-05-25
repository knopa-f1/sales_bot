from aiogram.fsm.state import StatesGroup, State

class AddToCard(StatesGroup):# pylint: disable=too-few-public-methods
    waiting_count = State()

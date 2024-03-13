from typing import Literal

from aiogram.filters.callback_data import CallbackData


class BlackJackCallback(CallbackData, prefix='BJ'):
    """
    game_number: int \n
    move: Literal['take', 'stand']
    """
    game_number: int
    move: Literal['take', 'stand']

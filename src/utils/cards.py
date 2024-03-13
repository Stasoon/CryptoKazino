import random
from dataclasses import dataclass
from typing import Generator, Any


@dataclass
class Card:
    """
    Параметры:
    value: str
    suit: str
    """
    value: str
    suit: str

    @staticmethod
    def get_existing_suits() -> tuple:
        """ Возвращает возможные масти карт """
        return "Ч", "Б", "П", "К"

    @staticmethod
    def get_existing_values() -> tuple:
        """ Возвращает возможные значения карт """
        return *[str(i) for i in range(2, 10 + 1)], "В", "Д", "К", "Т"


def get_shuffled_deck(decks_count: int = 1) -> Generator[Card, Any, Any]:
    """
    Возвращает генератор (колоду) с объектами Card.  \n
    decks_count - сколько колод использовать \n
    """
    deck = [
        Card(value, suit)
        for value in Card.get_existing_values()
        for suit in Card.get_existing_suits()
    ] * decks_count
    random.shuffle(deck)

    return (card for card in deck)


def get_random_card():
    suit = random.choice(Card.get_existing_suits())
    value = random.choice(Card.get_existing_values())
    return Card(value, suit)

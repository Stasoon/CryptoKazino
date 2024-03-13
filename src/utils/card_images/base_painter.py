import io
from abc import ABC, abstractmethod
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from aiogram.types import BufferedInputFile

from settings import Config
from src.database import Game


class _GameImagePainter(ABC):
    def __init__(self, game: Game):
        self.game = game

        self.draw: ImageDraw = None
        self.table: Image = None
        self.table_size: Tuple[int, int] = (0, 0)

        self.card_size: tuple[int, int] = (180, 277)

    def _draw_header(self, game_name: str):
        baccarat_text = f"{game_name} №{self.game.number}"
        header_font = ImageFont.truetype("resources/fonts/font.otf", 55)
        header_pos = (self.table_size[0] // 2, self.table_size[1] // 9 + 50)

        self.draw.text(
            xy=header_pos, text=baccarat_text,
            fill=(0, 0, 0, 220), font=header_font,
            align='center', anchor='mm'
        )

    async def _draw_card(self, card_file_name: str, xy: tuple[int, int]):
        with Image.open(f'{Config.Games.CARD_IMAGES_PATH}/{card_file_name}.png') as card_img:
            card_img = card_img.resize(self.card_size)
            self.table.paste(card_img, xy, card_img)

    def _get_buffered_file_from_generated_photo(self):
        img_buffer = io.BytesIO()
        self.table.save(img_buffer, format='PNG')
        image_bytes = img_buffer.getvalue()
        buffered_image = BufferedInputFile(image_bytes, filename=f'Результаты игры №{self.game.number}')
        img_buffer.close()
        return buffered_image

    @abstractmethod
    def get_image(self) -> BufferedInputFile:
        ...

from core import GameObject
import pygame


class Platform(GameObject):
    """Абстрактный класс для создания платформ"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=False):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

    def update(self, scroll: int):
        """метод для обновления спрайта"""
        self.scroll(scroll)
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.rect.y += offset

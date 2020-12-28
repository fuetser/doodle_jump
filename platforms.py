from core import StaticGameObject
import pygame


class Platform(StaticGameObject):
    """Абстрактный класс для создания платформ"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)
        self.item = None

    def update(self, scroll: int):
        """метод для обновления спрайта"""
        self.scroll(scroll)
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.rect.y += offset

    def add_item(self, item: pygame.sprite.Sprite):
        """метод для добавления предмета к платформе"""
        if isinstance(item, pygame.sprite.Sprite) and self.item is None:
            self.item = item
        else:
            raise TypeError("Wrong argument supplied")

from core import GameObject
import pygame


class GameItem(GameObject):
    """Абстрактный класс для игрового предмета"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=False):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

    def activate(self, player: pygame.sprite.Sprite):
        """метод для применения эффекта предмета игроку"""
        raise NotImplementedError

    def update(self, scroll: int):
        """метод для обновления спрайта"""
        self.scroll(scroll)
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига предмета вниз по экрану"""
        self.rect.y += offset


class Spring(GameItem):
    """Класс для создания пружин"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=False):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

    def activate(self, player: pygame.sprite.Sprite):
        player.add_momentum(-5)

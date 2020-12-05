from core import GameObject
import pygame


class Platform(GameObject):
    """Абстрактный класс для создания платформ"""

    def __init__(self, x_pos: int, y_pos: int, image_path: str):
        super(Platform, self).__init__(x_pos, y_pos)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

    def draw(self, win):
        """метод для отрисовки"""
        win.blit(self.image, self.pos)
        self.update_rect()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.y += offset

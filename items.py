from core import GameObject
import pygame


class GameItem(GameObject):
    """Абстрактный класс для игрового предмета"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=False):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

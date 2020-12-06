from core import GameObject
import pygame


class Enemy(GameObject):
    """Абстрактный класс для противника"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=False):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

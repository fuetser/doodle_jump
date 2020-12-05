from core import GameObject
import pygame


class GameItem(GameObject):
    """Абстрактный класс для игрового предмета"""

    def __init__(self, x_pos: int, y_pos: int):
        super(GameItem, self).__init__(x_pos, y_pos)

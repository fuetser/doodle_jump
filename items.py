from core import GameObject
import pygame


class GameItem(GameObject):
    def __init__(self, x_pos: int, y_pos: int):
        super(GameItem, self).__init__(x_pos, y_pos)

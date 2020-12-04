from core import GameObject
import pygame


class Platform(GameObject):
    def __init__(self, x_pos: int, y_pos: int):
        super(Platform, self).__init__(x_pos, y_pos)

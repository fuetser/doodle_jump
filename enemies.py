from core import GameObject
import pygame


class Enemy(GameObject):
    def __init__(self, x_pos: int, y_pos: int):
        super(Enemy, self).__init__(x_pos, y_pos)

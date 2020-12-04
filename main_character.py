from core import GameObject
import pygame


class MainCharacter(GameObject):
    def __init__(self, x_pos: int, y_pos: int, image_path: str):
        super(MainCharacter, self).__init__(x_pos, y_pos)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

from core import GameObject
import pygame


class MainCharacter(GameObject):
    """Класс для создания главного персонажа"""

    def __init__(self, x_pos: int, y_pos: int, image_path: str):
        super(MainCharacter, self).__init__(x_pos, y_pos)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.v_momentum = 0  # текущее горизонтальное ускорение
        self.gravity_ratio = 0.2  # сила гравитации

    def move_h(self, offset: int):
        """метод для перемещения персонажа по горизонтали
            и появления с другой стороны при выходе за границы экрана"""
        self.x += offset
        if self.x + offset > 600:
            self.x = -self.width
        elif self.x + offset < -self.width:
            self.x = 600

    def move_v(self):
        """метод для обработки гравитации"""
        self.v_momentum += self.gravity_ratio
        if self.y > 600 - self.height:
            # self.v_momentum = 0
            pass
        self.y += self.v_momentum

    def jump(self):
        """метод для прыжка от платформы"""
        # self.y -= 5
        self.v_momentum = -5

    def draw(self, win: pygame.Surface):
        """метод для отрисовки и применения гравитации"""
        win.blit(self.image, self.pos)
        self.move_v()
        self.update_rect()

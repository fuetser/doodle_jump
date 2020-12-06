from core import GameObject
import pygame


class MainCharacter(GameObject):
    """Класс для создания главного персонажа"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=False):
        super().__init__(x, y, image_path, screen_size, convert_alpha)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.v_momentum = 0  # текущее горизонтальное ускорение
        self.gravity_ratio = 0.2  # сила гравитации
        self.facing_right = False

    def move_h(self, offset: int):
        """метод для перемещения персонажа по горизонтали
            и появления с другой стороны при выходе за границы экрана"""
        self.rect.x += offset
        if self.rect.x + offset > 600:
            self.rect.x = -self.width
        elif self.rect.x + offset < -self.width:
            self.rect.x = 600
        self.flip_image(offset)

    def flip_image(self, direction: int):
        """метод для попворота персонажа в засимомти от направления движения"""
        if direction > 0 and not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = True
        elif direction < 0 and self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = False

    def move_v(self):
        """метод для обработки гравитации"""
        self.v_momentum += self.gravity_ratio
        if self.y > 600 - self.height:
            # self.v_momentum = 0
            pass
        self.rect.y += self.v_momentum

    def jump(self):
        """метод для прыжка от платформы"""
        # self.y -= 5
        self.v_momentum = -5

    def update(self):
        self.move_v()

    def draw(self, win):
        win.blit(self.image, self.rect)

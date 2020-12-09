from core import GameObject
from items import GameItem
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

    def process_collision(self, coll: pygame.sprite.Sprite):
        """метод для обработки столкновений"""
        if self.bottom >= coll.top and self.bottom <= coll.bottom:
            if isinstance(coll, GameItem):
                coll.activate(self)
            elif self.v_momentum > 1:
                self.rect.bottom = coll.rect.top
                self.jump()

    def move_v(self):
        """метод для обработки гравитации"""
        self.v_momentum += self.gravity_ratio
        if self.y > self.screen_height - self.height:
            self.v_momentum = 0
        self.rect.y += self.v_momentum

    def jump(self):
        """метод для прыжка от платформы"""
        self.v_momentum = -5

    def update(self):
        self.move_v()

    def draw(self, win):
        win.blit(self.image, self.rect)

    def add_momentum(self, amount: int):
        """метод для изменения ускорения игрока"""
        self.v_momentum += amount

from core import AnimatedGameObject
import os
import pygame


class Enemy(AnimatedGameObject):
    """Абстрактный класс для противника"""

    def __init__(self, x, y, images, screen_size, convert_alpha=True):
        super().__init__(x, y, images, screen_size, convert_alpha)
        self.horizontal_speed = 5
        self.hp = 100
        self.blood_colors = ((254, 132, 132), (254, 92, 92), (254, 32, 32),
                             (186, 0, 0), (107, 0, 0), (83, 0, 0))
        # self.colors = ((184, 2, 1), (254, 101, 23), (255, 132, 62),
        #                (132, 4, 3), (236, 16, 12))
        # self.colors = ((27, 2, 63), (0, 106, 249), (0, 192, 249),
        #                (220, 0, 254), (188, 0, 254), (83, 25, 251))
        # self.colors = ((103, 197, 10), (255, 217, 0), (124, 215, 194),
        #                (5, 78, 111), (20, 20, 20))

    def move_h(self):
        self.rect.x += self.horizontal_speed
        if self.x > self.screen_width or self.x < -self.rect.width:
            self.horizontal_speed *= -1

    def update(self, scroll: int):
        """метод для обновления спрайта"""
        super().update()
        self.move_h()
        self.scroll(scroll)
        if self.y > self.screen_height or self.hp <= 0:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.rect.y += offset

    def take_damage(self, damage: int):
        """метод для нанесения урона"""
        self.hp -= damage


class FlyingEye(Enemy):
    def __init__(self, x, y, screen_size):
        images = [f"assets/enemies/eye/{image}" for image in os.listdir(
            "assets/enemies/eye")]
        super().__init__(x, y, images, screen_size)
        self.sound = pygame.mixer.Sound("assets/sounds/monster_sound.wav")
        self.sound.set_volume(0.4)
        self.sound.play()
        self.sound_length = self.sound.get_length()
        self.sound_timer = self.sound_length

    def update(self, scroll: int):
        super().update(scroll)
        if self.sound_timer <= 0:
            self.sound.play()
            self.sound_timer = self.sound_length
        else:
            self.sound_timer -= 0.025

from core import AnimatedGameObject
from items import HoloCoin
import os
import pygame


class Enemy(AnimatedGameObject):
    """Абстрактный класс для противника"""
    sound = None
    damage_sound = None
    death_sound = None

    def __init__(self, x, y, images, screen_size, group, sound, volume,
                 ratio=1, convert_alpha=True):
        super().__init__(x, y, images, screen_size, convert_alpha)
        self.volume = volume
        self.volume_ratio = ratio
        self.__class__.load_sound(sound, volume, self.volume_ratio)
        self.sound_length = self.sound.get_length()
        self.sound_timer = 0
        self.sound_reload = 0.02
        self.group = group
        self.horizontal_speed = 4
        self.hp = 100
        self.reward = 50
        self.facing_right = True
        self.blood_colors = ((254, 132, 132), (254, 92, 92), (254, 32, 32),
                             (186, 0, 0), (107, 0, 0), (83, 0, 0))

    @classmethod
    def load_sound(cls, sound, volume, ratio):
        """метод для загрузки звука врага"""
        if cls.sound is None:
            cls.sound = pygame.mixer.Sound(sound)
            cls.sound.set_volume(min(volume * ratio, 1))
            cls.load_base_sounds(ratio)

    @classmethod
    def load_base_sounds(cls, ratio):
        """метод для загрузки звуков, общих для всех врагов"""
        if cls.damage_sound is None:
            cls.damage_sound = pygame.mixer.Sound(
                "assets/sounds/enemy_damage.wav")
            cls.damage_sound.set_volume(0.2 * ratio)
        if cls.death_sound is None:
            cls.death_sound = pygame.mixer.Sound(
                "assets/sounds/enemy_death.wav")
            cls.death_sound.set_volume(0.3 * ratio)

    def move_h(self):
        self.rect.x += self.horizontal_speed
        if self.x > self.screen_width or self.x < -self.rect.width:
            self.horizontal_speed *= -1

    def update(self, scroll: int):
        """метод для обновления спрайта"""
        super().update()
        self.move_h()
        self.scroll(scroll)
        self.play_sound(self.sound_reload)
        if self.y > self.screen_height or self.hp <= 0:
            self.delete()
        if self.horizontal_speed < 0 != self.facing_right:
            self.rotate_image()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.rect.y += offset

    def take_damage(self, damage: int):
        """метод для нанесения урона"""
        self.hp -= damage
        self.damage_sound.play()

    def play_sound(self, step: float):
        """метод для воспроизведения звука предмета"""
        if self.sound_timer <= 0:
            self.sound.play()
            self.sound_timer = self.sound_length
        else:
            self.sound_timer -= step

    def delete(self, spawn_coin=False):
        if self.hp <= 0 or spawn_coin:
            coin = HoloCoin(*self.rect.center,
                            (self.screen_width, self.screen_width),
                            price=self.reward)
            self.group.add(coin)
            self.death_sound.play()
        super().delete()

    def rotate_image(self):
        self.image = pygame.transform.flip(self.image, True, False)


class FlyingEye(Enemy):
    def __init__(self, x, y, screen_size, group, ratio):
        images = [f"assets/enemies/eye/{image}" for image in os.listdir(
            "assets/enemies/eye")]
        super().__init__(x, y, images, screen_size, group,
                         "assets/sounds/monster_sound.wav",
                         volume=0.4, ratio=ratio)
        self.hp = 200
        self.reward = 200
        self.facing_right = False
        self.sound_reload = 0.025


class Dragon(Enemy):
    """Класс для создания дракона"""

    def __init__(self, x, y, screen_size, group, ratio):
        images = [f"assets/enemies/dragon/{image}" for image in os.listdir(
            "assets/enemies/dragon") for _ in range(4)]
        super().__init__(x, y, images, screen_size, group,
                         "assets/sounds/dragon.wav", volume=0.2, ratio=ratio)
        self.horizontal_speed = 6
        self.reward = 300
        self.hp = 300


class Medusa(Enemy):
    """Класс для создания медузы"""

    def __init__(self, x, y, screen_size, group, ratio):
        images = [f"assets/enemies/medusa/{image}" for image in os.listdir(
            "assets/enemies/medusa") for _ in range(4)]
        super().__init__(x, y, images, screen_size, group,
                         "assets/sounds/medusa.wav", volume=0.2, ratio=ratio)
        self.horizontal_speed = 3
        self.blood_colors = ((103, 197, 10), (255, 217, 0), (124, 215, 194),
                             (5, 78, 111), (20, 20, 20))


class Gin(Enemy):
    """Класс для создания медузы"""

    def __init__(self, x, y, screen_size, group, ratio):
        images = [f"assets/enemies/gin/{image}" for image in os.listdir(
            "assets/enemies/gin") for _ in range(5)]
        super().__init__(x, y, images, screen_size, group,
                         "assets/sounds/gin.wav", volume=0.2, ratio=ratio)
        self.sound_reload = 0.03
        self.horizontal_speed = 5
        self.reward = 150
        self.hp = 150
        self.blood_colors = ((27, 2, 63), (0, 106, 249), (0, 192, 249),
                             (220, 0, 254), (188, 0, 254), (83, 25, 251))

from core import StaticGameObject
import pygame
import random


class Platform(StaticGameObject):
    """Абстрактный класс для создания платформ"""
    image = None

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        self.__class__.load_image(image_path, convert_alpha)
        super().__init__(
            x, y, image_path, screen_size, convert_alpha, load_image=False)
        self.item = None

    @classmethod
    def load_image(cls, image_path, convert_alpha):
        if cls.image is None:
            if convert_alpha:
                cls.image = pygame.image.load(image_path).convert_alpha()
            else:
                cls.image = pygame.image.load(image_path).convert()

    def activate(self, player: pygame.sprite.Sprite):
        """метод для обработки коллизии с игроком"""
        player.rect.bottom = self.top
        player.jump()

    def update(self, scroll: int):
        """метод для обновления спрайта"""
        self.scroll(scroll)
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.rect.y += offset

    def add_item(self, item: pygame.sprite.Sprite):
        """метод для добавления предмета к платформе"""
        if isinstance(item, pygame.sprite.Sprite) and self.item is None:
            self.item = item
        else:
            raise TypeError("Wrong argument supplied")


class StaticPlatform(Platform):
    """Класс для создания статичных платформ"""

    def __init__(self, x, y, screen_size):
        super().__init__(
            x, y, "assets/platforms/static_platform.png", screen_size)


class MovingPlatform(Platform):
    """Класс для создания движущихся платформ"""

    def __init__(self, x, y, screen_size):
        super().__init__(
            x, y, "assets/platforms/moving_platform.png", screen_size)
        self.horizontal_speed = 2

    def update(self, scroll: int):
        self.rect.x += self.horizontal_speed
        if self.x > self.screen_width or self.x < -self.rect.width:
            self.horizontal_speed *= -1
        super().update(scroll)


class BreakingPlatform(Platform):
    """Класс для создания разрушающихся платформ"""
    sound = None

    def __init__(self, x, y, screen_size):
        super().__init__(
            x, y, "assets/platforms/breaking_platform.png", screen_size)
        self.colors = ((210, 165, 109), (206, 139, 84), (189, 126, 74),
                       (150, 97, 61), (131, 80, 46))
        if self.__class__.sound is None:
            self.__class__.sound = pygame.mixer.Sound(
                "assets/sounds/platform_break.wav")
            self.__class__.sound.set_volume(0.55)

    def activate(self, player: pygame.sprite.Sprite):
        self.delete()
        self.sound.play()
        for _ in range(20):
            color = random.choice(self.colors)
            player.spawn_particles(amount=2, momentum=random.randrange(0, 3),
                                   radius=random.randrange(4, 10), color=color)

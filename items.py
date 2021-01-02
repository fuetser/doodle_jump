from core import AnimatedGameObject
import os
import pygame
import random


class GameItem(AnimatedGameObject):
    """Абстрактный класс для игрового предмета"""
    sound = None

    def __init__(self, x, y, images, screen_size, sound, volume, convert_alpha=True):
        super().__init__(x, y, images, screen_size, convert_alpha)
        self.__class__.load_sound(sound, volume)
        self.activated = False
        self.sound_length = self.sound.get_length()
        self.sound_timer = 0
        self.collect_with_item = False

    @classmethod
    def load_sound(cls, file, volume):
        if cls.sound is None:
            cls.sound = pygame.mixer.Sound(file)
            cls.sound.set_volume(volume)

    def activate(self, player: pygame.sprite.Sprite):
        """метод для применения эффекта предмета игроку"""
        pass

    def update(self, *args, **kwargs):
        """метод для обновления спрайта"""
        super().update(kwargs.get("skip_frames", 1))
        if args:
            self.scroll(args[0])
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига предмета вниз по экрану"""
        self.rect.y += offset


class FlyingGameItem(GameItem):
    """Абстрактный класс для создания летающих игровых объектов"""

    def __init__(self, x, y, images, screen_size, sound, volume,
                 convert_alpha=True, lifespan=120, speed=2):
        super().__init__(
            x, y, images, screen_size, sound, volume, convert_alpha)
        self.lifespan = lifespan
        self.speed = speed

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            # self.sound.play()
            player.enable_gravity(False)
            player.set_flying_object(self)
            self.activated = True

    def on_delete(self, player: pygame.sprite.Sprite):
        if self.activated:
            self.sound.stop()
            player.enable_gravity(True)
            player.set_flying_object()


class Spring(GameItem):
    """Класс для создания пружин"""

    def __init__(self, x, y, screen_size):
        images = ("assets/items/spring16_opened.png",
                  "assets/items/spring16.png")
        super().__init__(
            x, y, images, screen_size, "assets/sounds/spring.wav", volume=0.25)
        self.offset_made = False

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            self.sound.play()
            self.activated = True
            player.set_momentum(-10)
            player.spawn_particles()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.activated:
            self.image = self.static_image
            if not self.offset_made:
                self.rect.y -= self.rect.w // 2 + 15
                self.offset_made = True


class PropellerHat(FlyingGameItem):
    """Класс для создания шапки с пропеллером"""

    def __init__(self, x, y, screen_size, upgrade=None):
        images = ["assets/items/hat32.png"]
        images += [f"assets/items/hat/{image}" for image in os.listdir(
            "assets/items/hat")]
        speed = upgrade[0] if upgrade is not None else 2
        lifespan = upgrade[1] if upgrade is not None else 180
        super().__init__(x, y, images, screen_size, "assets/sounds/hat.wav",
                         volume=0.4, lifespan=lifespan, speed=speed)

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
            super().update(skip_frames=3)
            self.set_pos((player.x + 30 - 23 * player.facing_right,
                          player.y - 25))
            self.lifespan -= 1
            if self.sound_timer <= 0:
                self.sound.play()
                self.sound_timer = self.sound_length
            else:
                self.sound_timer -= 0.025
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)


class Trampoline(GameItem):
    """Класс для создания трамплина"""

    def __init__(self, x, y, screen_size):
        images = ["assets/items/trampoline64.png"] * 2
        super().__init__(x, y, images, screen_size,
                         "assets/sounds/trampoline.wav", volume=0.25)

    def activate(self, player: pygame.sprite.Sprite):
        self.sound.play()
        player.set_momentum(-15)
        player.spawn_particles()


class Jetpack(FlyingGameItem):
    """Класс для создание джетпака"""

    def __init__(self, x, y, screen_size, upgrade=None):
        images = ["assets/items/jetpack48.png"]
        images += [f"assets/items/jetpack/{image}" for image in os.listdir(
            "assets/items/jetpack")]
        speed = upgrade[0] if upgrade is not None else 3
        lifespan = upgrade[1] if upgrade is not None else 240
        super().__init__(x, y, images, screen_size, "assets/sounds/jetpack.wav",
                         volume=0.2, lifespan=lifespan, speed=speed)
        self.image = self.static_image
        self.facing_right = True

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
            super().update()
            self.rotate_image(player.facing_right)
            self.set_pos(
                (player.x + player.rect.w - 15 - player.rect.w * player.facing_right,
                 player.y + 5))
            self.spawn_particles(player)
            if self.sound_timer <= 0:
                self.sound.play()
                self.sound_timer = self.sound_length
            else:
                self.sound_timer -= 0.01
            self.lifespan -= 1
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)

    def rotate_image(self, player_facing_right):
        if self.facing_right != player_facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def spawn_particles(self, player: pygame.sprite.Sprite):
        color = random.choice(((255, 77, 0), (255, 157, 0), (255, 234, 0)))
        direction = -1 if player.facing_right else 1
        player.spawn_particles(player.x + player.rect.w - (
                               player.rect.w + 5) * player.facing_right + 8,
                               player.y + 50, color, amount=5,
                               direction=direction)


class Coin(GameItem):
    """Абстрактный класс для создания монеток"""

    def __init__(self, x, y, folder, screen_size, price, ignore_scroll=False):
        images = [f"{folder}/{image}" for image in os.listdir(folder)
                  for _ in range(3)]
        super().__init__(x, y, images, screen_size,
                         "assets/sounds/coin.wav", volume=0.3)
        self.price = price
        self.ignore_scroll = ignore_scroll
        self.is_magnetized = False
        self.speed_x = 0
        self.speed_y = 0
        self.speed_coefficient = 13
        self.collect_with_item = True

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            self.sound.play()
            self.activated = True
            player.add_money(self.price)
            self.delete()

    def update(self, *args, **kwargs):
        if not self.ignore_scroll:
            super().update(*args, **kwargs)
            if self.is_magnetized:
                self.rect.x -= self.speed_x
                self.rect.y -= self.speed_y
        else:
            super().update()

    def magnetize(self, pos_x, pos_y):
        """метод для передвижения монетки к игроку при примагничивании"""
        self.is_magnetized = True
        self.speed_x = int((self.x - pos_x) / self.speed_coefficient)
        self.speed_y = int((self.y - pos_y) / self.speed_coefficient)
        self.speed_coefficient = max(self.speed_coefficient - 0.125, 1)


class BronzeCoin(Coin):
    """Класс для создания бронзовых монеток"""

    def __init__(self, x, y, screen_size, ignore_scroll=False):
        # BronzeCoin.load_images(images, create_static=False)
        super().__init__(x, y, "assets/items/bronze_coin", screen_size,
                         price=1, ignore_scroll=ignore_scroll)


class SilverCoin(Coin):
    """Класс для создания серебрянных монеток"""

    def __init__(self, x, y, screen_size, ignore_scroll=False):
        super().__init__(x, y, "assets/items/silver_coin", screen_size,
                         price=5, ignore_scroll=ignore_scroll)


class GoldenCoin(Coin):
    """Класс для создания золотых монеток"""

    def __init__(self, x, y, screen_size, ignore_scroll=False):
        super().__init__(x, y, "assets/items/golden_coin", screen_size,
                         price=10, ignore_scroll=ignore_scroll)


class Shield(GameItem):
    """Класс для создания щита"""

    def __init__(self, x, y, screen_size, upgrade=None):
        images = ["assets/items/shield32.png"]
        images += [f"assets/items/shield/{image}" for image in os.listdir(
            "assets/items/shield") for _ in range(3)]
        super().__init__(x, y, images, screen_size,
                         "assets/sounds/shield.wav", volume=0.4)
        self.lifespan = upgrade if upgrade is not None else 240
        self.image = self.static_image
        self.collect_with_item = True

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            player.set_shield(self)
            self.activated = True

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
            super().update()
            self.rect.center = player.rect.center
            self.lifespan -= 1
            if self.sound_timer <= 0:
                self.sound.play()
                self.sound_timer = self.sound_length
            else:
                self.sound_timer -= 0.04
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)

    def on_delete(self, player: pygame.sprite.Sprite):
        if self.activated:
            player.set_shield()


class Magnet(GameItem):
    """Класс для создания магнита"""

    def __init__(self, x, y, screen_size, upgrade=None):
        images = ["assets/items/magnet32.png"]
        images += [f"assets/items/magnet/{image}" for image in os.listdir(
            "assets/items/magnet") for _ in range(2)]
        super().__init__(x, y, images, screen_size,
                         "assets/sounds/magnet.wav", volume=0.4)
        self.diameter = upgrade[0] if upgrade is not None else 150
        self.lifespan = upgrade[1] if upgrade is not None else 240
        self.image = self.static_image
        self.coverage_area = pygame.Rect(
            x - 100, y - 100, self.diameter, self.diameter)
        self.collect_with_item = True

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            player.set_magnet(self)
            self.activated = True

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
            super().update()
            self.rect.center = player.rect.center
            self.coverage_area.center = player.rect.center
            if self.sound_timer <= 0:
                self.sound.play()
                self.sound_timer = self.sound_length
            else:
                self.sound_timer -= 0.03
            self.lifespan -= 1
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)

    def on_delete(self, player: pygame.sprite.Sprite):
        if self.activated:
            player.set_magnet()

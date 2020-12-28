from core import AnimatedGameObject
import os
import pygame


class GameItem(AnimatedGameObject):
    """Абстрактный класс для игрового предмета"""

    def __init__(self, x, y, images, screen_size, convert_alpha=True):
        super().__init__(x, y, images, screen_size, convert_alpha)
        self.static_image = self.images.pop(0)
        self.frames_amount -= 1
        self.activated = False

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

    def __init__(self, x, y, images, screen_size, convert_alpha=True,
                 lifespan=120, speed=2):
        super().__init__(x, y, images, screen_size, convert_alpha)
        self.lifespan = lifespan
        self.speed = speed

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            player.enable_gravity(False)
            player.set_flying_object(self)
            self.activated = True

    def on_delete(self, player: pygame.sprite.Sprite):
        if self.activated:
            player.enable_gravity(True)
            player.set_flying_object()


class Spring(GameItem):
    """Класс для создания пружин"""

    def __init__(self, x, y, screen_size):
        images = ("assets/items/spring16_opened.png",
                  "assets/items/spring16.png")
        super().__init__(x, y, images, screen_size)
        self.offset_made = False

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            self.activated = True
            player.set_momentum(-10)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.activated:
            self.image = self.static_image
            if not self.offset_made:
                self.rect.y -= self.rect.w // 2 + 15
                self.offset_made = True


class PropellerHat(FlyingGameItem):
    """Класс для создания шапки с пропеллером"""

    def __init__(self, x, y, screen_size):
        images = ["assets/items/hat32.png"]
        images += [f"assets/items/hat/{image}" for image in os.listdir(
            "assets/items/hat")]
        super().__init__(x, y, images, screen_size, lifespan=180, speed=2)

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
            super().update(skip_frames=3)
            self.set_pos((player.x + 30 - 23 * player.facing_right,
                          player.y - 25))
            self.lifespan -= 1
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)


class Trampoline(GameItem):
    """Класс для создания трамплина"""

    def __init__(self, x, y, screen_size):
        images = ["assets/items/trampoline64.png"] * 2
        super().__init__(x, y, images, screen_size)

    def activate(self, player: pygame.sprite.Sprite):
        player.set_momentum(-15)


class Jetpack(FlyingGameItem):
    """Класс для создание джетпака"""

    def __init__(self, x, y, screen_size):
        images = ["assets/items/jetpack48.png"]
        images += [f"assets/items/jetpack/{image}" for image in os.listdir(
            "assets/items/jetpack")]
        super().__init__(x, y, images, screen_size, lifespan=240, speed=4)
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
            self.lifespan -= 1
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)

    def rotate_image(self, player_facing_right):
        if self.facing_right != player_facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            # self.facing_right = player_facing_right

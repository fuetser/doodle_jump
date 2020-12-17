from core import GameObject
import pygame


class GameItem(GameObject):
    """Абстрактный класс для игрового предмета"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

    def activate(self, player: pygame.sprite.Sprite):
        """метод для применения эффекта предмета игроку"""
        raise NotImplementedError

    def update(self, scroll: int, **kwargs):
        """метод для обновления спрайта"""
        self.scroll(scroll)
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига предмета вниз по экрану"""
        self.rect.y += offset


class Spring(GameItem):
    """Класс для создания пружин"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

    def activate(self, player: pygame.sprite.Sprite):
        player.set_momentum(-10)


class PropellerHat(GameItem):
    """Класс для создания шапки с пропеллером"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)
        self.speed = 2
        self.lifespan = 180
        self.activated = False

    def activate(self, player: pygame.sprite.Sprite):
        if not self.activated:
            player.enable_gravity(False)
            player.set_flying_object(self)
            self.activated = True

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
            self.set_pos((player.x + 30 - 23 * player.facing_right,
                          player.y - 15))
            self.lifespan -= 1
        if self.lifespan == 0 or self.y > self.screen_height:
            self.delete(player)

    def on_delete(self, player: pygame.sprite.Sprite):
        if self.activated:
            player.enable_gravity(True)
            player.set_flying_object()


class Trampoline(GameItem):
    """Класс для создания трамплина"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)

    def activate(self, player: pygame.sprite.Sprite):
        player.set_momentum(-15)


class Jetpack(PropellerHat):
    """Класс для создание джетпака"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)
        self.speed = 4
        self.lifespan = 240
        self.activated = False
        self.facing_right = True

    def update(self, *args, **kwargs):
        player = kwargs.get("player")
        if not self.activated:
            self.scroll(args[0])
        else:
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
            self.facing_right = player_facing_right

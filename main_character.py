from core import StaticGameObject, Group, Particle
from enemies import Enemy
from items import GameItem, Coin
import pygame
import random


class MainCharacter(StaticGameObject):
    """Класс для создания главного персонажа"""

    def __init__(self, x, y, image_path, screen_size, upgrade=None, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.v_momentum = 0  # текущее горизонтальное ускорение
        self.gravity_ratio = 0.2  # сила гравитации
        self.facing_right = False
        self.falling = True
        self.flying_object = None
        self.has_item = False
        self.game_over = False
        self.money_collected = 0
        self.shield = None
        self.magnet = None
        self.magnet_rect = None
        self.damage = upgrade if upgrade is not None else 40
        self.shoot_colors = (
            (187, 210, 102), (127, 163, 1), (70, 91, 0), (204, 221, 141))
        self.jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.jump_sound.set_volume(0.45)
        self.shoot_sound.set_volume(0.3)
        self.bullets = Group()
        self.particles = Group()

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
        scroll = True
        if isinstance(coll, GameItem):
            if coll.collect_with_item or not self.has_item:
                coll.activate(self)
        elif isinstance(coll, Enemy):
            if self.bottom > coll.top + 20 and self.shield is None:
                self.game_over = True
            else:
                coll.delete()
        elif self.bottom <= coll.top + 10 and not self.has_item:
            self.rect.bottom = coll.rect.top
            self.jump()
        elif self.bottom - 10 > coll.top and self.v_momentum > 0 and not self.has_item:
            scroll = False
        return scroll

    def process_magnet_collisions(self, group: Group):
        if self.magnet_rect is not None and self.magnet is not None:
            for coll in group.get_rect_collisions(self.magnet_rect):
                if isinstance(coll, Coin):
                    coll.magnetize(*self.pos)

    def move_v(self):
        """метод для обработки гравитации"""
        if self.falling:
            self.v_momentum += self.gravity_ratio
            if self.y > self.screen_height - self.height:
                self.v_momentum = 0
            self.rect.y += self.v_momentum
        if self.flying_object is not None:
            self.rect.y -= self.flying_object.speed

    def shoot(self, target_x: int, target_y: int):
        """метод для выстрела в определенном направлении"""
        x_pos = self.rect.right if self.facing_right else self.rect.left
        bullet = Bullet(x_pos - 10, self.y + 15, "assets/items/bullet.png",
                        (self.screen_width, self.screen_height))
        bullet.shoot(target_x, target_y)
        self.bullets.add(bullet)
        self.shoot_sound.play()
        self.spawn_explosion(x_pos, self.y + 15, self.shoot_colors)

    def calculate_bullets_collisions(self, coll: pygame.sprite.Sprite):
        """метод для обработки столкновений пуль с объектом"""
        if (collisions := self.bullets.get_collisions(coll)):
            coll.take_damage(self.damage)
            for collision in collisions:
                self.spawn_explosion(
                    *collision.pos, coll.blood_colors, radius=(2, 12))
                collision.delete()

    def jump(self):
        """метод для прыжка от платформы"""
        self.jump_sound.play()
        self.set_momentum(-5)
        for _ in range(20):
            self.spawn_particles(amount=1, radius=random.randrange(4, 10),
                                 momentum=random.randrange(0, 3))

    def update(self, enemy=None):
        print(len(self.particles))
        self.move_v()
        self.bullets.update()
        self.particles.update()
        if enemy is not None:
            self.calculate_bullets_collisions(enemy)

    def spawn_particles(self, x=None, y=None, color="white",
                        radius=8, amount=10, direction=None, momentum=3):
        direction = random.choice((-1, 1)) if direction is None else direction
        x = self.rect.center[0] if x is None else x
        y = self.bottom if y is None else y
        for _ in range(amount):
            self.particles.raw_add(Particle(x, y, radius, color,
                                            direction=direction,
                                            momentum=momentum))

    def spawn_explosion(self, x, y, colors, amount=2, radius=(2, 8),
                        repeat=25, momentum=4):
        """метод для спавна взрыва из частиц"""
        for _ in range(repeat):
            direction = random.choice((-1, 1))
            res_momentum = random.randrange(-momentum, momentum)
            res_radius = random.randint(*radius)
            color = random.choice(colors)
            self.spawn_particles(x, y, color, amount=amount, radius=res_radius,
                                 direction=direction, momentum=res_momentum)

    def draw(self, win: pygame.Surface):
        win.blit(self.image, self.rect)
        self.bullets.draw(win)
        self.particles.raw_draw(win)

    def add_momentum(self, amount: int):
        """метод для изменения ускорения игрока"""
        self.v_momentum += amount

    def set_momentum(self, new_momentum: int):
        """метод для установки ускорения падения"""
        self.v_momentum = new_momentum

    def enable_gravity(self, state: bool):
        """метод для отключения гравитации для игрока"""
        self.falling = state

    def set_flying_object(self, flying_object=None):
        """метод для добавления шапки/джетпака"""
        self.has_item = flying_object is not None
        self.flying_object = flying_object

    def add_money(self, money_to_add: int):
        """метод для добавления денег игроку при подборе монетки"""
        self.money_collected += money_to_add

    def get_collected_money(self) -> int:
        return self.money_collected

    def set_shield(self, shield=None):
        if self.shield is not None and shield is not None:
            self.shield.delete(self)
        self.shield = shield

    def set_magnet(self, magnet=None):
        if self.magnet is not None and magnet is not None:
            self.magnet.delete(self)
        self.magnet = magnet
        if magnet is not None:
            self.magnet_rect = magnet.coverage_area
        else:
            self.magnet_rect = None

    def reset(self):
        """метод для приведения атрибутов к дефолтному состоянию"""
        self.v_momentum = 0
        self.falling = True
        self.flying_object = None
        self.has_item = False
        self.game_over = False
        self.money_collected = 0
        self.shield = None
        self.magnet = None
        self.magent_rect = None
        self.bullets.clear()
        self.particles.clear()


class Bullet(StaticGameObject):
    """Класс для создания пули"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super().__init__(x, y, image_path, screen_size, convert_alpha)
        self.speed_x = 0
        self.speed_y = 0
        self.speed_coefficient = 10

    def shoot(self, target_x: int, target_y: int):
        """метод для старта полета пули в определенном направлении"""
        self.speed_x = int((self.x - target_x) / self.speed_coefficient)
        self.speed_y = int((self.y - target_y) / self.speed_coefficient)

    def update(self):
        self.rect.x -= self.speed_x
        self.rect.y -= self.speed_y
        condition1 = self.x > self.screen_width or self.y > self.screen_height
        condition2 = self.x < self.rect.width or self.x < self.rect.height
        if condition1 or condition2:
            self.delete()

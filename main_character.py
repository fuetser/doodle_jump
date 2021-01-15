from core import *
from enemies import Enemy
from items import GameItem, Coin
import os
import pygame
import random


class MainCharacter(AnimatedGameObject):
    """Класс для создания главного персонажа"""

    def __init__(self, x, y, screen_size, damage=None, reload_time=None, jump=None):
        images = [f"assets/character/{image}" for image in os.listdir(
            "assets/character")]
        super().__init__(x, y, images, screen_size, create_static=False)
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
        self.damage = damage if damage is not None else 35
        self.reload_time = reload_time if reload_time is not None else 90
        self.jum_height = jump if jump is not None else -4
        self.reload_timer = 0
        self.shoot_colors = (
            (187, 210, 102), (127, 163, 1), (70, 91, 0), (204, 221, 141))
        self.volume_ratio = 1
        self.jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.update_sound_volume()
        self.jump_sound.set_volume(0.45 * self.volume_ratio)
        self.shoot_sound.set_volume(0.3 * self.volume_ratio)
        self.bullets = Group()
        self.particles = Group()
        self.is_rotating = False
        self.current_rotation = 0
        self.item_pos = self.rect.center
        self.particles_coefficient = 1
        self.PARTICLES_KEY = "particles"

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
        if (direction > 0) != self.facing_right:
            self.images = tuple(map(
                lambda img: pygame.transform.flip(img, True, False),
                self.images))
            self.facing_right = not self.facing_right

    def process_collision(self, coll: pygame.sprite.Sprite):
        """метод для обработки столкновений"""
        scroll = True
        if isinstance(coll, GameItem):
            self.process_game_item(coll)
        elif isinstance(coll, Enemy):
            self.process_enemy(coll)
        elif self.v_momentum > 0 and not self.has_item:
            scroll = self.process_platform(coll)
        return scroll

    def process_game_item(self, coll: GameItem):
        """метод для обработки коллтзий с игровыми предметами"""
        if coll.collect_with_item or not (self.has_item or self.is_rotating):
            coll.activate(self)

    def process_enemy(self, coll: Enemy):
        """метод для обработки коллизий с врагами"""
        if self.bottom > coll.top + 20:
            self.game_over = self.shield is None
        elif self.v_momentum > 0:
            coll.delete(spawn_coin=True)

    def process_platform(self, coll):
        """метод для обработки коллизий с платформами"""
        scroll = True
        if self.bottom <= coll.top + 10:
            coll.activate(self)
        else:
            scroll = False
        return scroll

    def process_magnet_collisions(self, group: Group):
        """метод для обработки коллизий магнита с монетками"""
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
        if self.reload_timer == 0:
            x_pos = self.rect.right if self.facing_right else self.rect.left
            bullet = Bullet(x_pos - 10, self.y + 15, "assets/items/bullet.png",
                            (self.screen_width, self.screen_height))
            bullet.shoot(target_x, target_y)
            self.bullets.add(bullet)
            self.shoot_sound.play()
            self.spawn_explosion(x_pos, self.y + 15, self.shoot_colors)
            self.reload_timer = self.reload_time

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
        self.set_momentum(self.jum_height)
        for _ in range(20):
            self.spawn_particles(amount=1, radius=random.randrange(4, 10),
                                 momentum=random.randrange(0, 3))

    def update(self, enemy_group):
        self.move_v()
        self.bullets.update()
        self.particles.update()
        for enemy in enemy_group:
            self.calculate_bullets_collisions(enemy)
        if self.reload_timer > 0:
            self.reload_timer -= 1
        self.update_image()

    def update_image(self):
        """метод для обновления изображения игрока"""
        if self.is_rotating:
            self.current_rotation += 12
            if self.current_rotation > 360:
                self.is_rotating = False
        self.current_frame = int(self.v_momentum < 0)
        self.image = self.images[self.current_frame]

    def load_upgrades(self, damage=None, reload_time=None, jump=None):
        """метод для загрузки прокачки игрока при перезагрузке сцены"""
        self.damage = damage if damage is not None else 35
        self.reload_time = reload_time if reload_time is not None else 90
        self.jum_height = jump if jump is not None else -4

    def spawn_particles(self, x=None, y=None, color="white", radius=8,
                        amount=10, direction=None, momentum=3, lifespan=120):
        x = self.rect.center[0] if x is None else x
        y = self.bottom if y is None else y
        for _ in range(round(amount * self.particles_coefficient)):
            if direction is None:
                direction = random.choice((-1, 0, 1))
            self.particles.raw_add(Particle(x, y, radius, color,
                                            direction=direction,
                                            momentum=momentum,
                                            lifespan=lifespan))

    def spawn_explosion(self, x, y, colors, amount=2, radius=(2, 8),
                        repeat=25, momentum=4):
        """метод для спавна взрыва из частиц"""
        for _ in range(round(repeat * self.particles_coefficient)):
            res_momentum = random.randrange(-momentum, momentum)
            res_radius = random.randint(*radius)
            color = random.choice(colors)
            self.spawn_particles(x, y, color, amount=amount, radius=res_radius,
                                 momentum=res_momentum)

    def spawn_glowing_particles(self, x, y, amount=10, direction=None,
                                radius=8, momentum=3, lifespan=120):
        """метод для спавна светящихся частиц"""
        for _ in range(round(amount * self.particles_coefficient)):
            if direction is None:
                direction = random.choice((-1, 0, 1))
            particle = GlowingParticle(x, y, radius, direction=direction,
                                       momentum=momentum, lifespan=lifespan)
            self.particles.raw_add(particle)

    def draw(self, win: pygame.Surface):
        if not self.is_rotating:
            win.blit(self.image, self.rect)
            self.item_pos = self.rect.center
        else:
            image = pygame.transform.rotate(self.image, self.current_rotation)
            x = self.x - image.get_width() // 2
            y = self.y - image.get_height() // 2
            win.blit(image, (x, y))
            self.item_pos = self.pos
        self.bullets.draw(win)
        self.particles.raw_draw(win)

    def rotate(self):
        """метод для запуска вращения игрока вокруг своей оси"""
        if not self.is_rotating:
            self.is_rotating = True
            self.current_rotation = 0

    def update_sound_volume(self):
        """метод для обновления громкости звука предмета"""
        if (ratio := self.get_game_value(self.VOLUME_KEY)) != -1:
            self.volume_ratio = ratio
            self.jump_sound.set_volume(0.45 * self.volume_ratio)
            self.shoot_sound.set_volume(0.3 * self.volume_ratio)

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

    def update_particles_amount(self):
        """метод для получения коэффициента количества частиц"""
        if (amount := self.get_game_value(self.PARTICLES_KEY)) != -1:
            self.particles_coefficient = amount

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
        self.is_rotating = False
        self.current_rotation = 0
        self.item_pos = self.rect.center
        self.bullets.clear()
        self.particles.clear()


class Bullet(StaticGameObject):
    """Класс для создания пули"""
    image = None

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        self.__class__.load_image(image_path, convert_alpha)
        super().__init__(
            x, y, image_path, screen_size, convert_alpha, load_image=False)
        self.speed_x = 0
        self.speed_y = 0
        self.speed_coefficient = 10
        self.lifespan = 150

    @classmethod
    def load_image(cls, image_path, convert_alpha):
        if cls.image is None:
            if convert_alpha:
                cls.image = pygame.image.load(image_path).convert_alpha()
            else:
                cls.image = pygame.image.load(image_path).convert()

    def shoot(self, target_x: int, target_y: int):
        """метод для старта полета пули в определенном направлении"""
        self.speed_x = int((self.x - target_x) / self.speed_coefficient)
        self.speed_y = int((self.y - target_y) / self.speed_coefficient)

    def update(self):
        self.rect.x -= self.speed_x
        self.rect.y -= self.speed_y
        self.lifespan -= 1
        condition1 = self.x > self.screen_width or self.y > self.screen_height
        condition2 = self.x < self.rect.width or self.x < self.rect.height
        if condition1 or condition2 or self.lifespan <= 0:
            self.delete()

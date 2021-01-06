import json
import pygame
import random


class GameObject(pygame.sprite.Sprite):
    """Абстрактный класс для игровых объектов"""
    object_id = 0

    def __init__(self, screen_size):
        super().__init__()
        self.screen_width, self.screen_height = screen_size
        self._id = GameObject.object_id
        GameObject.object_id += 1
        self.to_delete = False

    def update(self):
        """метод для обновления положения объекта"""
        pass

    def collides(self, rect: pygame.Rect):
        """метод для проверки столкновений с другими объектами"""
        return self.rect.colliderect(rect)

    def collidepoint(self, point: tuple[int, int]):
        """Метод для проверки столкновения объекта с точкой"""
        return self.rect.collidepoint(point)

    def set_pos(self, pos: tuple[int, int]):
        """метод для изменения позиции объекта"""
        self.rect.topleft = pos

    def delete(self, *args, **kwargs):
        """метод для удаления спарйта из группы"""
        self.to_delete = True
        self.on_delete(*args, **kwargs)

    def on_delete(self, *args, **kwargs):
        """метод, выполняемый при удалении объекта"""
        pass

    def process_collision(self, item: pygame.sprite.Sprite):
        """метод для обработки столкновения с объетами"""
        pass

    def __eq__(self, other):
        """метод для сравнения спрайтов"""
        return self._id == other._id

    def __ne__(self, other):
        return self._id != other._id

    @property
    def pos(self) -> tuple[int, int]:
        """метод для получения позиции объекта"""
        return self.rect.topleft

    @property
    def x(self) -> int:
        return self.rect.x

    @property
    def y(self) -> int:
        return self.rect.y

    @property
    def top(self) -> int:
        return self.rect.top

    @property
    def bottom(self) -> int:
        return self.rect.bottom


class StaticGameObject(GameObject):
    """Абстрактный класс для создания статичных игровых объектов"""

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True,
                 load_image=True):
        super().__init__(screen_size)
        if load_image:
            if convert_alpha:
                self.image = pygame.image.load(image_path).convert_alpha()
            else:
                self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class AnimatedGameObject(GameObject):
    """Абстрактный класс для создания анимированных игровых объеков"""
    images = None
    static_image = None

    def __init__(self, x, y, images, screen_size, convert_alpha=True,
                 create_static=True, colorkey=None):
        super().__init__(screen_size)
        self.__class__.load_images(
            images, convert_alpha, create_static, colorkey)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.current_frame = 0
        self.frames_amount = len(self.images)

    @classmethod
    def load_images(cls, images, convert_alpha=True, create_static=True, colorkey=None):
        """метод для загрузки анимации спрайта"""
        if cls.images is None:
            if convert_alpha:
                cls.images = [pygame.image.load(
                    image).convert_alpha() for image in images]
            else:
                cls.images = [pygame.image.load(
                    image).convert() for image in images]
            cls.set_colorkey(colorkey)
            if create_static and cls.static_image is None:
                cls.static_image = cls.images.pop(0)

    @classmethod
    def set_colorkey(cls, colorkey):
        if colorkey is not None:
            if colorkey == -1:
                for image in cls.images:
                    image.set_colorkey(image.get_at((5, 5)))
            else:
                for image in cls.images:
                    image.set_colorkey(colorkey)

    def update(self, skip_frames=1):
        position = self.pos
        self.current_frame = (
            self.current_frame + skip_frames) % self.frames_amount
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        self.set_pos(position)


class GameScene():
    """Абстрактный класс для игровой сцены/меню"""

    def __init__(self, display: pygame.Surface, manager, fps=60):
        # на принятой поверхности происхоит отрисовка сцены
        self.display = display  # объект из функции pygame.display.set_mode()
        self.FPS = fps
        self.clock = pygame.time.Clock()
        self.size = (self.display.get_width(), self.display.get_height())
        self.running = True
        #  мэнэджер загрузки сцен
        self.manager = manager
        self.HIGHSCORE_KEY = "highscore"
        self.MONEY_KEY = "money"
        self.MAGNET_KEY = "magnet"
        self.SHIELD_KEY = "shield"
        self.HAT_KEY = "hat"
        self.JETPACK_KEY = "jetpack"
        self.DAMAGE_KEY = "damage"
        self.RELOAD_KEY = "reload"
        self.JUMP_KEY = "jump"

    def redraw(self, win: pygame.Surface):
        """метод для отрисовки на заданной поверхности"""
        pass

    def handle_events(self):
        """метод для обработки событий внутри сцены"""
        pass

    def close(self):
        """метод для закрытия сцены"""
        self.running = False

    def show(self):
        """метод для запуска сцены"""
        self.running = True
        while self.running:
            self.handle_events()
            self.redraw(self.display)
            pygame.display.update()
            self.clock.tick(self.FPS)

    def set_game_value(self, key, new_value):
        """метод для обновления файла с игровыми сохранениями"""
        try:
            with open("values.json", "r+", encoding="u8") as f:
                data = json.load(f)
                data[key] = new_value
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except Exception as err:
            print(err)

    def get_game_value(self, key):
        """метод для получения значения из файла игровых сохранений"""
        try:
            with open("values.json", "r", encoding="u8") as f:
                data = json.load(f)
        except Exception as err:
            print(err)
            result = -1
        else:
            result = data.get(key, -1)
        finally:
            return result

    def load_upgrades_levels(self):
        """метод для получения уровней предметов"""
        try:
            with open("values.json", "r", encoding="u8") as f:
                data = json.load(f)
        except Exception as err:
            print(err)
            self.magnet_level = 0
            self.shield_level = 0
            self.hat_level = 0
            self.jetpack_level = 0
            self.damage_level = 0
            self.reload_level = 0
            self.jump_level = 0
        else:
            self.magnet_level = data.get(self.MAGNET_KEY)
            self.shield_level = data.get(self.SHIELD_KEY)
            self.hat_level = data.get(self.HAT_KEY)
            self.jetpack_level = data.get(self.JETPACK_KEY)
            self.damage_level = data.get(self.DAMAGE_KEY)
            self.reload_level = data.get(self.RELOAD_KEY)
            self.jump_level = data.get(self.JUMP_KEY)


class Group():
    """Кастомный класс для организации спрайтов"""

    def __init__(self, *sprites):
        self.sprites = list(sprites)

    def update(self, *args, **kwargs):
        """метод для обновления спрайтов"""
        for sprite in self.sprites:
            sprite.update(*args, **kwargs)
        self.clear_sprites()

    def add(self, sprite: pygame.sprite.Sprite):
        """метод для добавления спрайта в группу"""
        if isinstance(sprite, pygame.sprite.Sprite):
            self.sprites.append(sprite)
        else:
            raise TypeError("Wrong type for argument")

    def raw_add(self, sprite):
        """метод для добавления объектов, не наследующихся от спрайта"""
        self.sprites.append(sprite)

    def raw_draw(self, win):
        """метод для отрисовки объектов, если у них есть метод draw(self, win)"""
        for sprite in self.sprites:
            sprite.draw(win)

    def remove(self, sprite: pygame.sprite.Sprite):
        """метод для удаления спрайта из группы"""
        if isinstance(sprite, pygame.sprite.Sprite):
            for index, value in tuple(enumerate(self.sprites))[::-1]:
                if sprite == value:
                    self.sprites.pop(index)
                    break
        else:
            raise TypeError("Wrong type for argument")

    def clear_sprites(self):
        """метод для удаления помеченных спрайтов"""
        for index, sprite in tuple(enumerate(self.sprites))[::-1]:
            if sprite.to_delete:
                self.sprites.pop(index)

    def draw(self, win, sort=None):
        """метод для отрисовки спрайтов из группы"""
        sprites = self.sprites if sort is None else sorted(
            self.sprites, key=sort)
        for sprite in sprites:
            win.blit(sprite.image, sprite.rect)

    def clear(self):
        """Метод для удаления всех спрайтов из группы"""
        self.sprites.clear()

    def get_collisions(self, target, ignore=None):
        """метод для получения спрайтов, с которыми столкнулся предеанный объект"""
        if ignore is None:
            return [sprite for sprite in self.sprites if target.collides(
                sprite.rect)]
        else:
            ignore = [el for el in ignore if el is not None]
            return [sprite for sprite in self.sprites if target.collides(
                sprite.rect) and sprite not in ignore]

    def get_rect_collisions(self, rect):
        """метод для получения коллизий ректа со спрайтами в группе"""
        return [sprite for sprite in self.sprites if rect.colliderect(sprite.rect)]

    def __getitem__(self, index):
        try:
            return self.sprites[index]
        except IndexError:
            raise IndexError(f"Wrong index supplied: {index}")

    def __len__(self):
        return len(self.sprites)


class Particle():
    """класс для создания частицы"""

    def __init__(self, x, y, radius, color, lifespan=120, direction=1, momentum=3):
        self.x_pos = x
        self.y_pos = y
        self.speed_x = random.random() * 5 * direction
        self.color = color
        self.gravity = 0.2
        self.v_momentum = momentum
        self.radius = radius
        self.lifespan = lifespan
        self.to_delete = False

    def draw(self, win):
        if self.lifespan > 0 and self.radius > 0:
            pygame.draw.circle(
                win, self.color, (self.x_pos, self.y_pos), self.radius)

    def update(self):
        self.radius -= random.random()
        self.x_pos += self.speed_x
        self.v_momentum += self.gravity
        self.y_pos += self.v_momentum
        self.lifespan -= 1
        if self.lifespan <= 0 or self.radius <= 0:
            self.to_delete = True


class GlowingParticle():
    """Класс для создания светящихся частиц"""

    def __init__(self, x, y, radius, lifespan=120, direction=1, momentum=3):
        self.x = x
        self.y = y
        self.radius = radius
        self.lifespan = lifespan
        self.direction = direction
        self.v_momentum = momentum
        self.speed_x = random.random() * 5 * direction
        self.gravity = 0.2
        self.to_delete = False
        self.create_image()

    def update(self):
        self.x += self.speed_x
        self.v_momentum += self.gravity
        self.y += self.v_momentum
        self.lifespan -= 1
        self.radius -= random.random()
        if self.lifespan <= 0 or self.radius <= 0:
            self.to_delete = True
        else:
            self.create_image()

    def draw(self, win):
        win.blit(self.image, (self.x - self.radius, self.y - self.radius),
                 special_flags=pygame.BLEND_RGB_ADD)

    def create_image(self):
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        pygame.draw.circle(self.image, (20, 20, 20),
                           (self.radius, self.radius), self.radius)

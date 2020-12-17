from core import GameScene, Group
from items import *
from main_character import MainCharacter
from platforms import Platform
import pygame
import random


class Level(GameScene):
    """Класс для создания уровня"""

    def __init__(self, display: pygame.Surface, fps=60):
        super(Level, self).__init__(display, fps)
        self.background = pygame.image.load("assets/background.png")
        self.main_character = MainCharacter(200, 100,
                                            "assets/base_character72.png",
                                            self.size)
        # прямоугольник для проверки упал игрок вниз или нет
        self.bottom_rect = pygame.Rect(
            -100, self.size[0] - 2, self.size[1] + 200, 2)
        # координаты фона (нужны, чтобы сдвигать фон при движении вверх)
        self.bg_pos = [0, -2000]
        self.offset = 5
        # переменные для обработки движения по нажатым кнопкам
        self.scroll_down = False
        self.move_right = False
        self.move_left = False
        self.parallax_coefficient = 0.1
        # количество платформ в сцене
        self.platforms_amount = 10
        # список платформ на экране
        self.platforms = Group()
        self.items = Group()

    def spawn_platforms(self):
        """метод для генерации новых платформ в рандомных координатах"""
        for _ in range(self.platforms_amount - len(self.platforms)):
            x = random.randint(0, self.size[0] - 100)
            y = random.randint(0, self.size[1] - 100)
            platform = Platform(
                x, y, "assets/platform72.png", self.size)
            self.platforms.add(platform)
            self.spawn_objects(platform, x, y)

    def spawn_objects(self, platform: Platform, x: int, y: int):
        if 0.1 < random.random() < 0.2:
            spring = Spring(x + 10, y - 5, "assets/spring16.png", self.size)
            platform.add_item(spring)
            self.items.add(spring)
        elif 0.4 < random.random() < 0.5:
            hat = PropellerHat(x + 10, y - 15, "assets/hat32.png", self.size)
            platform.add_item(hat)
            self.items.add(hat)
        elif 0.2 < random.random() < 0.3:
            trampoline = Trampoline(x + 4, y - 15, "assets/trampoline64.png",
                                    self.size)
            platform.add_item(trampoline)
            self.items.add(trampoline)
        elif 0.3 < random.random() < 0.4:
            jetpack = Jetpack(x + 13, y - 45,
                              "assets/jetpack48.png", self.size)
            platform.add_item(jetpack)
            self.items.add(jetpack)

    def get_collisions(self, target, group):
        return [sprite for sprite in group if target.collides(sprite.rect)]

    def check_collisions(self):
        """метод для обработки всех столкновений"""
        for coll in self.get_collisions(self.main_character, self.platforms):
            self.main_character.process_collision(coll)
            self.scroll_down = True
        for coll in self.get_collisions(self.main_character, self.items):
            self.main_character.process_collision(coll)
            self.scroll_down = True
        if self.main_character.collides(self.bottom_rect):
            print("You lose")
            self.close()

    def redraw(self, win):
        """метод для отрисовки сцены"""
        win.fill((255, 255, 255))
        win.blit(self.background, self.bg_pos)
        self.main_character.draw(win)
        self.platforms.draw(win)
        self.items.draw(win)

    def handle_events(self):
        """метод для обработки событий сцены"""
        pygame.display.set_caption(str(self.clock.get_fps()))
        self.spawn_platforms()
        # остановка сдвига вниз, когда игрок начинает падать вниз
        if self.main_character.v_momentum > 0:
            self.scroll_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                self.handle_keyboard_events(event)
            if event.type == pygame.KEYUP:
                self.handle_keyboard_events(event, state=False)
        self.check_collisions()
        self.handle_movement()
        self.main_character.update()
        self.items.update(self.offset if self.scroll_down else 0,
                          player=self.main_character)

    def handle_movement(self):
        """метод для обработки движения персонажа и платформ"""
        # self.offset = (self.size[1] - self.main_character.y) // 20
        self.move_character(8)
        if self.scroll_down:
            self.scroll(self.offset)
            self.platforms.update(self.offset)

    def handle_keyboard_events(self, event, state=True):
        """метод для обработки нажатий клавиатуры"""
        if event.key == pygame.K_ESCAPE:
            self.close()
        if event.key == pygame.K_a:
            self.move_left = state
        if event.key == pygame.K_d:
            self.move_right = state

    def scroll(self, offset: int):
        """метод для сдвига фона вниз"""
        if self.scroll_down:
            self.bg_pos[1] += offset * self.parallax_coefficient

    def move_character(self, offset: int):
        """метод для сдвига игрока по горизонтали, пока зажаты кнопки A/D"""
        if self.move_right:
            self.main_character.move_h(offset)
        elif self.move_left:
            self.main_character.move_h(-offset)


class MainMenu(GameScene):
    """Класс для создания главного меню (пока пустой)"""

    def __init__(self, display: pygame.Surface, fps=60):
        super(MainMenu, self).__init__(display, fps)

    def redraw(self, win):
        win.fill((255, 0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()

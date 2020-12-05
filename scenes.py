from core import GameScene
from main_character import MainCharacter
from platforms import Platform
import pygame
import random


class Level(GameScene):
    """Класс для создания уровня"""

    def __init__(self, display: pygame.Surface, fps=60):
        super(Level, self).__init__(display, fps)
        self.background = pygame.image.load("assets/background.png")
        self.main_character = MainCharacter(
            200, 100, "assets/base_character72.png")
        # прямоугольник для проверки упал игрок вниз или нет
        self.bottom_rect = pygame.Rect(
            0, display.get_height() - 2, display.get_width(), 2)
        # координаты фона (нужны, чтобы сдвигать фон при движении вверх)
        self.bg_pos = [0, -2000]
        # переменные для обработки движения по нажатым кнопкам
        self.scroll_up = False
        self.scroll_down = False
        self.move_right = False
        self.move_left = False
        self.parallax_coefficient = 0.25
        # количество платформ в сцене
        self.platforms_amount = 10
        # список платформ на экране
        self.platforms = []
        self.spawn_platforms()

    def spawn_platforms(self):
        """метод для генерации новых платформ в рандомных координатах"""
        for _ in range(self.platforms_amount - len(self.platforms)):
            self.platforms.append(Platform(
                *[random.randint(0, 500) for _ in range(2)], "assets/platform72.png"))

    def check_collisions(self):
        """метод для обработки всех столкновений (надо будет разбить на отдельные)"""
        for platform in self.platforms:
            # проверка столкновений игрока и платформ
            if self.main_character.collides(platform.rect):
                if self.main_character.y > platform.y:
                    # если игрок находится над платформой, то он останавливается
                    # на ней и не падает дяльше
                    self.main_character.y = platform.rect.top - self.main_character.height
                # прыжок игрока после касания платформы
                self.main_character.jump()
                # сдвиг фона вниз вместе с платформами
                self.scroll_down = True
        # проверка столкновения с низом экрана
        if self.main_character.collides(self.bottom_rect):
            self.main_character.v_momentum = -10
            # self.close()
            print("You lose")

    def scroll_platforms(self, offset: int):
        """метод для сдвига всех платформ вниз"""
        if self.scroll_down:
            for platform in self.platforms:
                platform.scroll(offset)

    def delete_platforms(self):
        """метод для удаления платформ, которые выходя за границы экрана"""
        for platform in self.platforms:
            if platform.pos[1] > 600:
                self.platforms.remove(platform)

    def redraw(self, win):
        """метод для отрисовки сцены"""
        win.fill((255, 255, 255))
        win.blit(self.background, self.bg_pos)
        self.main_character.draw(win)
        for platform in self.platforms:
            platform.draw(win)

    def handle_events(self):
        """метод для обработки событий сцены"""
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
        self.scroll(3)
        self.move_character(8)
        self.check_collisions()
        self.scroll_platforms(3)
        self.delete_platforms()

    def handle_keyboard_events(self, event, state=True):
        """метод для обработки нажатий клавиатуры"""
        if event.key == pygame.K_ESCAPE:
            self.close()
        if event.key == pygame.K_w:
            self.scroll_up = state
        if event.key == pygame.K_s:
            self.scroll_down = state
        if event.key == pygame.K_a:
            self.move_left = state
        if event.key == pygame.K_d:
            self.move_right = state
        if event.key == pygame.K_SPACE:
            self.main_character.jump()

    def scroll(self, offset: int):
        """метод для сдвига фона вниз/вверх"""
        if self.scroll_up:
            self.bg_pos[1] -= offset
        elif self.scroll_down:
            self.bg_pos[1] += offset

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

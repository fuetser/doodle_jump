from core import GameScene, Group
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
                "assets/base_character72.png", self.size, convert_alpha=True)
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
        self.parallax_coefficient = 0.1
        # количество платформ в сцене
        self.platforms_amount = 10
        # список платформ на экране
        self.platforms = Group()

    def spawn_platforms(self):
        """метод для генерации новых платформ в рандомных координатах"""
        for _ in range(self.platforms_amount - len(self.platforms)):
            x = random.randint(0, self.size[0] - 100)
            y = random.randint(0, self.size[1] - 100)
            platform = Platform(
                x, y, "assets/platform72.png", self.size, convert_alpha=True)
            self.platforms.add(platform)

    def get_collisions(self, target, group):
        return [sprite for sprite in group if target.collides(sprite.rect)]

    def check_collisions(self):
        """метод для обработки всех столкновений"""
        for coll in self.get_collisions(self.main_character, self.platforms):
            if self.main_character.bottom >= coll.top and self.main_character.bottom <= coll.bottom:
                if self.main_character.v_momentum > 1:
                    self.main_character.rect.bottom = coll.rect.top
                    self.scroll_down = True
                    self.main_character.jump()
        if self.main_character.collides(self.bottom_rect):
            self.main_character.v_momentum = -10
            # self.close()
            print("You lose")

    def redraw(self, win):
        """метод для отрисовки сцены"""
        win.fill((255, 255, 255))
        win.blit(self.background, self.bg_pos)
        self.main_character.draw(win)
        self.platforms.draw(win)

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
        self.main_character.update()
        self.handle_movement()
        self.check_collisions()

    def handle_movement(self):
        """метод для обработки движения персонажа и платформ"""
        self.scroll(5 * self.parallax_coefficient)
        self.move_character(8)
        if self.scroll_down:
            self.platforms.update(5)

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

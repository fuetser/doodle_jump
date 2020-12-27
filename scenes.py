from core import GameScene, Group, GameObject
from enemies import *
from items import *
import json
from main_character import MainCharacter
from platforms import Platform
import pygame
import random


class Level(GameScene):
    """Класс для создания уровня"""

    def __init__(self, display: pygame.Surface, fps=60):
        super(Level, self).__init__(display, fps)
        self.background = pygame.image.load(
            "assets/ui/cycled_bg.jpg").convert()
        self.bg_height = self.background.get_height()
        self.main_character = MainCharacter(200, 100,
                                            "assets/base_character72.png",
                                            self.size)
        # прямоугольник для проверки упал игрок вниз или нет
        self.bottom_rect = pygame.Rect(
            -100, self.size[0] - 2, self.size[1] + 200, 2)
        # координаты фона (нужны, чтобы сдвигать фон при движении вверх)
        self.bg_pos = -self.background.get_height() + self.size[1]
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
        self.enemies = Group()

        self.score_font = pygame.font.SysFont("cambriacambriamath", 30)
        self.score = 0
        self.game_over = False
        self.enemy_height = 0

    def spawn_platforms(self):
        """метод для генерации новых платформ в рандомных координатах"""
        for _ in range(self.platforms_amount - len(self.platforms)):
            x = random.randint(0, self.size[0] - 100)
            y = random.randint(0, self.size[1] - 100)
            platform = Platform(
                x, y, "assets/platforms/platform72.png", self.size)
            self.platforms.add(platform)
            self.spawn_objects(platform, x, y)
            self.spawn_enemies()

    def spawn_objects(self, platform: Platform, x: int, y: int):
        if 0.1 < random.random() < 0.2:
            spring = Spring(
                x + 10, y - 5, "assets/items/spring16.png", self.size)
            platform.add_item(spring)
            self.items.add(spring)
        elif 0.4 < random.random() < 0.5:
            hat = PropellerHat(
                x + 10, y - 15, "assets/items/hat32.png", self.size)
            platform.add_item(hat)
            self.items.add(hat)
        elif 0.2 < random.random() < 0.3:
            trampoline = Trampoline(
                x + 4, y - 15, "assets/items/trampoline64.png", self.size)
            platform.add_item(trampoline)
            self.items.add(trampoline)
        elif 0.3 < random.random() < 0.4:
            jetpack = Jetpack(x + 13, y - 45,
                              "assets/items/jetpack48.png", self.size)
            platform.add_item(jetpack)
            self.items.add(jetpack)

    def spawn_enemies(self):
        """метод для спавна врагов"""
        if len(self.enemies) == 0 and self.score > 10000:
            if self.score - self.enemy_height > 2000:
                self.enemy_height = self.score
                enemy = Enemy(0, 0, "assets/enemies/enemy.png", self.size)
                self.enemies.add(enemy)

    def check_collisions(self):
        """метод для обработки всех столкновений"""
        for group in (self.platforms, self.items, self.enemies):
            for coll in group.get_collisions(self.main_character):
                self.main_character.process_collision(coll)
                self.scroll_down = True

        if self.main_character.collides(self.bottom_rect) or self.main_character.game_over:
            self.game_over = True
            self.close()

    def redraw(self, win):
        """метод для отрисовки сцены"""
        win.fill((255, 255, 255))
        relative_background_y = self.bg_pos % self.bg_height
        win.blit(self.background, (0, relative_background_y - self.bg_height))
        if relative_background_y < self.size[1]:
            win.blit(self.background, (0, relative_background_y))
        self.main_character.draw(win)
        self.platforms.draw(win)
        self.items.draw(win)
        self.enemies.draw(win)
        win.blit(self.render_score(), (10, 10))

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.main_character.shoot(*event.pos)

        self.check_collisions()
        self.handle_movement()
        self.main_character.update(
            self.enemies[0] if len(self.enemies) else None)
        self.enemies.update(self.offset if self.scroll_down else 0)
        self.items.update(self.offset if self.scroll_down else 0,
                          player=self.main_character)

    def handle_movement(self):
        """метод для обработки движения персонажа и платформ"""
        self.offset = 5
        # если игрок находится выше середины экрана,
        # то сдвигаются платформы вниз, а не игрок вверх
        while self.main_character.y < self.size[1] // 2 - 50:
            self.offset += 1
            self.main_character.rect.y += 1
        self.move_character(8)
        if self.scroll_down:
            self.scroll(self.offset)
            self.platforms.update(self.offset)

    def handle_keyboard_events(self, event, state=True):
        """метод для обработки нажатий клавиатуры"""
        if event.key == pygame.K_a:
            self.move_left = state
        if event.key == pygame.K_d:
            self.move_right = state

    def scroll(self, offset: int):
        """метод для сдвига фона вниз"""
        if self.scroll_down:
            self.score += offset
            self.bg_pos += offset * self.parallax_coefficient

    def move_character(self, offset: int):
        """метод для сдвига игрока по горизонтали, пока зажаты кнопки A/D"""
        if self.move_right:
            self.main_character.move_h(offset)
        elif self.move_left:
            self.main_character.move_h(-offset)

    def render_score(self):
        """Метод для рендера игрового счета"""
        return self.score_font.render(str(self.score), True, (0, 0, 0))

    def get_score(self) -> int:
        return self.score

    def restart(self):
        """Метод для перезапуска игры"""
        self.game_over = False
        self.main_character.reset()
        self.score = 0
        self.bg_pos = -self.background.get_height() + self.size[1]
        self.offset = 5
        self.scroll_down = False
        self.move_right = False
        self.move_left = False
        self.platforms.clear()
        self.items.clear()
        self.enemies.clear()
        self.main_character.set_pos((200, 100))


class MainMenu(GameScene):
    """Класс для создания главного меню (пока пустой)"""

    def __init__(self, display: pygame.Surface, fps=60):
        super(MainMenu, self).__init__(display, fps)
        self.background = pygame.image.load(
            "assets/ui/main_menu_bg.jpg").convert()
        self.play_button = GameObject(400, 150, "assets/ui/play_button.png",
                                      self.size, convert_alpha=True)
        self.load_level = False

    def redraw(self, win):
        win.blit(self.background, (0, 0))
        win.blit(self.play_button.image, self.play_button.rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.collidepoint(event.pos):
                    self.load_level = True
                    self.close()

    def show(self):
        self.load_level = False
        super().show()


class GameOverMenu(GameScene):
    """Класс для создание меню после проигрыша"""

    def __init__(self, display: pygame.Surface, fps=60):
        super(GameOverMenu, self).__init__(display, fps)
        self.score = 0
        self.highscore = 0
        self.font = pygame.font.SysFont("cambriacambriamath", 40)
        self.restart_button = GameObject(200, 210, "assets/ui/restart_button.png",
                                         self.size, convert_alpha=True)
        self.menu_button = GameObject(200, 300, "assets/ui/menu_button.png",
                                      self.size, convert_alpha=True)
        self.restart_game = False
        self.load_main_menu = False

    def redraw(self, win):
        pygame.draw.rect(win, "grey",
                         (50, 50, self.size[0] - 100, self.size[1] - 100))
        highscore = self.font.render(
            f"Highscore: {self.highscore}", True, "black")
        current_score = self.font.render(f"Score: {self.score}", True, "black")
        win.blit(highscore, ((self.size[0] - highscore.get_width()) // 2, 75))
        win.blit(current_score,
                 ((self.size[0] - current_score.get_width()) // 2, 150))
        # win.blit(self.font.render(str(self.score), True, "black"), (60, 110))
        win.blit(self.restart_button.image, self.restart_button.rect)
        win.blit(self.menu_button.image, self.menu_button.rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button.collidepoint(event.pos):
                    self.restart_game = True
                    self.close()
                if self.menu_button.collidepoint(event.pos):
                    self.load_main_menu = True
                    self.close()

    def set_score(self, score: int):
        """Метод для установки счета игры"""
        self.score = score
        self.update_highscore(score)

    def get_highscore(self):
        """метод для получения рекорда из файла"""
        try:
            with open("values.json", "r", encoding="u8") as f:
                data = json.load(f)
        except Exception as err:
            print(err)
            highscore = -1
        else:
            highscore = int(data.get("highscore", -1))
        return highscore

    def save_highscore(self, new_highscore: int):
        """метод для сохранения нового рекорда"""
        try:
            with open("values.json", "w", encoding="u8") as f:
                json.dump({"highscore": new_highscore}, f)
        except Exception as err:
            print(err)

    def update_highscore(self, new_highscore: int):
        """метод для обновления рекорда по окончанию игры"""
        if (score := self.get_highscore()) != -1 and new_highscore > score:
            self.save_highscore(new_highscore)
            self.highscore = new_highscore
        else:
            self.highscore = score

    def show(self):
        self.restart_game = False
        self.load_main_menu = False
        super().show()

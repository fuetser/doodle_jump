from core import GameScene, Group, StaticGameObject
from enemies import FlyingEye
from items import *
import json
from main_character import MainCharacter
from platforms import Platform
import pygame
import random


class Level(GameScene):
    """Класс для создания уровня"""

    def __init__(self, display: pygame.Surface, manager, fps=60):
        super(Level, self).__init__(display, manager, fps)
        self.load_upgrades()

        self.background = pygame.image.load(
            "assets/ui/cycled_bg.jpg").convert()
        self.bg_height = self.background.get_height()
        self.main_character = MainCharacter(200, 100,
                                            "assets/base_character72.png",
                                            self.size, self.damage_upgrade)
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
        # группы объектов на экране
        self.platforms = Group()
        self.items = Group()
        self.enemies = Group()

        self.score_font = pygame.font.SysFont("cambriacambriamath", 30)
        self.score = 0
        self.enemy_height = 0
        self.coin = GoldenCoin(500, 15, self.size, ignore_scroll=True)

        self.lose_sound = pygame.mixer.Sound("assets/sounds/lose.wav")
        self.lose_sound.set_volume(0.4)

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
        # if 0.1 < random.random() < 0.2:
        #     spring = Spring(x + 10, y - 5, self.size)
        #     platform.add_item(spring)
        #     self.items.add(spring)
        # elif 0.2 < random.random() < 0.3:
        #     hat = PropellerHat(x + 10, y - 25, self.size, self.hat_upgrade)
        #     platform.add_item(hat)
        #     self.items.add(hat)
        # elif 0.2 < random.random() < 0.3:
        #     trampoline = Trampoline(x + 4, y - 15, self.size)
        #     platform.add_item(trampoline)
        #     self.items.add(trampoline)
        if 0 < random.random() < 0.4:
            jetpack = Jetpack(x + 13, y - 45, self.size, self.jetpack_upgrade)
            platform.add_item(jetpack)
            self.items.add(jetpack)
        # elif 0.4 < random.random() < 0.5:
        #     coin = SilverCoin(x + 10, y - 25, self.size)
        #     platform.add_item(coin)
        #     self.items.add(coin)
        # elif 0.5 < random.random() < 0.6:
        #     magnet = Magnet(x + 10, y - 25, self.size, self.magnet_upgrade)
        #     platform.add_item(magnet)
        #     self.items.add(magnet)
        # elif 0.6 < random.random() < 0.7:
        #     shield = Shield(x + 10, y - 25, self.size, self.shield_upgrade)
        #     platform.add_item(shield)
        #     self.items.add(shield)

    def spawn_enemies(self):
        """метод для спавна врагов"""
        if len(self.enemies) == 0 and self.score > 10000:
            if self.score - self.enemy_height > 2000:
                self.enemy_height = self.score
                enemy = FlyingEye(0, 0, self.size)
                self.enemies.add(enemy)

    def check_collisions(self):
        """метод для обработки всех столкновений"""
        for group in (self.platforms, self.items, self.enemies):
            ignore = (self.main_character.shield, self.main_character.magnet)
            for coll in group.get_collisions(self.main_character, ignore):
                self.scroll_down = self.main_character.process_collision(coll)
            self.main_character.process_magnet_collisions(group)

        if self.main_character.collides(self.bottom_rect) or self.main_character.game_over:
            self.manager.load_scene(2)
            self.lose_sound.play()
            self.items.clear()
            self.mute_sounds()
            self.close()

    def redraw(self, win):
        """метод для отрисовки сцены"""
        win.fill((255, 255, 255))
        relative_background_y = self.bg_pos % self.bg_height
        win.blit(self.background, (0, relative_background_y - self.bg_height))
        if relative_background_y < self.size[1]:
            win.blit(self.background, (0, relative_background_y))
        self.platforms.draw(win)
        self.main_character.draw(win)
        self.items.draw(win)
        self.enemies.draw(win)
        win.blit(self.render_score(), (10, 10))
        money = self.render_money()
        money_x = self.size[0] - money.get_width() - 10
        win.blit(money, (money_x, 10))
        self.coin.set_pos((money_x - self.coin.rect.w - 10, 15))

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

    def load_upgrades(self):
        """метод для загрузки прокачки игрока"""
        self.load_upgrades_levels()
        with open("upgrades.json", "r", encoding="u8") as f:
            data = json.load(f)
        self.magnet_upgrade = data.get(self.MAGNET_KEY).get(
            str(self.magnet_level))
        self.shield_upgrade = data.get(self.SHIELD_KEY).get(
            str(self.shield_level))
        self.hat_upgrade = data.get(self.HAT_KEY).get(str(self.hat_level))
        self.jetpack_upgrade = data.get(self.JETPACK_KEY).get(
            str(self.jetpack_level))
        self.damage_upgrade = data.get(self.DAMAGE_KEY).get(
            str(self.damage_level))

    def mute_sounds(self):
        """метод для отсановки всех звуков"""
        for sprite in self.items:
            if hasattr(sprite, "sound"):
                sprite.sound.stop()

    def render_score(self):
        """Метод для рендера игрового счета"""
        return self.score_font.render(str(self.score), True, (0, 0, 0))

    def render_money(self):
        """метод для рендера количества собранных монеток"""
        return self.score_font.render(
            str(self.main_character.get_collected_money()), True, (0, 0, 0))

    def get_score(self) -> int:
        return self.score

    def get_collected_money(self) -> int:
        return self.main_character.get_collected_money()

    def restart(self):
        """Метод для перезапуска игры"""
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
        self.items.add(self.coin)

    def revive_game(self):
        """метод для продолжения игры после проигрыша"""
        self.main_character.set_pos((250, 150))
        self.move_left = False
        self.move_right = False
        self.show()

    def show(self):
        self.load_upgrades()
        super().show()


class MainMenu(GameScene):
    """Класс для создания главного меню (пока пустой)"""

    def __init__(self, display: pygame.Surface, manager, fps=60):
        super(MainMenu, self).__init__(display, manager, fps)
        self.background = pygame.image.load(
            "assets/ui/main_menu_bg.jpg").convert()
        self.play_button = StaticGameObject(400, 125,
                                            "assets/ui/play_button.png",
                                            self.size, convert_alpha=True)
        self.shop_button = StaticGameObject(400, 190,
                                            "assets/ui/shop_button.png",
                                            self.size, convert_alpha=True)
        self.click_sound = pygame.mixer.Sound("assets/sounds/button_press.wav")
        self.click_sound.set_volume(0.4)

    def redraw(self, win):
        win.blit(self.background, (0, 0))
        win.blit(self.play_button.image, self.play_button.rect)
        win.blit(self.shop_button.image, self.shop_button.rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.collidepoint(event.pos):
                    self.manager.load_scene(1)
                    self.click_sound.play()
                    self.close()
                if self.shop_button.collidepoint(event.pos):
                    self.manager.load_scene(4)
                    self.click_sound.play()
                    self.close()

    def show(self):
        self.load_level = False
        self.load_shop = False
        super().show()


class GameOverMenu(GameScene):
    """Класс для создание меню после проигрыша"""

    def __init__(self, display: pygame.Surface, manager, fps=60):
        super(GameOverMenu, self).__init__(display, manager, fps)
        self.score = 0
        self.highscore = 0
        self.font = pygame.font.SysFont("cambriacambriamath", 40)
        self.restart_button = StaticGameObject(220, 230,
                                               "assets/ui/restart_button.png",
                                               self.size, convert_alpha=True)
        self.menu_button = StaticGameObject(220, 300,
                                            "assets/ui/menu_button.png",
                                            self.size, convert_alpha=True)
        self.continue_button = StaticGameObject(200, 475,
                                                "assets/ui/continue_button.png",
                                                self.size, convert_alpha=True)
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        self.click_sound.set_volume(0.6)
        self.revive_price = 250
        self.revive_countdown = 5 * self.FPS
        self.revive_happened = False
        self.draw_revive = False

    def redraw(self, win):
        pygame.draw.rect(win, "grey",
                         (50, 50, self.size[0] - 100, self.size[1] - 100))
        highscore = self.font.render(
            f"Highscore: {self.highscore}", True, "black")
        current_score = self.font.render(f"Score: {self.score}", True, "black")
        win.blit(highscore, ((self.size[0] - highscore.get_width()) // 2, 75))
        win.blit(current_score,
                 ((self.size[0] - current_score.get_width()) // 2, 150))
        win.blit(self.restart_button.image, self.restart_button.rect)
        win.blit(self.menu_button.image, self.menu_button.rect)
        if self.draw_revive:
            self.draw_revive_dialog(win)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button.collidepoint(event.pos):
                    self.manager.load_scene(1)
                    self.click_sound.play()
                    self.revive_happened = False
                    self.close()
                if self.menu_button.collidepoint(event.pos):
                    self.manager.load_scene(0)
                    self.click_sound.play()
                    self.revive_happened = False
                    self.close()
                if self.draw_revive and self.continue_button.collidepoint(event.pos):
                    self.manager.load_scene(3)
                    self.update_money(-self.revive_price)
                    self.revive_happened = True
                    self.click_sound.play()
                    self.close()

    def set_score(self, score: int):
        """Метод для установки счета игры"""
        self.score = score
        self.update_highscore(score)

    def update_highscore(self, new_highscore: int):
        """метод для обновления рекорда по окончанию игры"""
        if (score := self.get_game_value(self.HIGHSCORE_KEY)) != -1 and new_highscore > score:
            self.set_game_value(self.HIGHSCORE_KEY, new_highscore)
            self.highscore = new_highscore
        else:
            self.highscore = score

    def update_money(self, money_to_add):
        if (money := self.get_game_value(self.MONEY_KEY)) != -1:
            self.set_game_value(self.MONEY_KEY, money + money_to_add)

    def show_revive_dialog(self):
        """метод для показа диалога возрождения"""
        if (money := self.get_game_value(self.MONEY_KEY)) != -1 and money >= self.revive_price:
            if not self.revive_happened:
                self.draw_revive = True

    def draw_revive_dialog(self, win: pygame.Surface):
        """метод для отрисовки диалога возрождения"""
        if self.revive_countdown > 0:
            pygame.draw.rect(win, (100, 100, 100),
                             (50, 400, self.size[0] - 100, 150))
            title = self.font.render(
                "Do you want to continue?", True, (0, 0, 0))
            time_remains = self.font.render(
                str(self.revive_countdown // self.FPS + 1), True, (0, 0, 0))
            win.blit(self.continue_button.image, self.continue_button.rect)
            win.blit(title, ((self.size[0] - title.get_width()) // 2, 410))
            win.blit(time_remains, (360, 475))
            self.revive_countdown -= 1
        else:
            self.draw_revive = False

    def restart(self):
        self.revive_countdown = 5 * self.FPS
        self.draw_revive = False
        self.restart_game = False
        self.load_main_menu = False

    def show(self):
        self.restart()
        self.show_revive_dialog()
        super().show()


class ShopMenu(GameScene):
    """Класс для создания магазина"""

    def __init__(self, display: pygame.Surface, manager, fps=60):
        super(ShopMenu, self).__init__(display, manager, fps)
        self.load_upgrades_levels()
        self.font = pygame.font.SysFont("cambriacambriamath", 32)
        self.menu_button = StaticGameObject(50, 525,
                                            "assets/ui/menu_button.png",
                                            self.size, convert_alpha=True)
        self.magnet_item = ShopItem(50, 25, self.size, "Magnet",
                                    level=self.magnet_level)
        self.shield_item = ShopItem(50, 150, self.size, "Shield",
                                    level=self.shield_level)
        self.hat_item = ShopItem(50, 275, self.size, "Hat",
                                 level=self.hat_level)
        self.jetpack_item = ShopItem(50, 400, self.size, "Jetpack",
                                     level=self.jetpack_level)
        self.damage_item = ShopItem(300, 25, self.size, "Damage",
                                    level=self.damage_level)
        self.click_sound = pygame.mixer.Sound("assets/sounds/button_press.wav")
        self.upgrade_sound = pygame.mixer.Sound(
            "assets/sounds/upgrade_unlock.wav")
        self.click_sound.set_volume(0.4)
        self.upgrade_sound.set_volume(0.4)

    def redraw(self, win):
        win.fill((255, 255, 255))
        win.blit(self.menu_button.image, self.menu_button.rect)
        self.magnet_item.draw(win)
        self.shield_item.draw(win)
        self.hat_item.draw(win)
        self.jetpack_item.draw(win)
        self.damage_item.draw(win)
        money = self.font.render(
            f"{self.get_game_value(self.MONEY_KEY)}$", True, (0, 0, 0))
        win.blit(money, (self.size[0] - money.get_width() - 25, 540))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button.collidepoint(event.pos):
                    self.manager.load_scene(0)
                    self.click_sound.play()
                    self.close()
                if self.magnet_item.clicked(event.pos):
                    self.purchase_upgrade(
                        key=self.MAGNET_KEY, item=self.magnet_item)
                if self.shield_item.clicked(event.pos):
                    self.purchase_upgrade(
                        key=self.SHIELD_KEY, item=self.shield_item)
                if self.hat_item.clicked(event.pos):
                    self.purchase_upgrade(
                        key=self.HAT_KEY, item=self.hat_item)
                if self.jetpack_item.clicked(event.pos):
                    self.purchase_upgrade(
                        key=self.JETPACK_KEY, item=self.jetpack_item)
                if self.damage_item.clicked(event.pos):
                    self.purchase_upgrade(
                        key=self.DAMAGE_KEY, item=self.damage_item)

    def purchase_upgrade(self, key, item):
        """метод для покупки улучшения"""
        if (money := self.get_game_value(self.MONEY_KEY)) != -1:
            if money >= item.price and item.level < 5:
                self.set_game_value(self.MONEY_KEY, money - item.price)
                item.add_level()
                self.set_game_value(key, item.level)
                self.upgrade_sound.play()

    def show(self):
        self.load_main_menu = False
        super().show()


class ShopItem(StaticGameObject):
    """Класс для создания предметов магазина"""

    def __init__(self, x, y, screen_size, title, level=0):
        super().__init__(x, y, "assets/ui/upgrades_bar.png",
                         screen_size, convert_alpha=True)
        self.title_text = title
        self.level = level
        self.price = (self.level + 1) * 100
        self.font = pygame.font.SysFont("cambriacambriamath", 32)
        self.title = self.font.render(
            f"{title} ({self.price if self.level < 5 else 'max'})",
            True, (0, 0, 0))
        self.title_pos = [
            x + (self.image.get_width() - self.title.get_width()) // 2, y]
        self.rect.y = y + self.title.get_height() + 10
        self.plus_button = StaticGameObject(x, y,
                                            "assets/ui/plus_button.png",
                                            screen_size, convert_alpha=True)
        self.plus_button.set_pos((self.rect.right - self.plus_button.rect.w,
                                  y + self.title.get_height() + 10))
        self.colors = (
            (253, 245, 66),
            (251, 216, 8),
            (255, 144, 5),
            (249, 83, 11),
            (255, 0, 0)
        )
        if level > 0:
            self.progress_rect = pygame.Rect(
                self.x + 12, self.y + 11, 20 * self.level + 9 * (
                    self.level - 1), 30)

    def draw(self, win: pygame.Surface):
        if self.level > 0:
            pygame.draw.rect(
                win, self.colors[self.level - 1], self.progress_rect)
        win.blit(self.title, self.title_pos)
        win.blit(self.image, self.rect)
        win.blit(self.plus_button.image, self.plus_button.rect)

    def add_level(self):
        if self.level < 5:
            self.level += 1
            self.price = (self.level + 1) * 100
            self.title = self.font.render(
                f"{self.title_text} ({self.price if self.level < 5 else 'max'})",
                True, (0, 0, 0))
            self.title_pos[0] = self.x + (
                self.image.get_width() - self.title.get_width()) // 2
            self.progress_rect = pygame.Rect(self.x + 12, self.y + 11,
                                             20 * self.level + 9 * (
                                                 self.level - 1), 30)

    def clicked(self, position):
        """метод для проверки нажатия на кнопку"""
        return self.plus_button.collidepoint(position)

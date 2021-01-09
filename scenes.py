from core import GameScene, Group, StaticGameObject
from enemies import *
from items import *
import json
from main_character import MainCharacter
from platforms import *
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
        self.main_character = MainCharacter(
            200, 100, self.size, self.damage_upgrade,
            self.reload_upgrade, self.jump_upgrade)
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

        self.min_width = 100
        self.min_height = 50
        self.chunck_height = self.size[1]
        # вероятности спавна монеток (0, 1)
        self.bronze_coin_spawn = 1
        self.silver_coin_spawn = 0
        self.golden_coin_spawn = 0

        # вероятности спавна врагов (0, 1)
        self.medusa_spawn = 1
        self.gin_spawn = 0
        self.eye_spawn = 0
        self.dragon_spawn = 0

    def spawn_chuck(self, start_y=0):
        """метод для спавна игрового чанка"""
        totalh = random.randrange(-50, 100)
        while totalh < self.size[1]:
            totalw = random.randrange(-50, 100)
            height = random.randrange(self.min_height, self.min_height * 2)
            while totalw < self.size[0]:
                width = random.randrange(self.min_width, self.min_width * 2)
                y_offset = random.randrange(-self.min_height, self.min_height)
                self.spawn_platform(totalw, totalh + start_y + y_offset)
                totalw += width
            totalh += height
        self.min_width += 1
        self.min_height += 1

    def generate_chuncks(self):
        """метод для генерации чанков в процессе прохождения вверх"""
        self.chunck_height += self.offset
        if self.chunck_height >= self.size[1]:
            self.spawn_chuck(-self.size[1])
            self.chunck_height = 0
        self.spawn_enemies()

    def spawn_platform(self, x: int, y: int):
        """метод для генерации платформы"""
        if random.choice((True, True, True, False)) and 0 <= x < self.size[0] - 65:
            platform = Platform(
                x, y, "assets/platforms/platform72.png", self.size)
            self.platforms.add(platform)
            if random.random() > 0.8:
                self.spawn_objects(platform, x, y)

    def spawn_objects(self, platform: Platform, x: int, y: int):
        """метод для спавна игровых объектов в сцене"""
        if random.choice((True, False)):
            item = self.spawn_item(x, y)
        else:
            item = self.spawn_coin(x, y)
        platform.add_item(item)
        self.items.add(item)

    def spawn_item(self, x, y):
        """метод для спавна предмета"""
        value = random.random()
        item = Spring(x + 10, y - 10, self.size)
        if 0.2 < value < 0.3:
            item = PropellerHat(x + 10, y - 30, self.size, self.hat_upgrade)
        elif 0.3 < value < 0.4:
            item = Trampoline(x, y - 15, self.size)
        elif 0.4 < value < 0.5:
            item = Jetpack(x + 13, y - 45, self.size, self.jetpack_upgrade)
        elif 0.5 < value < 0.6:
            item = Magnet(x + 10, y - 25, self.size, self.magnet_upgrade)
        elif 0.6 < value < 0.7 and self.score > 5000:
            item = Shield(x + 10, y - 25, self.size, self.shield_upgrade)
        elif 0.7 < value < 0.8 and self.score > 10000:
            item = Rocket(x + 10, y - 35, self.size, self.rocket_upgrade)
        elif 0.8 < value < 0.9 and self.score > 5000:
            item = Hole(x, y, self.size)
        return item

    def spawn_coin(self, x, y):
        """метод для спавна монеток"""
        value = random.random()
        item = BronzeCoin(x + 10, y - 25, self.size)
        if self.silver_coin_spawn < value <= self.golden_coin_spawn:
            item = GoldenCoin(x + 10, y - 25, self.size)
        elif self.bronze_coin_spawn < value < self.silver_coin_spawn:
            item = SilverCoin(x + 10, y - 25, self.size)
        return item

    def update_coin_spawn(self):
        """метод для изменения шанса спавна монеток с увеличением высоты"""
        if self.score > 17500:
            self.golden_coin_spawn = 1
            self.silver_coin_spawn = 0.25
            self.bronze_coin_spawn = 0.025
        elif self.score > 10000:
            self.golden_coin_spawn = min(self.golden_coin_spawn + 0.0025, 0.9)
            self.silver_coin_spawn = max(self.silver_coin_spawn - 0.001, 0.4)
            self.bronze_coin_spawn = max(self.bronze_coin_spawn - 0.002, 0.1)
        elif self.score > 5000:
            self.silver_coin_spawn = min(self.silver_coin_spawn + 0.0025, 0.9)
            self.bronze_coin_spawn = max(self.bronze_coin_spawn - 0.001, 0.4)

    def spawn_enemies(self):
        """метод для спавна врагов"""
        diff = random.randrange(1500, 2500)
        if self.score > 7000 and self.score - self.enemy_height > diff:
            value = random.random()
            x_pos = random.randrange(0, self.size[0])
            enemy = Medusa(x_pos, -50, self.size, self.items)
            if self.eye_spawn < value <= self.dragon_spawn:
                enemy = Dragon(x_pos, -50, self.size, self.items)
            elif self.gin_spawn < value <= self.eye_spawn:
                enemy = FlyingEye(x_pos, -50, self.size, self.items)
            elif self.medusa_spawn < value <= self.gin_spawn:
                enemy = Gin(x_pos, -50, self.size, self.items)
            self.enemy_height = self.score
            self.enemies.add(enemy)

    def update_enemies_spawn(self):
        """метод для обновления шанса спавна врагов с увеличением высоты"""
        if self.score > 16000:
            self.dragon_spawn = min(self.dragon_spawn + 0.025, 0.9)
            self.eye_spawn = max(self.eye_spawn - 0.001, 0.4)
            self.gin_spawn = max(self.gin_spawn - 0.002, 0.25)
            self.medusa_spawn = max(self.medusa_spawn - 0.004, 0.1)
        elif self.score > 12500:
            self.eye_spawn = min(self.eye_spawn + 0.025, 0.9)
            self.gin_spawn = max(self.gin_spawn - 0.001, 0.4)
            self.medusa_spawn = max(self.medusa_spawn - 0.001, 0.2)
        elif self.score > 9000:
            self.gin_spawn = min(self.gin_spawn + 0.025, 0.9)
            self.medusa_spawn = max(self.medusa_spawn - 0.001, 0.4)

    def check_collisions(self):
        """метод для обработки всех столкновений"""
        ignore = (self.main_character.shield, self.main_character.magnet)
        for group in (self.platforms, self.items, self.enemies):
            for coll in group.get_collisions(self.main_character, ignore):
                self.scroll_down = self.main_character.process_collision(coll)
            self.main_character.process_magnet_collisions(group)
        if self.main_character.collides(self.bottom_rect) or self.main_character.game_over:
            self.game_over()

    def redraw(self, win):
        """метод для отрисовки сцены"""
        win.fill((255, 255, 255))
        relative_background_y = self.bg_pos % self.bg_height
        win.blit(self.background, (0, relative_background_y - self.bg_height))
        if relative_background_y < self.size[1]:
            win.blit(self.background, (0, relative_background_y))
        self.platforms.draw(win)
        self.main_character.draw(win)
        self.items.draw(win, sort=lambda sprite: sprite.draw_order)
        self.enemies.draw(win)
        win.blit(self.render_score(), (10, 10))
        money = self.render_money()
        money_x = self.size[0] - money.get_width() - 10
        win.blit(money, (money_x, 10))
        self.coin.set_pos((money_x - self.coin.rect.w - 10, 15))

    def handle_events(self):
        """метод для обработки событий сцены"""
        self.generate_chuncks()
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
        self.main_character.update(self.enemies)
        self.enemies.update(self.offset if self.scroll_down else 0)
        self.items.update(self.offset if self.scroll_down else 0,
                          player=self.main_character)
        self.update_coin_spawn()
        self.update_enemies_spawn()

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
        if event.key == pygame.K_ESCAPE:
            self.manager.load_scene(5)
            self.close()
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
        self.reload_upgrade = data.get(self.RELOAD_KEY).get(
            str(self.reload_level))
        self.jump_upgrade = data.get(self.JUMP_KEY).get(
            str(self.jump_level))
        self.rocket_upgrade = data.get(self.ROCKET_KEY).get(
            str(self.rocket_level))

    def game_over(self):
        """метод для завершения уровня"""
        self.manager.load_scene(2)
        self.lose_sound.play()
        self.mute_sounds()
        self.close()

    def mute_sounds(self):
        """метод для отсановки всех звуков"""
        for sprite in self.items:
            if hasattr(sprite, "sound"):
                sprite.sound.stop()
        self.main_character.mute()

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
        self.reset_values()
        self.main_character.reset()
        self.platforms.clear()
        self.items.clear()
        self.enemies.clear()
        self.main_character.set_pos((200, 100))
        self.items.add(self.coin)

    def reset_values(self):
        """метод для сброса значений уровня"""
        self.score = 0
        self.bg_pos = -self.background.get_height() + self.size[1]
        self.offset = 5
        self.min_width = 100
        self.min_height = 50
        self.chunck_height = self.size[1]
        self.scroll_down = False
        self.move_right = False
        self.move_left = False
        self.reset_spawn_values()

    def reset_spawn_values(self):
        """метод для сброса вероятностей спавна предметов"""
        self.bronze_coin_spawn = 1
        self.silver_coin_spawn = 0
        self.golden_coin_spawn = 0
        self.medusa_spawn = 1
        self.gin_spawn = 0
        self.eye_spawn = 0
        self.dragon_spawn = 0

    def revive_game(self, clear_groups=True):
        """метод для продолжения игры после проигрыша"""
        if clear_groups:
            self.enemies.clear()
            for item in self.items:
                if isinstance(item, Hole):
                    item.delete()
        self.main_character.set_pos((250, 150))
        self.main_character.game_over = False
        self.move_left = False
        self.move_right = False
        self.show(spawn_chuck=False)

    def show(self, spawn_chuck=True):
        self.load_upgrades()
        self.main_character.load_upgrades(
            self.damage_upgrade, self.reload_upgrade, self.jump_upgrade)
        if spawn_chuck:
            self.spawn_chuck()
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
        self.sub_font = pygame.font.SysFont("cambriacambriamath", 30)
        self.restart_button = StaticGameObject(228, 230,
                                               "assets/ui/restart_button.png",
                                               self.size, convert_alpha=True)
        self.menu_button = StaticGameObject(228, 300,
                                            "assets/ui/menu_button.png",
                                            self.size, convert_alpha=True)
        self.continue_button = StaticGameObject(210, 480,
                                                "assets/ui/continue_button.png",
                                                self.size, convert_alpha=True)
        self.background = pygame.image.load(
            "assets/ui/game_over_bg.jpg").convert()
        self.revive_dialog = pygame.image.load(
            "assets/ui/revive_dialog.png").convert_alpha()
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        self.click_sound.set_volume(0.6)
        self.revive_price = 250
        self.revive_countdown = 5 * self.FPS
        self.revive_happened = False
        self.draw_revive = False
        self.money_collected = 0

    def redraw(self, win):
        win.blit(self.background, (50, 50))
        highscore = self.font.render(
            f"Highscore: {self.highscore}", True, "black")
        current_score = self.font.render(f"Score: {self.score}", True, "black")
        money = self.font.render(f"Money collected: {self.money_collected}",
                                 True, "black")
        win.blit(highscore, ((self.size[0] - highscore.get_width()) // 2, 65))
        win.blit(current_score,
                 ((self.size[0] - current_score.get_width()) // 2, 115))
        win.blit(money, ((self.size[0] - money.get_width()) // 2, 165))
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
            self.money_collected = money_to_add

    def show_revive_dialog(self):
        """метод для показа диалога возрождения"""
        if (money := self.get_game_value(self.MONEY_KEY)) != -1 and money >= self.revive_price:
            if not self.revive_happened:
                self.draw_revive = True

    def draw_revive_dialog(self, win: pygame.Surface):
        """метод для отрисовки диалога возрождения"""
        if self.revive_countdown > 0:
            win.blit(self.revive_dialog, (50, 375))
            cost_text = self.sub_font.render(
                f"It costs {self.revive_price}$", True, (0, 0, 0))
            time_remains = self.font.render(str(
                self.revive_countdown // self.FPS + 1), True, (0, 0, 0))
            win.blit(cost_text, (
                (self.revive_dialog.get_width() - cost_text.get_width()) // 2 + 50, 437))
            win.blit(self.continue_button.image, self.continue_button.rect)
            win.blit(time_remains, (370, 480))
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
        self.items = (
            (ShopItem(75, 25, self.size, "Magnet", level=self.magnet_level),
             self.MAGNET_KEY),
            (ShopItem(75, 150, self.size, "Shield", level=self.shield_level),
             self.SHIELD_KEY),
            (ShopItem(75, 275, self.size, "Hat", level=self.hat_level),
             self.HAT_KEY),
            (ShopItem(75, 400, self.size, "Jetpack", level=self.jetpack_level),
             self.JETPACK_KEY),
            (ShopItem(325, 25, self.size, "Damage", level=self.damage_level),
             self.DAMAGE_KEY),
            (ShopItem(325, 150, self.size, "Reload", level=self.reload_level),
             self.RELOAD_KEY),
            (ShopItem(325, 275, self.size, "Jump", level=self.jump_level),
             self.JUMP_KEY),
            (ShopItem(325, 400, self.size, "Rocket", level=self.rocket_level),
             self.ROCKET_KEY)
        )
        self.click_sound = pygame.mixer.Sound("assets/sounds/button_press.wav")
        self.upgrade_sound = pygame.mixer.Sound(
            "assets/sounds/upgrade_unlock.wav")
        self.background = pygame.image.load("assets/ui/shop_bg.jpg").convert()
        self.click_sound.set_volume(0.4)
        self.upgrade_sound.set_volume(0.3)

    def redraw(self, win):
        win.blit(self.background, (0, 0))
        win.blit(self.menu_button.image, self.menu_button.rect)
        for item, _ in self.items:
            item.draw(win)
        money = self.font.render(f"{self.get_game_value(self.MONEY_KEY)}$",
                                 True, (0, 0, 0))
        win.blit(money, (self.size[0] - money.get_width() - 50, 535))

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
                for item, key in self.items:
                    if item.clicked(event.pos):
                        self.purchase_upgrade(key, item)

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
                                  y + self.title.get_height() + 11))
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


class PauseMenu(GameOverMenu):
    """Класс для создания меню паузы"""

    def __init__(self, display, manager, fps):
        super().__init__(display, manager, fps)
        self.background = pygame.image.load("assets/ui/pause_bg.png").convert()
        self.continue_button = StaticGameObject(
            228, 300, "assets/ui/continue_button.png", self.size)
        self.menu_button = StaticGameObject(
            228, 375, "assets/ui/menu_button.png", self.size)
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        self.click_sound.set_volume(0.6)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.continue_button.collidepoint(event.pos):
                    self.manager.load_scene(3, clear_groups=False)
                    self.close()
                if self.menu_button.collidepoint(event.pos):
                    self.manager.load_scene(0)
                    self.close()

    def redraw(self, win: pygame.Surface):
        win.blit(self.background, (50, 50))
        win.blit(self.continue_button.image, self.continue_button.rect)
        win.blit(self.menu_button.image, self.menu_button.rect)

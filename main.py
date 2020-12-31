import pygame
from scenes import *


class Game():
    """Главный класс игры, ответственный за управление сценами"""

    def __init__(self, width: int, height: int, fps=60):
        pygame.init()
        pygame.font.init()
        self.SCREEN_SIZE = (width, height)
        self.display = pygame.display.set_mode(self.SCREEN_SIZE)
        self.FPS = fps
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Doodle Jump")
        pygame.display.set_icon(
            pygame.image.load("assets/base_character72.png").convert_alpha())

        self.main_menu = MainMenu(self.display, self.FPS)
        self.level = Level(self.display, self.FPS)
        self.game_over_menu = GameOverMenu(self.display, self.FPS)
        self.shop = ShopMenu(self.display, self.FPS)

    def handle_events(self):
        self.switch_scenes()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def switch_scenes(self):
        if self.level.game_over:
            self.game_over_menu.set_score(self.level.get_score())
            self.game_over_menu.update_money(self.level.get_collected_money())
            self.game_over_menu.show()
        if self.main_menu.load_shop:
            self.shop.show()
        if self.game_over_menu.load_main_menu or self.shop.load_main_menu:
            self.shop.load_main_menu = False
            self.game_over_menu.revive_happened = False
            self.main_menu.show()
        if self.game_over_menu.revive_game:
            self.level.revive_game()
        elif self.main_menu.load_level or self.game_over_menu.restart_game:
            self.level.restart()
            self.level.show()

    def run(self):
        self.main_menu.show()
        while True:
            self.handle_events()
            pygame.display.update()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    game = Game(width=600, height=600)
    game.run()

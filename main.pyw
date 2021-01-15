import json
import pygame
from scenes import *


class Game():
    """Главный класс игры, ответственный за управление сценами"""

    def __init__(self, width: int, height: int, fps=60):
        pygame.init()
        pygame.font.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(32)
        self.SCREEN_SIZE = (width, height)
        self.display = pygame.display.set_mode(self.SCREEN_SIZE)
        self.FPS = fps
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Doodle Jump")
        pygame.display.set_icon(pygame.image.load(
            "assets/character/character0.png").convert_alpha())

        self.main_menu = MainMenu(self.display, self, self.FPS)
        self.level = Level(self.display, self, self.FPS)
        self.game_over_menu = GameOverMenu(self.display, self, self.FPS)
        self.shop = ShopMenu(self.display, self, self.FPS)
        self.pause_menu = PauseMenu(self.display, self, self.FPS)
        self.settings_menu = SettingsMenu(self.display, self, self.FPS)

        self.load_main_menu = True
        self.load_level = False
        self.load_game_over_menu = False
        self.revive_level = False
        self.load_shop = False
        self.load_pause_menu = False
        self.load_settings = False
        self.clear_groups = True

        self.level_music_playing = True
        self.MUSIC_KEY = "music"
        self.volume_ratio = 1

    def update_sound_volume(self):
        """метод для получения громкости звука"""
        try:
            with open("values.json", "r", encoding="u8") as f:
                data = json.load(f)
        except Exception as err:
            print(err)
            self.volume_ratio = 1
        else:
            self.volume_ratio = data.get(self.MUSIC_KEY, 1)

    def apply_sound_volume(self):
        """метод для установки громкости музыки"""
        if self.level_music_playing:
            pygame.mixer.music.set_volume(0.2 * self.volume_ratio)
        else:
            pygame.mixer.music.set_volume(0.25 * self.volume_ratio)

    def switch_scenes(self):
        """метод для переключения сцен в зависимости от флагов"""
        if self.load_main_menu:
            self.level.stop_sounds()
            self.main_menu.show()
        elif self.load_level:
            self.level.restart()
            self.level.show()
        elif self.revive_level:
            self.level.revive_game(self.clear_groups)
        elif self.load_game_over_menu:
            self.game_over_menu.set_score(self.level.get_score())
            self.game_over_menu.update_money(self.level.get_collected_money())
            self.game_over_menu.show()
        elif self.load_shop:
            self.shop.show()
        elif self.load_pause_menu:
            self.pause_menu.show()
        elif self.load_settings:
            self.settings_menu.show()

    def play_music(self):
        """метод для воспроизведения фоновой музыки в зависимости от сцены"""
        if self.load_main_menu or self.load_shop or self.load_settings:
            if self.level_music_playing:
                pygame.mixer.music.load("assets/music/menu_music.ogg")
                pygame.mixer.music.set_volume(0.2 * self.volume_ratio)
                pygame.mixer.music.play(-1)
                self.level_music_playing = False
        elif not self.level_music_playing:
            pygame.mixer.music.load("assets/music/level_music.mp3")
            pygame.mixer.music.set_volume(0.25 * self.volume_ratio)
            pygame.mixer.music.play(-1)
            self.level_music_playing = True

    def load_scene(self, index, clear_groups=True):
        """метод для загрузки сцены"""
        self.reset_flags()
        if index == 0:
            self.load_main_menu = True
        elif index == 1:
            self.load_level = True
        elif index == 2:
            self.load_game_over_menu = True
        elif index == 3:
            self.revive_level = True
        elif index == 4:
            self.load_shop = True
        elif index == 5:
            self.load_pause_menu = True
        elif index == 6:
            self.load_settings = True
        self.clear_groups = clear_groups
        self.update_sound_volume()
        self.apply_sound_volume()

    def reset_flags(self):
        """метод для сброса значений флагов загрузки сцен"""
        self.load_main_menu = False
        self.load_level = False
        self.load_game_over_menu = False
        self.load_shop = False
        self.revive_level = False
        self.load_pause_menu = False
        self.load_settings = False

    def run(self):
        self.update_sound_volume()
        self.apply_sound_volume()
        while True:
            self.play_music()
            self.switch_scenes()


if __name__ == '__main__':
    game = Game(width=600, height=600)
    game.run()

import pygame
from scenes import MainMenu, Level


class Game():
    def __init__(self, width: int, height: int, fps=60):
        pygame.init()
        self.SCREEN_SIZE = (width, height)
        self.display = pygame.display.set_mode(self.SCREEN_SIZE)
        self.FPS = fps
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Doodle Jump")

        self.main_menu = MainMenu(self.display, self.FPS)
        self.level = Level(self.display, self.FPS)

    def redraw(self, win):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                self.handle_keyboard_events(event)

    def handle_keyboard_events(self, event):
        if event.key == pygame.K_SPACE:
            self.main_menu.show()
        if event.key == pygame.K_RETURN:
            self.level.show()

    def run(self):
        while True:
            self.handle_events()
            self.redraw(self.display)
            pygame.display.update()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    game = Game(width=600, height=600)
    game.run()

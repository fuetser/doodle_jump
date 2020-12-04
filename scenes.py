from core import GameScene
import pygame


class MainMenu(GameScene):
    def __init__(self, display: pygame.Surface, fps=60):
        super(MainMenu, self).__init__(display, fps)
        self.background = pygame.image.load("assets/background.png")
        self.bg_pos = [0, 0]
        self.scroll_up = False
        self.scroll_down = False
        self.parallax_coefficient = 0.25

    def redraw(self, win):
        win.fill((255, 255, 255))
        win.blit(self.background, self.bg_pos)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                self.handle_keyboard_events(event)
            if event.type == pygame.KEYUP:
                self.scroll_up = False
                self.scroll_down = False

        if self.scroll_up:
            self.bg_pos[1] -= 5
        elif self.scroll_down:
            self.bg_pos[1] += 5

    def handle_keyboard_events(self, event):
        if event.key == pygame.K_ESCAPE:
            self.close()
        if event.key == pygame.K_UP:
            # self.scroll(-20)
            self.scroll_up = True
        if event.key == pygame.K_DOWN:
            # self.scroll(20)
            self.scroll_down = True

    def scroll(self, offset: int):
        # y = self.background.get_rect()[1]
        # if y + offset > self.background.get_height():
            # self.bg_pos[1] += offset * self.parallax_coefficient
        self.bg_pos[1] += offset


class Level(GameScene):
    def __init__(self, display: pygame.Surface, fps=60):
        super(Level, self).__init__(display, fps)

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

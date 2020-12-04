import pygame


class GameObject():
    def __init__(self, x_pos: int, y_pos: int):
        self.x = x_pos
        self.y = y_pos

    def move(new_x: int, new_y: int):
        raise NotImplementedError

    @property
    def pos(self):
        return (self.x, self.y)


class GameScene():
    def __init__(self, display: pygame.Surface, fps=60):
        self.display = display
        self.FPS = fps
        self.clock = pygame.time.Clock()
        self.running = True

    def redraw(self, win):
        raise NotImplementedError

    def handle_events(self):
        raise NotImplementedError

    def close(self):
        self.running = False

    def show(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.redraw(self.display)
            pygame.display.update()
            self.clock.tick(self.FPS)

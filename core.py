import pygame


class GameObject(pygame.sprite.Sprite):
    """Абстрактный класс для игровых объектов"""

    def __init__(self, x_pos: int, y_pos: int):
        super(GameObject, self).__init__()
        self.x = x_pos
        self.y = y_pos

    def move(new_x: int, new_y: int):
        """метод для передвижения объекта"""
        raise NotImplementedError

    def draw(self, win: pygame.Surface):
        """метод для отрисовки на переданной поверхности"""
        raise NotImplementedError

    def update_rect(self):
        """метод для обновления положения объекта"""
        self.rect.topleft = self.pos

    def collides(self, rect: pygame.Rect):
        """метод для проверки столкновений с другими объектами"""
        return self.rect.colliderect(rect)

    def set_pos(self, pos: tuple[int, int]):
        """метод для изменения позиции объекта"""
        x_pos, y_pos = pos
        self.x = x_pos
        self.y = y_pos

    @property
    def pos(self) -> tuple[int, int]:
        """метод для получения позиции объекта"""
        return (self.x, self.y)


class GameScene():
    """Абстрактный класс для игровой сцены/меню"""

    def __init__(self, display: pygame.Surface, fps=60):
        # на принятой поверхности происхоит отрисовка сцены
        self.display = display  # объект из функции pygame.display.set_mode()
        self.FPS = fps
        self.clock = pygame.time.Clock()
        self.running = True

    def redraw(self, win: pygame.Surface):
        """метод для отрисовки на заданной поверхности"""
        raise NotImplementedError

    def handle_events(self):
        """метод для обработки событий внутри сцены"""
        raise NotImplementedError

    def close(self):
        """метод для закрытия сцены"""
        self.running = False

    def show(self):
        """метод для запуска сцены"""
        self.running = True
        while self.running:
            self.handle_events()
            self.redraw(self.display)
            pygame.display.update()
            self.clock.tick(self.FPS)

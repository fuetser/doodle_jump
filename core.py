import pygame


class GameObject(pygame.sprite.Sprite):
    """Абстрактный класс для игровых объектов"""
    object_id = 0

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        super(GameObject, self).__init__()
        if convert_alpha:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.screen_width, self.screen_height = screen_size
        self._id = GameObject.object_id
        GameObject.object_id += 1
        self.to_delete = False

    def update(self):
        """метод для обновления положения объекта"""
        raise NotImplementedError

    def collides(self, rect: pygame.Rect):
        """метод для проверки столкновений с другими объектами"""
        return self.rect.colliderect(rect)

    def collidepoint(self, point: tuple[int, int]):
        """Метод для проверки столкновения объекта с точкой"""
        return self.rect.collidepoint(point)

    def set_pos(self, pos: tuple[int, int]):
        """метод для изменения позиции объекта"""
        self.rect.topleft = pos

    def delete(self, *args, **kwargs):
        """метод для удаления спарйта из группы"""
        self.to_delete = True
        self.on_delete(*args, **kwargs)

    def on_delete(self, *args, **kwargs):
        """метод, выполняемый при удалении объекта"""
        pass

    def process_collision(self, item: pygame.sprite.Sprite):
        """метод для обработки столкновения с объетами"""
        raise NotImplementedError

    def __eq__(self, other):
        """метод для сравнения спрайтов"""
        return self._id == other._id

    @property
    def pos(self) -> tuple[int, int]:
        """метод для получения позиции объекта"""
        return self.rect.topleft

    @property
    def x(self) -> int:
        return self.rect.x

    @property
    def y(self) -> int:
        return self.rect.y

    @property
    def top(self) -> int:
        return self.rect.top

    @property
    def bottom(self) -> int:
        return self.rect.bottom


class GameScene():
    """Абстрактный класс для игровой сцены/меню"""

    def __init__(self, display: pygame.Surface, fps=60):
        # на принятой поверхности происхоит отрисовка сцены
        self.display = display  # объект из функции pygame.display.set_mode()
        self.FPS = fps
        self.clock = pygame.time.Clock()
        self.size = (self.display.get_width(), self.display.get_height())
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


class Group():
    """Кастомный класс для организации спрайтов"""

    def __init__(self, *sprites):
        self.sprites = list(sprites)

    def update(self, *args, **kwargs):
        """метод для обновления спрайтов"""
        for sprite in self.sprites:
            sprite.update(*args, **kwargs)
        self.clear_sprites()

    def add(self, sprite: pygame.sprite.Sprite):
        """метод для добавления спрайта в группу"""
        if isinstance(sprite, pygame.sprite.Sprite):
            self.sprites.append(sprite)
        else:
            raise TypeError("Wrong type for argument")

    def remove(self, sprite: pygame.sprite.Sprite):
        """метод для удаления спрайта из группы"""
        if isinstance(sprite, pygame.sprite.Sprite):
            for index, value in tuple(enumerate(self.sprites))[::-1]:
                if sprite == value:
                    self.sprites.pop(index)
                    break
        else:
            raise TypeError("Wrong type for argument")

    def clear_sprites(self):
        """метод для удаления помеченных спрайтов"""
        for index, sprite in tuple(enumerate(self.sprites))[::-1]:
            if sprite.to_delete:
                self.sprites.pop(index)

    def draw(self, win):
        """метод для отрисовки спрайтов из группы"""
        for sprite in self.sprites:
            win.blit(sprite.image, sprite.rect)

    def __getitem__(self, index):
        try:
            return self.sprites[index]
        except IndexError:
            raise IndexError(f"Wrong index supplied: {index}")

    def __len__(self):
        return len(self.sprites)

    def clear(self):
        """Метод для удаления всех спрайтов из группы"""
        self.sprites.clear()

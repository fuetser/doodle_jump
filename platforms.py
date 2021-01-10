from core import StaticGameObject
import pygame


class Platform(StaticGameObject):
    """Абстрактный класс для создания платформ"""
    image = None

    def __init__(self, x, y, image_path, screen_size, convert_alpha=True):
        self.__class__.load_image(image_path, convert_alpha)
        super().__init__(
            x, y, image_path, screen_size, convert_alpha, load_image=True)
        self.item = None
        self.count = 0
        self.chek = False

    @classmethod
    def load_image(cls, image_path, convert_alpha):
        if cls.image is None:
            if convert_alpha:
                cls.image = pygame.image.load(image_path).convert_alpha()
            else:
                cls.image = pygame.image.load(image_path).convert()

    def update(self, scroll: int, moving=False):
        """метод для обновления спрайта"""
        self.scroll(scroll)
        if self.count == 51:
            self.chek = True
        if self.count == 0:
            self.chek = False
        if moving == True and self.chek == False:
            self.rect.x += 3
            self.count += 1
        elif moving == True and self.chek == True:
            self.rect.x -= 3
            self.count -= 1
        if self.y > self.screen_height:
            self.delete()

    def scroll(self, offset: int):
        """метод для сдвига платформы вниз по экрану"""
        self.rect.y += offset

    def add_item(self, item: pygame.sprite.Sprite):
        """метод для добавления предмета к платформе"""
        if isinstance(item, pygame.sprite.Sprite) and self.item is None:
            self.item = item
        else:
            raise TypeError("Wrong argument supplied")


import pygame
from pygame.sprite import Sprite


class Background(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.image = pygame.image.load('images/space.bmp')
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = 0,0


    def blitme(self):
        self.screen.blit(self.image, self.rect)
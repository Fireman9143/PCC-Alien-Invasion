import pygame
from pygame.sprite import Sprite


class Rocket(Sprite):
    '''a class to manage rockets'''
    def __init__(self, ai_game) -> None:
        '''create a rocket object at the ships current position'''
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.rocket_color
        #create a bullet rect at (0, 0), set correct position
        self.rect = pygame.Rect(0, 0, self.settings.rocket_width, self.settings.rocket_height)
        self.rect.midtop = ai_game.ship.rect.midtop
        #stores the rockets position as a float
        self.y = float(self.rect.y)
    
    def update(self):
        '''move the rocket up the screen'''
        self.y -= self.settings.rocket_speed
        self.rect.y = self.y
    
    def draw_rocket(self):
        '''draw the rocket to the screen'''
        pygame.draw.rect(self.screen, self.color, self.rect)
import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    '''class ship is a class to manage the ship'''
    def __init__(self, ai_game) -> None:
        '''initialize the ship and set the starting position'''
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        #load the ship image and rect
        self.image = pygame.image.load('images/ship2.bmp')
        self.rect = self.image.get_rect()
        #start each new ship at the bottom center
        self.rect.midbottom = self.screen_rect.midbottom
        #stores a float for the ships exact horizontal position
        self.x = float(self.rect.x)
        #movement flags start with a ship that is not moving
        self.moving_right = False
        self.moving_left = False


    def update(self):
        '''update the ships position based on the movement flags'''
        #update the ships x value not the rect
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        #update the rect object from self.x
        self.rect.x = self.x


    def center_ship(self):
        '''centers the ship'''
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)


    def blitme(self):
        '''draw the ship at its current location'''
        self.screen.blit(self.image, self.rect)
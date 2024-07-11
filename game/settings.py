import pygame
from background import Background

class Settings:
    '''a class to store all settings for alien invasion'''
    def __init__(self) -> None:
        '''initialize game static settings'''
        #screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        #ship settings
        self.ship_limit = 3
        #bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (228, 16, 4)
        self.bullets_allowed = 20
        #rocket settings
        self.rocket_width = 30
        self.rocket_height = 20
        self.rocket_color = (200, 200, 200)
        self.rockets_allowed = 1
        #alien settings
        self.fleet_drop_speed = 10
        #how quickly the game speeds up
        self.speedup_scale = 1.1
        #How quickly alien point values increase
        self.score_scale = 1.5
        self.initialize_dynamic_settings()


    def initialize_dynamic_settings(self):
        '''initialize settings the change throughout the game'''
        self.ship_speed = 2
        self.bullet_speed = 8.0
        self.rocket_speed = 10.0
        self.alien_speed = 1.0
        #scoring setting
        self.alien_points = 50
        #fleet_direction of 1 = right, -1 = left
        self.fleet_direction = 1


    def increase_speed(self):
        '''increase speed settings'''
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.rocket_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points*self.score_scale)
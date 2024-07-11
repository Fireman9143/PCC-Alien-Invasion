import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from rocket import Rocket
from alien import Alien
from background import Background
from time import sleep
from game_stats import GameStats
from button import Button


class AlienInvasion:
    '''overall class to manage game assets and behavior'''
    def __init__(self):
        '''initialize game and create game resources'''
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption('AlienInvasion')
        #create an instance to store game stats
        self.stats = GameStats(self)
        #create background from Background class
        self.background = Background(self)
        #create instance of ship
        self.ship = Ship(self)
        #create group of bullets, rockets, and aliens
        self.bullets = pygame.sprite.Group()
        self.rockets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        #calls _create_fleet function to populate aliens
        self._create_fleet()
        self.clock = pygame.time.Clock()
        #start alien invasion in an inactive state
        self.game_active = False
        self.play_button = Button(self, 'Play')
        

    def run_game(self):
        '''start the main loop fort the game'''
        while True:
            self._check_events()  
            if self.game_active:        
                self.ship.update()
                self._update_rockets()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)


    def _check_events(self):
        '''respond to key presses and mouse events'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        '''start a new game when the user clicks play'''
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #reset game settings
            self.settings.initialize_dynamic_settings()
            #reset game stats
            self.stats.reset_stats()
            self.game_active = True
            #get rid of remaining bullets and aliens
            self.rockets.empty()
            self.bullets.empty()
            self.aliens.empty()
            #create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            #hide cursor
            pygame.mouse.set_visible(False)
    

    def _check_keydown_events(self, event):
        '''check for key presses'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_r:
            self._fire_rocket()


    def _check_keyup_events(self, event):
        '''check for key releases'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _fire_bullet(self):
        '''create a new bullet and add it to the bullets group'''
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    

    def _fire_rocket(self):
        '''create a new rocket and add it to the rockets group'''
        if len(self.rockets) < self.settings.rockets_allowed:
            new_rocket = Rocket(self)
            self.rockets.add(new_rocket)


    def _update_bullets(self):
        '''update position of bullets and get rid of old bullets'''
        #update bullet positon
        self.bullets.update()
        #get rid of bullets that have disapered
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()


    def _update_rockets(self):
        '''update position of rocket and get rid of old rockets'''
        #update rocket position
        self.rockets.update()
        #get rid of rockets that disappeared
        for rocket in self.rockets.copy():
            if rocket.rect.bottom <= 0:
                self.rockets.remove(rocket)
        self._check_rocket_alien_collisions()


    def _check_bullet_alien_collisions(self):
        '''respond to bullet alien colission'''
        #remove any bullets and aliens that have collided
        collisions1 = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if not self.aliens:
            #destroy bullets and create new fleet
            self.rockets.empty()
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()


    def _check_rocket_alien_collisions(self):
        '''respond to rocket alien colissions'''
        #remove any rockets and aliens that have collided
        collisions2 = pygame.sprite.groupcollide(self.rockets, self.aliens, True, True)
        if not self.aliens:
            #destroy rocket and create new fleet
            self.rockets.empty()
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()


    def _create_fleet(self):
        '''create the fleet of aliens'''
        #create an alien and keep adding aliens until there is no room left
        #spacing between aliens is one alien width and one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x,current_y = alien_width,alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            #finished a row, reset x and increment y
            current_x = alien_width
            current_y += 2 * alien_height


    def _create_alien(self, x_position, y_position):
        '''create alien and place it in the fleet'''
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)


    def _update_aliens(self):
        '''check if alien fleet is at edge then update positions'''
        self._check_fleet_edges()
        self.aliens.update()
        #look for alien ship collisons
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        #look for aliens hitting th bottom of the screen
        self._check_aliens_bottom()


    def _ship_hit(self):
        '''respond to ship being hit by alien'''
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            #get rid of any remaining bullets and aliens
            self.rockets.empty()
            self.bullets.empty()
            self.aliens.empty()
            #create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)


    def _check_fleet_edges(self):
        '''respond appropriately if any aliens have reached an edge'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        '''drop the entire fleet and change the fleets direction'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _check_aliens_bottom(self):
        '''check if any aliens of reached the bottom of the screen'''
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #treat this the same as if the ship got hit
                self._ship_hit()
                break


    def _update_screen(self):
        '''update images on the screen and flip to a new screen'''
        self.screen.fill(self.settings.bg_color)
        self.background.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for rocket in self.rockets.sprites():
            rocket.draw_rocket()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        #draw the play button when the game is inactive
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()


if __name__ == "__main__":
    '''make a game instance and run the game'''
    ai = AlienInvasion()
    ai.run_game()
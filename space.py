import sys
from time import sleep
from pathlib import Path
import json
import pygame
from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard
import soundFX as se


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self) -> None:
        """InitialDrawize the game and create game resources"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        #For full screen mode, these 3 lines instead of the self.screen below
        #self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        #self.settings.screen_width = self.screen.get_rect().width
        #self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        #Create instance to store game stats and create scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        #Set the background color
        self.bg_color = (230, 230, 230)
        #Start game in inactive state
        self.game_active = False
        #Make the play button
        self.play_button = Button(self, "Play")
        pygame.mixer.music.load("/home/fireman9143/MyCode/721472__victor_natas__boss-fight.wav")
        pygame.mixer.music.play(-1)


    def run_game(self):
        "Start main game loop"
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)


    def _check_events(self):
        """Responds to keyboard and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._close_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        """Start a new game when player clicks on play button"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #Reset game settings
            self.settings.initialize_dynamic_settings()
            #Start new game
            self._start_game()


    def _start_game(self):
        #Reset game stats
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True
        #Get rid of bullets and aliens
        self.bullets.empty()
        self.aliens.empty()
        #Create new fleet and center ship
        self._create_fleet()
        self.ship.center_ship()
        #Hide mouse cursor
        pygame.mouse.set_visible(False)


    def _close_game(self):
        """Save high score and exit"""
        saved_high_score = self.stats.save_high_score()
        if self.stats.high_score > saved_high_score:
            path = Path("highest_score.json")
            contents = json.dumps(self.stats.high_score)
            path.write_text(contents)
        sys.exit()


    def _check_keydown_events(self, event):
        """Respond to key presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left =  True
        elif event.key ==  pygame.K_p or event.key == pygame.K_RETURN:
            self._start_game()
        elif event.key == pygame.K_q:
            self._close_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    def _check_keyup_events(self, event):
        """Respond to key release"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _fire_bullet(self):
        """Create new bullet and add to bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            se.bullet_sound.play()


    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets"""
        #Update bullet position
        self.bullets.update()
        #Get rid of bullets that are off screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collision()


    def _check_bullet_alien_collision(self):
        """Respond to bullet-alien collisions"""
        #Remove any bullets and aliens that collide
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            se.alien_sound.play()
        if not self.aliens:
            #Destroy existing bullets and make new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            #Increase level
            self.stats.level += 1
            self.sb.prep_level()


    def _create_fleet(self):
        """Create fleet of aliens"""
        #Make an alien and keep adding until no room left
        #Space between aliens in one alien width and height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3*alien_height):
            while current_x < (self.settings.screen_width - 2*alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2*alien_width
            #Finished a row, reset x and increment y
            current_x = alien_width
            current_y += 2*alien_height


    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)


    def _update_aliens(self):
        """Check if aliens are at edge then update positions"""
        self._check_fleet_edges()
        self.aliens.update()
        #Look for alien-ship collision
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        #Look for alien hitting bottom of screen
        self._check_aliens_bottom()


    def _check_aliens_bottom(self):
        """Check if aliens have reached bottom of screen"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #Treat the same as if ship was hit
                self._ship_hit()
                break


    def _ship_hit(self):
        """Respond to ship being hit by alien"""
        if self.stats.ships_left > 0:
            #Decrement ships_left and update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            #Get rid of remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()
            #Create new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()
            #Pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)


    def _check_fleet_edges(self):
        """Respond if alien reaches edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """Drop entire fleet and change its direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _update_screen(self):
        """Update images and flip new screen"""
        #Redraw the screen during each pass of the loop
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        #Draw scoreboard
        self.sb.show_score()
        #Draw play button if inactive
        if not self.game_active:
            self.play_button.draw_button()
        #Make most recent screen drawn visible
        pygame.display.flip()


if __name__ == "__main__":
    #Make an instance of the game and run it
    ai = AlienInvasion()
    ai.run_game()
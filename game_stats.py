from pathlib import Path
import json


class GameStats:
    """Track stats for alien invasion game"""

    def __init__(self, ai_game) -> None:
        """Initialize stats"""
        self.settings = ai_game.settings
        self.reset_stats()
        #High score should never be reset
        self.high_score = self.save_high_score()


    def save_high_score(self):
        """Checks high score and saves highest score"""
        path = Path("highest_score.json")
        try:
            contents = path.read_text()
            return json.loads(contents)
        except FileNotFoundError:
            return 0


    def reset_stats(self):
        """Initialize stats that can change during game"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
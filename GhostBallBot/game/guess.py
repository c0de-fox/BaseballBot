import math

# Import game functions
from database.models import (
    GameModel as Game,
    GuessModel as Guess,
    PlayerModel as Player,
)


class ProcessGuess:
    def __init__(self, game, **kwargs):
        self.game_manager = game

        self.message = kwargs.get("message")
        self.pitch_value = kwargs.get("pitch_value")
        self.difference = kwargs.get("difference")
        self.difference_score = kwargs.get("difference_score")
        self.guesses = kwargs.get("guesses")
        self.guess = kwargs.get("guess")

    def get_guesses(self):
        # Get all guesses for this game as a list of combo Guess + Player models,
        # excluding invalid results, from lowest to highest
        # http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#joins-and-subqueries
        self.guesses = (
            Guess.select(
                Guess.guess,
                Player.player_id,
                Player.player_name,
                Player.total_points,
            )
            .join(Player)
            .where(
                (Guess.game == self.game_manager.game.game_id)
                & (Guess.guess > 0)
                & (Guess.player.player_id == Player.player_id)
            )
            .order_by(Guess.guess)
        )
        return self.guesses

    def update_difference_value(self):
        # Update player's difference in guessed value
        Guess.update({"difference": self.difference}).where(
            (Guess.game.game_id == self.game_manager.game.game_id)
            & (Guess.player.player_id == self.guess.player.player_id)
            & (Guess.guess_id == self.guess.guess_id)
        ).execute()

    def update_player_total_points(self):
        # Update player's total score
        Player.update(
            {
                "total_points": math.floor(
                    self.guess.player.total_points + self.difference_score
                )
            }
        ).where(Player.player_id == self.guess.player.player_id).execute()

    def get_difference(self, guess=None):
        """Difference calculation, includes "loop over" effect"""
        if not guess:
            guess = self.guess.guess

        difference = abs(guess - self.pitch_value)

        if difference > 500:
            return 1000 - difference

        self.difference = difference

        self.update_difference_value()
        return self.difference

    def get_difference_score(self):
        """
        Calculate points for the player based on how close
        they are (within range of 0-500) to the pitch_value
        """

        if self.difference == 0:
            self.difference_score = 15
        elif self.difference > 0 and self.difference < 21:
            self.difference_score = 8
        elif self.difference > 20 and self.difference < 51:
            self.difference_score = 5
        elif self.difference > 50 and self.difference < 101:
            self.difference_score = 3
        elif self.difference > 100 and self.difference < 151:
            self.difference_score = 2
        elif self.difference > 150 and self.difference < 201:
            self.difference_score = 1
        elif self.difference > 200 and self.difference < 495:
        self.difference_score = 0
        else:
            self.difference_score = -5

        self.update_player_total_points()
        return self.difference_score

    def get_winner_loser(self):
        # Determine which guesses are closest and furthest from the pitch_value
        guess_values = [record.guess for record in self.get_guesses()]
        # Closest to the pitch_value
        winner = min(guess_values, key=lambda guess: self.get_difference(guess))
        # Furthest from the pitch_value
        loser = max(guess_values, key=lambda guess: self.get_difference(guess))

        return winner, loser

    def process_guesses(self):
        """
        Iterates through the guesses for this game, and appends to the message string
        the results of how well that player performed this round.

        Uses the pitch_value to determine the difference from their guess to the correct score
        """
        winner, loser = self.get_winner_loser()

        for guess in self.get_guesses():
            self.guess = guess

            difference = self.get_difference()
            difference_score = self.get_difference_score()

            self.message += f"{guess.player.player_name} | {guess.guess} | {difference} | {difference_score} | {guess.player.total_points}\n"

            if guess.guess == winner:
                closest_player_id = guess.player.player_id

            if guess.guess == loser:
                furthest_player_id = guess.player.player_id

        return self.message, closest_player_id, furthest_player_id

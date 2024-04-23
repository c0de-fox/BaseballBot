#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=unnecessary-lambda,line-too-long,missing-module-docstring

import math

from database.models import (
    GuessModel as Guess,
    PlayerModel as Player,
)


class ProcessGuess:
    """
    A helper class for the GameManager that handles the
    logic for all of the players at the end of a game
    """

    def __init__(self, game, pitch_value, message):
        self.game_manager = game
        self.message = message
        self.pitch_value = pitch_value

        self.difference = 0
        self.difference_score = 0
        self.guesses = [Guess]
        self.guess = Guess

    def get_guesses(self):
        """
        Get all guesses for this game as a list of combo Guess + Player models,
        excluding invalid results, from lowest to highest value
        http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#joins-and-subqueries
        """
        self.guesses = (
            Guess.select(
                Guess.guess,
                Player.player_id,
                Player.player_name,
                Player.total_points,
                Guess.difference
            )
            .join(Player)
            .where(
                (Guess.game == self.game_manager.game.game_id)
                & (Guess.guess > 0)
                & (Guess.player.player_id == Player.player_id)
            )
            .order_by(Guess.difference)
        )
        return self.guesses

    def update_difference_value(self):
        """Store the difference between the player's guessed value and the pitch_value"""
        Guess.update({"difference": self.difference}).where(
            (Guess.game == self.game_manager.game.game_id)
            & (Guess.player == self.guess.player.player_id)
            & (Guess.guess_id == self.guess.guess_id)
        ).execute()

    def update_player_total_points(self):
        """Update player's total score with how many points they won this round"""
        Player.update(
            {
                "total_points": math.floor(
                    self.guess.player.total_points + self.difference_score
                )
            }
        ).where(Player.player_id == self.guess.player.player_id).execute()

    def get_difference(self, guess=None):
        """Difference calculation, includes "loop over" effect"""
        self.game_manager.logger.debug("get_difference")

        self.game_manager.logger.debug(guess if guess else "")

        if not guess:
            guess = self.guess.guess

            self.game_manager.logger.debug(f"guess: {guess}")

        difference = abs(guess - self.pitch_value)

        self.game_manager.logger.debug(f"Difference:{difference}")

        if difference > 500:
            difference = 1000 - difference

            self.game_manager.logger.debug("Diff loop over 500")
            self.game_manager.logger.debug(f"{difference}")

        self.difference = difference
        return self.difference

    def get_difference_score(self):
        """
        Calculate points for the player based on how close
        they are (within range of 0-500) to the pitch_value
        """

        self.game_manager.logger.debug("> get_difference_score")
        self.game_manager.logger.debug(self.difference)

        if self.difference == 0:
            self.difference_score = 15
            self.game_manager.logger.debug("0 Diff")
        elif self.difference > 0 and self.difference < 21:
            self.difference_score = 8
            self.game_manager.logger.debug("0 to 20 diff")
        elif self.difference > 20 and self.difference < 51:
            self.difference_score = 5
            self.game_manager.logger.debug("21 to 50 Diff")
        elif self.difference > 50 and self.difference < 101:
            self.difference_score = 3
            self.game_manager.logger.debug("51 to 100 Diff")
        elif self.difference > 100 and self.difference < 151:
            self.difference_score = 2
            self.game_manager.logger.debug("101 to 150 Diff")
        elif self.difference > 150 and self.difference < 201:
            self.difference_score = 1
            self.game_manager.logger.debug("151 to 200 Diff")
        elif self.difference > 200 and self.difference < 495:
            self.difference_score = 0
            self.game_manager.logger.debug("Diff too big")
        else:
            self.difference_score = -5
            self.game_manager.logger.debug("Big succ")

        return self.difference_score

    def get_winner_loser(self):
        """Determine which guesses are closest and furthest from the pitch_value"""

        self.game_manager.logger.debug("> get_winner_loser")

        guess_values = [record.guess for record in self.get_guesses()]
        self.game_manager.logger.debug(", ".join([str(guess) for guess in guess_values]))

        # Closest to the pitch_value
        winner = min(guess_values, key=lambda guess: self.get_difference(guess))
        self.game_manager.logger.debug(f"winner: {winner}")

        # Furthest from the pitch_value
        loser = max(guess_values, key=lambda guess: self.get_difference(guess))
        self.game_manager.logger.debug(f"loser: {loser}")

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

            self.game_manager.logger.debug(f"Current guess: {guess}")


            difference = self.get_difference()
            difference_score = self.get_difference_score()
            self.update_difference_value()
            self.update_player_total_points()

            self.message += f"{guess.player.player_name} | {guess.guess} | {difference} | {difference_score} | {(guess.player.total_points + difference_score)}\n"

            self.game_manager.logger.debug(f"new total: {(guess.player.total_points + difference_score)}")

            if guess.guess == winner:
                closest_player_id = guess.player.player_id

            if guess.guess == loser:
                furthest_player_id = guess.player.player_id

        self.game_manager.logger.debug(self.message)
        return self.message, closest_player_id, furthest_player_id

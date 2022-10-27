#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=no-member

"""
    A Context Manager / State Machine that keeps track of
    a single game instance (there should only be one) in a
    Discord channel
"""

import pdb
import uuid
import datetime

# import dateparser

from database.models import (
    database,
    GameModel as Game,
    GuessModel as Guess,
    PlayerModel as Player,
)


def check_is_running(method):
    """
    Decorator that determines if the game is running or not
    """

    async def wrapper(self):

        if self.is_running and self.new_game:
            return await self.message.channel.send("A game is already running")

        if not self.is_running and not self.new_game:
            return await self.message.channel.send("There is no game running")

        await method(self)

    return wrapper


class GameManager:
    """
    The game state class

    This represents a game that exists in a channel
    """

    def __init__(self):
        # Only one game should run at at time
        self.is_running = False

        self.new_game = True

        self.commands = [
            ("braveball", self.start),
            ("resolve", self.stop),
            ("guess", self.guess),
            ("points", self.points),
            ("help", self.help),
        ]

        self.game = Game

        # Discord message
        self.message = None

        # Discord client instance
        self.discord = None

    def __enter__(self):
        """
        Allows use of `with Game() as game` for try/except statements
        (https://peps.python.org/pep-0343/)
        """

        database.connect()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Automagically close the database
        when this class has ended execution
        """
        database.close()

    # @check_is_running
    async def start(self):
        """
        Start command - Starts a new game if there isn't already one running
        """
        # print(dir(self.message))

        self.is_running = True
        self.new_game = False

        # game.pitch_value is unknown at the start of the game
        self.game = Game.create(game_id=uuid.uuid4(), server_id=self.message.channel.id)

        await self.message.channel.send("Send me your guesses with !guess <number>")

    def __stop_args__(self):
        pieces = self.message.content.split()

        if len(pieces) == 2:
            return pieces[1], False, None, None

        if len(pieces) == 4:
            return pieces[1], True, pieces[2], pieces[3]

        return None, False, None, None

    async def close_game(self):
        """Update game state database for closing arguments"""
        # Determine arguments
        pitch_value, has_batter, batter_id, batter_guess = self.__stop_args__()
        if not pitch_value:
            return await self.message.channel.send(
                f"Invalid command <@{ str(self.message.author.id) }>!"
            )

        if has_batter:
            player_id = batter_id[3:]
            Guess.create(
                game_id=self.game.game_id,
                player_id=player_id,
                player_name=self.discord.get_user(int(player_id).name),
                guess=int(batter_guess),
            ).save()

        # Save the pitch value
        self.game.update(
            {
                Game.pitch_value: pitch_value,
                Game.date_ended: datetime.datetime.now(),
            }
        )

        return int(pitch_value)

    # @check_is_running
    async def stop(self):
        """
        Stop command - Stops the game if it is currently running,
        saves the pitch value, and displays differences
        """

        pitch_value = await self.close_game()

        # Start calculating difference

        # Get all guesses for this game as a list of combo Guess + Player models,
        # excluding invalid results, from lowest to highest
        # http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#joins-and-subqueries
        records = (
            Guess.select(
                Guess.guess, Player.player_id, Player.player_name, Player.total_points
            )
            .join(Player)
            .where(
                (Guess.game_id == self.game.game_id)
                & (Guess.guess > 0)
                & (Guess.player_id == Player.player_id)
            )
            .order_by(Guess.guess)
        )

        # Minimum of 3 players
        if len(records) < 1:
            self.game = None
            self.is_running = False
            await self.message.channel.send(
                ("Play closed!\n" + "However, there were not enough participants.")
            )

        message = (
            "Closed this play! Here are the results\n"
            + "PLAYER | GUESS | DIFFERENCE | POINTS GAINED | TOTAL POINTS\n"
        )

        def get_difference(guess):
            difference = abs(guess - pitch_value)

            if difference > 500:
                return 1000 - difference

            return difference

        # Determine which guesses are closest and furthest from the pitch_value
        guess_values = [record.guess for record in records]
        closest_guess_value = min(
            guess_values, key=lambda guess: get_difference(guess)
        )
        furthest_guess_value = max(
            guess_values, key=lambda guess: get_difference(guess)
        )

        def get_difference_score():
            # TODO: Calculate score based on scoring table
            return 0

        for record in records:
            difference = abs(record.guess - pitch_value)
            difference_score = get_difference_score()

            # TODO: Update Guess.difference
            # TODO: Update Player.total_points

            if record.guess == closest_guess_value:
                closest_player_id = record.player.player_id

            if record.guess == furthest_guess_value:
                furthest_player_id = record.player.player_id

            message += f"{record.player.player_name} | {record.guess} | {difference} | {difference_score} | {record.player.total_points}\n"

        message += (
            f"\nCongrats <@{closest_player_id}>! You were the closest!\n"
            + f"Sorry <@{furthest_player_id}>, you were way off"
        )

        await self.message.channel.send(message)

        # stop and discard game
        self.is_running = False
        self.game = None

    # @check_is_running
    async def guess(self):
        """
        Guess command - Allows the player to add a guess to the current
        running game
        """

        value = int(self.message.content.split()[1])
        if value < 1 or value > 1000:
            return await self.message.channel.send(
                "Invalid value. It must be between 1 and 1000 inclusive"
            )

        player_id, created = Player.get_or_create(
            player_id=self.message.author.id, player_name="c0de"
        )

        player_guess, created = Guess.get_or_create(
            guess_id=uuid.uuid4(), game_id=self.game.game_id, player_id=player_id
        )

        Guess.update({"guess": value}).where((Guess.game_id==self.game.game_id) & (Guess.player_id==player_id)).execute()
        if created:
            return await self.message.add_reaction("\N{THUMBS UP SIGN}")

        return await self.message.channel.send(
            f"<@{ str(self.message.author.id) }> your guess has been updated"
        )

    async def points(self):
        """
        Points command - returns a table ordered from highest to lowest
        of the players and their points
        """
        # TODO
        # value = self.message.content.split()
        # try:
        #     if len(value) > 1:
        #         timestamp = dateparser.parse(value[1])
        # except:
        #     return await self.message.channel.send("Invalid timestamp. Try again")

        return await self.message.channel.send("Sorry, not implemented yet")

    async def help(self):
        """help command"""
        # TODO: Add help message
        help_message = "help"

        recipient = await self.discord.fetch_user(self.message.author.id)
        await recipient.send(help_message)

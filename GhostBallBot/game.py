#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=no-member

"""
    A Context Manager / State Machine that keeps track of
    a single game instance (there should only be one) in a
    Discord channel
"""

import uuid

# import dateparser

from database.models import database, GameModel, GuessModel


async def check_is_running(method, start_new_game=True):
    """
    Decorator that determines if the game is running or not
    """

    async def wrapper(self):

        if self.is_running and start_new_game:
            return await self.message.channel.send("A game is already running")

        if not self.is_running and not start_new_game:
            return await self.message.channel.send("There is no game running")

        await method(self)

    return await wrapper


class Game:
    """
    The game state class

    This represents a game that exists in a channel
    """

    def __init__(self):
        # Only one game should run at at time
        self.is_running = False

        self.commands = {
            "ghostball": self.start,
            "resolve": self.stop,
            "guess": self.guess,
            "points": self.points,
            "help": self.help,
        }

        self.game = GameModel

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

    @check_is_running
    async def start(self):
        """
        Start command - Starts a new game if there isn't already one running
        """
        self.is_running = True

        # game.pitch_value is unknown at the start of the game
        self.game = GameModel.create(
            game_id=uuid.uuid4(), server_id=self.message.guild.id
        )

        await self.message.send("Send me your guesses with !guess <number>")

    def __stop_args__(self):
        pieces = self.message.content.split()

        if len(pieces) == 2:
            return pieces[1], False, None, None

        if len(pieces) == 4:
            return pieces[1], True, pieces[2], pieces[3]

        return None, False, None, None

    @check_is_running(stop, start_new_game=False)
    async def stop(self):
        """
        Stop command - Stops the game if it is currently running,
        saves the pitch value, and displays differences
        """

        # Determine arguments
        pitch_value, has_batter, batter_id, batter_guess = self.__stop_args__()
        if not pitch_value:
            return await self.message.channel.send(
                f"Invalid command <@{ str(self.message.author.id) }>!"
            )

        if has_batter:
            player_id = batter_id[3:]
            GuessModel.create(
                game_id=self.game.game_id,
                player_id=player_id,
                player_name=self.discord.get_user(int(player_id).name),
                guess=int(batter_guess),
            )

        # Save the pitch value
        self.game.update({"pitch_value": pitch_value})

        # TODO: Determine differences

        await self.message.channel.send(
            "Difference calculation is not currently available"
        )

        # stop and discard game
        self.is_running = False
        self.game = None

    @check_is_running(guess, start_new_game=False)
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

        # TODO: Check if the user tried to vote before, update their vote if so

        player_guess, created = GuessModel.get_or_create(
            game_id=self.game.game_id,
            player_id=self.message.author.id,
            player_name=self.message.author.name,
        )

        player_guess.update(guess=value)
        if not created:  # They updated their guess
            await self.message.channel.send(
                f"<@{ str(self.message.author.id) }> your guess has been updated"
            )

        return await self.message.add_reaction(emoji="\N{THUMBS UP SIGN}")

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

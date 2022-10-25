#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

import uuid

import dateparser

from database.models import database, GameModel, GuessModel


async def check_is_running(method, start_new_game=True):
    """
    Decorator that determines if the game is running or not
    """

    async def wrapper(self):

        if self.is_running and start_new_game:
            return await self.message.channel.send("A game is already running")
        elif not self.is_running and not start_new_game:
            return await self.message.channel.send(
                "There is no game running to add guesses to"
            )

        await method(self)

    return await wrapper


class Game:
    """
    The game state class

    This represents a game that exists in a channel
    """

    def __enter__(self):
        """
        Allows use of `with Game as game` for try/except statements

        We are using this instead of __init__, they work very similar
        to each other (https://peps.python.org/pep-0343/)
        """
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
        self.is_running = True

        # game.pitch_value is unknown at the start of the game
        self.game = GameModel.create(
            game_id=uuid.uuid4(), server_id=self.message.guild.id
        )

        await self.message.send(
            "@flappy ball, pitch is in! Send me your guesses with !guess <number>"
        )

    def __stopArgs__(self):
        pieces = self.message.content.split()

        if len(pieces) == 2:
            return pieces[1], False, None, None
        elif len(pieces) == 4:
            return pieces[1], True, pieces[2], pieces[3]

        return None, False, None, None

    @check_is_running(start_new_game=False)
    async def stop(self):
        # Determine arguments
        pitch_value, has_batter, batter_id, batter_guess = self.__stopArgs__()
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

    @check_is_running(start_new_game=False)
    async def guess(self):
        value = int(self.message.content.split()[1])
        if value < 1 or value > 1000:
            return await self.message.channel.send(
                f"Invalid value. It must be between 1 and 1000 inclusive"
            )

        GuessModel.create(
            game_id=self.game.game_id,
            player_id=self.message.author.id,
            player_name=self.message.author.name,
            guess=value,
        )

        return await self.message.add_reaction(emoji="\N{THUMBS UP SIGN}")

    async def points(self):
        # TODO
        value = self.message.content.split()
        try:
            if len(value) > 1:
                timestamp = dateparser.parse(value[1])
        except:
            return await self.message.channel.send("Invalid timestamp. Try again")

        return await self.message.channel.send("Sorry, not implemented yet")

    async def help(self):
        # TODO: Add help message
        help_message = "help"

        recipient = await self.discord.fetch_user(self.message.author.id)
        await recipient.send(help_message)

#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=no-member,not-an-iterable

"""
    A Context Manager / State Machine that keeps track of
    a single game instance (there should only be one) in a
    Discord channel
"""

import uuid
import datetime

# import dateparser

from database.models import (
    database,
    GameModel as Game,
    GuessModel as Guess,
    PlayerModel as Player,
)
from game.guess import ProcessGuess


class GameManager:
    """
    The game state class

    This represents a game that exists in a channel
    """

    def __init__(self):
        # Only one game should run at at time
        self.is_running = False

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

    async def start(self):
        """
        Start command - Starts a new game if there isn't already one running
        """

        if self.is_running:
            return await self.message.channel.send("A game is already running")

        self.is_running = True

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

    async def update_pitch_value(self):
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
        Game.update(
            {
                Game.pitch_value: pitch_value,
                Game.date_ended: datetime.datetime.now(),
            }
        ).where(Game.game_id == self.game.game_id).execute()

        return int(pitch_value)

    async def stop(self):
        """
        Stop command - Stops the game if it is currently running,
        saves the pitch value, and displays differences
        """

        if not self.is_running:
            return await self.message.channel.send("There is no game running")

        # How many valid guesses got placed?
        guess_count = (
            Guess.select()
            .join(Game)
            .where((Guess.game.game_id == self.game.game_id) & (Guess.guess > 0))
            .count()
        )

        # Discard the game if there weren't enough players
        if guess_count < 3:
            self.game = None
            self.is_running = False
            return await self.message.channel.send(
                ("Play closed!\n" + "However, there were not enough participants.")
            )

        message = (
            "Closed this play! Here are the results\n"
            + "PLAYER | GUESS | DIFFERENCE | POINTS GAINED | TOTAL POINTS\n"
        )

        pitch_value = await self.update_pitch_value()
        guess_processor = ProcessGuess(
            game=self, pitch_value=pitch_value, message=message
        )

        (
            message,
            closest_player_id,
            furthest_player_id,
        ) = guess_processor.process_guesses()

        message += (
            f"\nCongrats <@{closest_player_id}>! You were the closest!\n"
            + f"Sorry <@{furthest_player_id}>, you were way off"
        )

        await self.message.channel.send(message)

        # stop and discard game
        self.is_running = False
        self.game = None

    async def guess(self):
        """
        Guess command - Allows the player to add a guess to the current
        running game
        """

        if not self.is_running:
            return await self.message.channel.send("There is no game running")

        value = int(self.message.content.split()[1])
        if value < 1 or value > 1000:
            return await self.message.channel.send(
                "Invalid value. It must be between 1 and 1000 inclusive"
            )

        # Create player if they don't exist
        player, _ = Player.get_or_create(
            player_id=self.message.author.id, player_name=self.message.author.name
        )

        # Create the guess (or allow us to say update successful)
        _, created = Guess.get_or_create(
            guess_id=uuid.uuid4(), game_id=self.game.game_id, player_id=player.player_id
        )

        Guess.update({"guess": value}).where(
            (Guess.game == self.game.game_id)
            & (Guess.player_id == self.message.author.id)
        ).execute()

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
        message = (
            "\nPlayers, who played recently, with their points highest to lowest\n\n"
        )
        message += "Player | Total Points | Last Played\n"

        players = Player.select(
            Player.player_name, Player.total_points, Player.last_update
        ).order_by(Player.last_update.desc(), Player.total_points.desc())

        for player in players:
            message += (
                " | ".join(
                    [
                        player.player_name,
                        str(player.total_points),
                        str(player.last_update)[:-10],
                    ]
                )
                + "\n"
            )

        return await self.message.channel.send(message)

    async def help(self):
        """help command - Sends a DM to the requesting user with available commands"""

        help_message = (
            "Braveball commands\n"
            + "!braveball - Start new game\n"
            + "!guess - While a game is running, add a guess"
            + " (or update an existing one) from 1-1000\n"
            + "!resolve <value> - 1-1000 to resolve the game\n"
            + " You can also add a batter's guess with: "
            + "!resolve <value> <discord id #> <guess>\n"
            + "!points - Shows a table of the most recent players, and their scores\n"
            + "!help - Shows this message"
        )

        recipient = await self.discord.fetch_user(self.message.author.id)
        await recipient.send(help_message)

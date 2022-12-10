#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring

import datetime

from database.models import GameModel as Game, GuessModel as Guess
from game.base import BaseGameManager
from game.process_guess import ProcessGuess


class EndGameManager(BaseGameManager):
    """Commands that run at the end of a game"""

    def __init__(self):
        super().__init__()
        self.commands.append(("resolve", self.stop))

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
            player_name = await self.discord.get_user(int(player_id).name)
            Guess.create(
                game_id=self.game.game_id,
                player_id=player_id,
                player_name=player_name,
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

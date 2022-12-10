#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring

from database.models import GameModel as Game
from game.base import BaseGameManager


class NewGameManager(BaseGameManager):
    """Commands that run at the start of a new game"""

    def __init__(self):
        super().__init__()
        self.commands.append(("braveball", self.start))

    async def start(self):
        """
        Start command - Starts a new game if there isn't already one running
        """

        if self.is_running:
            return await self.message.channel.send("A game is already running")

        self.is_running = True

        # game.pitch_value is unknown at the start of the game
        self.game = Game.create(server_id=self.message.channel.id)

        await self.message.channel.send("Send me your guesses with !guess <number>")

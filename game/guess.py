#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring,too-few-public-methods

from database.models import PlayerModel as Player, GuessModel as Guess
from game.base import BaseGameManager


class GuessManager(BaseGameManager):
    """Commands that run when a player makes a guess"""

    def __init__(self):
        super().__init__()
        self.commands.append(("guess", self.guess))

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
            game_id=self.game.game_id, player_id=player.player_id
        )

        Guess.update({"guess": value}).where(
            (Guess.game == self.game.game_id) & (Guess.player == self.message.author.id)
        ).execute()

        if created:
            return await self.message.add_reaction("\N{THUMBS UP SIGN}")

        return await self.message.channel.send(
            f"<@{ str(self.message.author.id) }> your guess has been updated"
        )

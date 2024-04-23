#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring,too-few-public-methods

from database.models import PlayerModel as Player
from game.base import BaseGameManager


class ClearManager(BaseGameManager):
    """Commands that run when a player clears the session leaderboard"""

    def __init__(self):
        super().__init__()
        self.commands.append(("clear", self.clear))

    async def clear(self):
        """Clear command - Clears the session scoreboard"""

        players = Player.select(Player.player_id, Player.total_points)

        for player in players:
            player.total_points = 0

        Player.bulk_update(players, fields=[Player.total_points])

        clear_message = "The score has been cleared!"

        await self.message.channel.send(clear_message)

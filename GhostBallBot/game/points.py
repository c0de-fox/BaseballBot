#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=not-an-iterable,missing-module-docstring

from database.models import PlayerModel as Player
from game.manager import BaseGameManager


class PointsManager(BaseGameManager):
    """Commands that run when a player makes a guess"""

    def __init__(self):
        self.commands.append(("points", self.points))
        super().__init__()

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

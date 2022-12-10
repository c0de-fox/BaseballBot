#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=not-an-iterable,missing-module-docstring,too-few-public-methods

from beautifultable import BeautifulTable

from database.models import PlayerModel as Player
from game.base import BaseGameManager


class PointsManager(BaseGameManager):
    """Commands that run when a player makes a guess"""

    def __init__(self):
        super().__init__()
        self.commands.append(("points", self.points))

    async def points(self):
        """
        Points command - returns a table ordered from highest to lowest
        of the players and their points
        """
        message = (
            "\nPlayers, who played recently, with their points highest to lowest\n\n"
        )

        message += "```\n"
        table = BeautifulTable()
        table.column_headers = ["Player", "Total Points", "Last Played"]

        players = Player.select(
            Player.player_name, Player.total_points, Player.last_update
        ).order_by(Player.last_update.desc(), Player.total_points.desc())

        for player in players:
            table.rows.append([
                player.player_name,
                str(player.total_points),
                str(player.last_update)[:-10],
            ])

        message += str(table)
        message += "\n```\n"

        return await self.message.channel.send(message)

#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring,too-few-public-methods

from database.models import PlayerModel as Player
from game.base import BaseGameManager


class ResetManager(BaseGameManager):
    """Commands that run when a player asks for help"""

    def __init__(self):
        super().__init__()
        self.commands.append(("reset", self.reset))

    async def reset(self):
        """Reset command purges all players (removes total points)"""
        Player.delete().where(True).execute()

        return await self.message.channel.send("ok")

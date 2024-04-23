#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring,too-few-public-methods

from game.base import BaseGameManager


class HelpManager(BaseGameManager):
    """Commands that run when a player asks for help"""

    def __init__(self):
        super().__init__()
        self.commands.append(("help", self.help))

    async def help(self):
        """help command - Sends a DM to the requesting user with available commands"""

        help_message = (
            "Braveball commands\n"
            + "ping - Will respond 'pong' if the bot is alive\n"
            + "!braveball - Start new game\n"
            + "!guess - While a game is running, add a guess"
            + " (or update an existing one) from 1-1000\n"
            + "!resolve <value> - 1-1000 to resolve the game\n"
            + "!clear - Clear the session scoreboard\n"
            + "!points - Shows a table of the most recent players, and their scores\n"
            + "!reset - Removes all players and total points\n"
            + "!help - Shows this message"
        )

        recipient = await self.discord.fetch_user(self.message.author.id)
        await recipient.send(help_message)

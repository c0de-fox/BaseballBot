#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring

from game.manager import BaseGameManager


class HelpManager(BaseGameManager):
    """Commands that run when a player asks for help"""

    def __init__(self):
        self.commands.append(("help", self.help))
        super().__init__()

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

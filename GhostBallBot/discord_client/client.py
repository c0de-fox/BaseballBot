#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=wrong-import-position

"""
    A discord bot that hosts Ghostball/Braveball.

    A discord game where players guess the pitch speed
    from a fantasy baseball pitcher, and whoever is
    closer gets more points
"""

import sys

import discord

# Import game functions
sys.path.append("..")
import game


class GhostBallClient(discord.Client):
    """
    Implementation of a Discord client that will monitor
    a channel for messages, and if it recieves a message
    defined in the Game object, and pass it along
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with game.GameManager() as self.game:
            self.game.discord = self

    async def on_ready(self):
        """Method called when connected to Discord"""
        print("Logged on as", self.user)

    async def on_message(self, message):
        """Method called when a message is recieved"""
        # Don't respond to ourself
        if message.author == self.user:
            return

        # Bot health check
        if message.content == "ping":
            await message.channel.send("pong")

        # Game commands
        if message.content.startswith("!"):
            firstword = message.content[1:].split()[0]

            # Determine if the first word is a command, and run it
            for command, function in self.game.commands:
                if firstword == command:
                    self.game.message = message
                    await function(self.game)

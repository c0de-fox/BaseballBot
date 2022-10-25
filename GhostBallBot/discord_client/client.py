#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

import sys

import discord

# Import game functions
sys.path.append('..')
import game

class GhostBallClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super(GhostBallClient, self).__init__(*args, **kwargs)

        with game.Game() as self.game:
            self.game.discord = self

    async def on_ready(self):
        print("Logged on as", self.user)

    async def on_message(self, message):
        # Don't respond to ourself
        if message.author == self.user:
            return

        # Bot health check
        if message.content == "ping":
            await message.channel.send("pong")

        # Game commands
        if message.content.startswith('!'):
            firstword = message.content[1:].split()[0]

            # Determine if the first word is a command, and run it
            for command, function in self.game.commands:
                if firstword == command:
                    self.game.message = message
                    await function(self.game)

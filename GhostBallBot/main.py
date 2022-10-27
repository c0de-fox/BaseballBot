#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=missing-module-docstring

import os

from discord import Intents
from discord_client.client import GhostBallClient
from database.models import DATABASE, database, create_models

if __name__ == "__main__":
    # Set up the database if we haven't already
    if not os.path.exists(DATABASE):
        database.connect()
        create_models()
        database.close()

    client = GhostBallClient(intents=Intents.all())
    client.run(os.environ.get("discord_token"))

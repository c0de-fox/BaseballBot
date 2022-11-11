#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=no-member

"""
    A Context Manager / State Machine that keeps track of
    a single game instance (there should only be one) in a
    Discord channel
"""

from database.models import database, GameModel as Game

class BaseGameManager:
    """Base Game Manager for each Game Manager class to inherit"""

    def __init__(self):
        # Only one game should run at at time
        self.is_running = False

        self.commands = []

        self.game = Game

        # Discord message
        self.message = None

        # Discord client instance
        self.discord = None

    def __enter__(self):
        """
        Allows use of `with Game() as game` for try/except statements
        (https://peps.python.org/pep-0343/)
        """

        database.connect()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Automagically close the database
        when this class has ended execution
        """
        database.close()


#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=no-member

"""
    A Context Manager / State Machine that keeps track of
    a single game instance (there should only be one) in a
    Discord channel
"""

from game.new_game import NewGameManager
from game.end_game import EndGameManager
from game.guess import GuessManager
from game.points import PointsManager
from game.reset import ResetManager
from game.help import HelpManager


class GameManager(
    NewGameManager, EndGameManager, GuessManager, PointsManager, ResetManager, HelpManager
):
    """
    Represents what this bot is able to do on a channel (or DMs)
    """

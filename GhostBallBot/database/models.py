#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# pylint: disable=too-few-public-methods

"""
    An implementation of a SQLite database
"""

import os
import datetime

from peewee import (
    SqliteDatabase,
    Model,
    UUIDField,
    IntegerField,
    CharField,
    DateTimeField,
    ForeignKeyField,
)

# User can provide path to database, or it will be put next to main.py
DATABASE = os.environ.get("database_path", os.getcwd() + "/ghostball.db")
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    """All of our models will inherit this class
    and use the same database connection"""

    class Meta:
        """meta"""

        database = database


class GameModel(BaseModel):
    """Games that are ran"""

    game_id = UUIDField(primary_key=True)
    server_id = IntegerField()

    pitch_value = IntegerField(null=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    date_ended = DateTimeField(null=True)


class GuessModel(BaseModel):
    """Guesses for a particular game"""

    player_id = IntegerField(primary_key=True)
    game_id = ForeignKeyField(GameModel, backref="guesses")

    player_name = CharField()
    guess = IntegerField()
    difference = IntegerField(null=True)
    date_guessed = DateTimeField(null=True)

    # TODO: Add unique constraint for player_id and game_id
    # ie: one guess per player allowed per game


def create_models():
    """Create database tables"""

    with database:
        database.create_tables([GameModel, GuessModel])

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
database = SqliteDatabase(DATABASE, pragmas={"foreign_keys": 1})


class BaseModel(Model):
    """All of our models will inherit this class
    and use the same database connection"""

    class Meta:
        """meta"""

        database = database


class PlayerModel(BaseModel):
    """Need to keep track of total player score"""

    player_id = IntegerField(primary_key=True)
    player_name = CharField()

    total_points = IntegerField(default=0)
    date_joined = DateTimeField(default=datetime.datetime.now)
    last_update = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        """Should set the last update everytime the record is saved"""
        self.last_update = datetime.datetime.now()
        super().save(*args, **kwargs)


class GameModel(BaseModel):
    """Games that are ran"""

    game_id = UUIDField(primary_key=True)
    server_id = IntegerField()

    pitch_value = IntegerField(null=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    date_ended = DateTimeField(null=True)


class GuessModel(BaseModel):
    """Guesses for a particular game"""

    guess_id = UUIDField(primary_key=True)

    player = ForeignKeyField(PlayerModel, backref="guesses")
    game_id = ForeignKeyField(GameModel, backref="guesses")

    guess = IntegerField(default=0)
    difference = IntegerField(null=True)
    date_guessed = DateTimeField(null=True)

def create_models():
    """Create database tables"""

    with database:
        database.create_tables([GameModel, GuessModel])

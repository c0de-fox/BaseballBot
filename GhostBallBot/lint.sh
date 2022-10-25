#!/bin/bash

pylint main.py game.py discord_client database > lint.log
black main.py game.py discord_client database

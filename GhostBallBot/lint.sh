#!/bin/bash

pylint main.py game.py discord_client database
black main.py game.py discord_client database

#!/bin/bash

pylint main.py game discord_client database > lint.log
black main.py game discord_client database

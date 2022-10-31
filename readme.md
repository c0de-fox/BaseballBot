# Discord Ghost Ball Bot

A bot that will listen on a discord channel, accpeting commands.  
The main commands are `!start`, `!guess [int]` and `!resolve [int]`.

The integer will be between 1 and 1000, and the person with the closest guess will win points.

The point scale is:

* 0-25 - 100 pts
* 26-50 - 75 pts
* 51-75 - 50 pts
* 76-100 - 25 pts

There should also be a running total for each player that can be checked with a command.

## Requirements

You will need a discord bot already set up and supply an auth token.

Python requirements can be installed with `pipenv install` (install pipenv with `pip3 install pipenv`)

## Usage

All of the new bot code is in the [GhostBallBot](./GhostBallBot/) folder. This documentation is for the new code.

The original code is in [src](./src/). Feel free to try to get this working.

1. Install the python requirements
1. Add discord token to run.sh
1. Execute run.sh
1. Bot should then connect to discord and start responding to commands defined in game.py


## Roadmap

Things that would be nice to add:

* (yaml) Config file for tweaking various internals
* Admin commands: table clear, record deletion, record update
* Audit log of admin commands, and previous values for anything changed

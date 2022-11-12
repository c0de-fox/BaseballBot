# Discord Baseball Bot

A bot that will listen on a discord channel, accpeting commands.

The main commands are `!braveball`, `!guess [int]` and `!resolve [int]`  
Use the `!help` command for more information

## Requirements

1. You will need a discord bot and an auth token
1. You will need access to a server that runs Docker
    * For development, docker is optional. See Development section of Usage below

## Points

Points are determined by the difference, which comes from this formula:

```python
difference = abs(guess - pitch_value)

if difference > 500:
    difference = 1000 - difference
```

The point scale is a range based on the difference

| minimum         | maximum         | points |
|-----------------|-----------------|--------|
| (no difference) | (no difference) | 15     |
| 1               | 20              | 8      |
| 21              | 50              | 5      |
| 51              | 100             | 3      |
| 101             | 150             | 2      |
| 151             | 200             | 1      |
| 200             | 494             | 0      |
| 495             | 500             | -5     |

Points are added to a running total for each player at the end of each round.

## Usage

If you are using docker:

1. You need to determine which version of the bot to use
    * If you are using a raspberry pi, you want `archarm64`
    * Otherwise, you most likely want `archx64`

### Production with docker

This docker command is the minimum required to run the bot:

`docker run -d -e discord_token="<discord token> c0defox/baseballbot:<version>"`

_Note: The above will not persist the database through restarts_

If you want to keep the database, use the following command:

`docker run -d -v database:/database -e database_path="/database/baseball.db" -e discord_token="<discord token>" c0defox/baseballbot:<version>`

### Development with docker

1. Modify the source code
1. Run `docker build -t baseballbot:<tag> .`
1. Run the same docker commands you would in production

_note: You will probably want to purge your builds after a while, as they will eventually take up space_

### Development without docker

Python requirements can be installed with `pipenv install` (install pipenv with `pip3 install pipenv`)

1. Install the python requirements
1. Add discord token to run.sh
1. Modify the source code
1. Start run.sh in the terminal (restart as you make code changes)

If you modify the source code, you should also run `lint.sh`. This will warn you of linting problems that you can choose to fix, as well as format all of the code to the same standard automatically (usually this will resolve linting warnings)

## Roadmap

Things that would be nice to add:

* (yaml) Config file for tweaking various internals
* Admin commands: table clear, record deletion, record update
* Audit log of admin commands, and previous values for anything changed

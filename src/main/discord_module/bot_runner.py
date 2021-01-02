import sys

import discord
from discord.utils import get

import uuid
import datetime
import dateparser

from src.main.configs import Configs
from src.main.database_module.guess_dao import GuessDAO, GUESSED_NUMBER, MEMBER_ID, MEMBER_NAME, DIFFERENCE
from src.main.services.points_service import PointsService
from src.main.database_module.play_dao import PlayDAO, PLAY_ID, CREATION_DATE, SERVER_ID
from src.main.db_session import DatabaseSession
from src.main.discord_module.leaderboard_config import LeaderboardConfig

play_dao = None
guess_dao = None
points_service = PointsService()
bot = discord.Client()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content
    server_id = message.guild.id

    '''
        Sets up the next set of guesses. 
    '''
    if content.startswith('!ghostball'):
        if play_dao.is_active_play(server_id):
            await message.channel.send("There's already an active play.  Could you close that one first, please?")
        else:
            generated_play_id = uuid.uuid4()
            play_object = {PLAY_ID: generated_play_id, CREATION_DATE: datetime.datetime.now(), SERVER_ID: server_id}
            play_dao.insert(play_object)

            await message.channel.send("@flappy ball, pitch is in!  Send me your guesses with a !guess command.")

    if content.startswith("!guess"):
        guess_value = None
        try:
            guess_value = __parse_guess__(content)
        except ValueError:
            await message.channel.send("That number is not between 1 and 1000.  We're still in MLN so don't try to cheat.")
            return

        if guess_value is None:
            await message.channel.send("I don't know what you did but I'm pretty sure you're tyring to break the bot so please stop.")
            return

        if not play_dao.is_active_play(server_id):
            await message.channel.send("Hey, there's no active play!  Start one up first with !ghostball.")
        else:
            play = play_dao.get_active_play(server_id)
            guess_object = {PLAY_ID: play['play_id'],
                            MEMBER_ID: str(message.author.id),
                            GUESSED_NUMBER: guess_value,
                            MEMBER_NAME: str(message.author.name)}

            if guess_dao.insert(guess_object, allow_update=True):
                await message.add_reaction(emoji="\N{THUMBS UP SIGN}")

    # Closes off the active play to be ready for the next set
    if content.startswith('!resolve'):
        # try:
        pitch_number, batter_id, batter_guess, has_batter = __parse_resolve_play__(content)
        if args is None:
            await message.channel.send("Hey " + "<@" + str(message.author.id) + ">, I'm not sure what you meant. "
                                                                                "You need real, numeric, values for this command to work.  "
                                                                                "Use !resolve <pitch number> <optional batter> <optional swing number>"
                                                                                " and try again.")

        # Check if we have an active play
        if not play_dao.is_active_play(server_id):
            await message.channel.send("You confused me.  There's no active play so I have nothing to close!")
        else:
            if has_batter:
                referenced_member_id = batter_id[3:-1]
                play = play_dao.get_active_play(server_id)
                guess_object = {PLAY_ID: play['play_id'],
                                MEMBER_ID: str(referenced_member_id),
                                GUESSED_NUMBER: batter_guess,
                                MEMBER_NAME: bot.get_user(int(referenced_member_id)).name}

                guess_dao.insert(guess_object, True)

            play = play_dao.resolve_play(pitch_number, server_id)
            guess_dao.set_differences(pitch_number, play['play_id'])
            guesses = points_service.fetch_sorted_guesses_by_play(guess_dao, play['play_id'])

            response_message = "Closed this play! Here are the results:\n"
            response_message += "PLAYER --- DIFFERENCE --- POINTS GAINED\n"
            for guess in guesses:
                response_message += guess[1] + " --- " + str(guess[2]) + " --- " + str(guess[3]) + "\n"

            if len(guesses) < 2:
                response_message += "Not enough people participated to give best and worst awards.  Stop being lazy."

            else:
                response_message += "\nCongrats to <@" + str(guesses[0][0]) + "> for being the closest! \n"
                response_message += "And tell <@" + str(guesses[-1][0]) + "> they suck."

            await message.channel.send(response_message)

    if content.startswith("!points"):
        try:
            timestamp = __parse_points_message__(content)
        except:
            await message.channel.send("You gave me a timestamp that was so bad, the best date handling library in the"
                                       " world of software couldn't figure out what you meant.  That's...impressive.  Now"
                                       " fix your shit and try again.")
            return
        
        points_by_user = points_service.fetch_points(timestamp, server_id, play_dao, guess_dao)
        response = "Here are the top guessers by points as per your request..."
        for user in points_by_user:
            if str(user[2]) != '0':
                response += "\n" + str(user[1]) + " : " + str(user[2])

        await message.channel.send(response)

    # Refresh Postgres connection
    if content.startswith('!restart'):
        play_dao.refresh()
        guess_dao.refresh()

    if content.startswith('!help'):
        help_message = __get_help_message__()
        recipient = await bot.fetch_user(message.author.id)
        await recipient.send(help_message)


def __get_help_message__():
    # Start message with person who asked for help
    help_message = "Hey!  I can be instructed to do any number of things!  Use the following commands: \n" \
                   "!guess <NUMBER> --- This will add your guess to the currently active play.  " \
                   "I will give you a thumbs up if everything worked!\n" \
                   "!ghostball --- Starts a new play. I'll let you know if this didn't work for some reason!\n" \
                   "!help --- You just asked for this.  If you ask for it again, I'll repeat myself.\n" \
                   "!resolve <PITCH_NUMBER> <OPTIONAL --- BATTER by @-mention> <OPTIONAL - ACTUAL SWING NUMBER> --- " \
                   "Uses the pitch number and real swing number to figure out who was closest and ends the active play." \
                   "If you include the batter and their swing number, they will get credit for how well they did!\n" \
                   "!points <OPTIONAL --- TIMESTAMP> Fetches all plays since your requested time, or the beginning of the unvierse " \
                   "if none given.  Will currently always dump all players - top X coming soon...\n" \
                   "!restart --- If the bot looks broken, this will take a shot at fixing it.  It won't answer your commands " \
                   "for about 3 seconds after you do this! BE CAREFUL!  ONLY USE IN AN EMERGENCY!\n" \
                   "<PING KALI IF YOU'RE CONFUSED, ANGRY, OR WANT TO GEEK OUT ABOUT BRAVELY DEFAULT!>\n"

    return help_message


def __parse_leaderboard_message__(message_content):
    return LeaderboardConfig(message_content)


def __parse_points_message__(message_content):
    pieces = message_content.split(' ')

    if len(pieces) > 1:
        try:
            timestamp = dateparser.parse(pieces[1])
        except:
            raise RuntimeError("Unable to parse timestamp!")
    else:
        timestamp = dateparser.parse("1970-01-01")

    return timestamp


def __parse_guess__(message_content):
    pieces = message_content.split(' ')
    try:
        guess_value = pieces[1]
        guess_as_int = int(guess_value)
        if guess_as_int > 1000 or guess_as_int < 1:
            raise ValueError("Number not between 1 and 1000 inclusive")
        else:
            return guess_value
    except TypeError:
        return None


def __parse_resolve_play__(message_content):
    pieces = message_content.split()
    try:
        if len(pieces) == 2:
            return pieces[1], None, None, False
        elif len(pieces) == 4:
            return pieces[1], pieces[2], pieces[3], True
        else:
            print("Illegal resolution command")
            return None, None
    except TypeError:
        return None, None


if __name__ == '__main__':
    args = sys.argv
    token = args[1]
    file_path = args[2]

    configs = Configs(file_path)
    databaseSession = DatabaseSession()

    play_dao = PlayDAO()
    guess_dao = GuessDAO()
    bot.run(token)

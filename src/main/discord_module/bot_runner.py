import sys

import discord
import uuid
import datetime

from src.main.configs import Configs
from src.main.database_module.guess_dao import GuessDAO, GUESSED_NUMBER, MEMBER_ID, MEMBER_NAME, DIFFERENCE
from src.main.database_module.play_dao import PlayDAO, PLAY_ID, CREATION_DATE
from src.main.db_session import DatabaseSession
from src.main.discord_module.leaderboard_config import LeaderboardConfig

play_dao = None
guess_dao = None
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

    '''
        Sets up the next set of guesses. 
    '''
    if content.startswith('!ghostball'):
        if play_dao.is_active_play():
            await message.channel.send("There's already an active play.  Could you close that one first, please?")
        else:
            play_object = {PLAY_ID: uuid.uuid4(), CREATION_DATE: datetime.datetime.now()}
            play_dao.insert(play_object)

            await message.channel.send("@flappyball, pitch is in!  Send me your guesses with a !guess command.")

    if content.startswith("!guess"):
        guess_value = __parse_guess__(content)

        if not play_dao.is_active_play():
            await message.channel.send("Hey, there's no active play!  Start one up first with !ghostball.")
        else:
            play = play_dao.get_active_play()
            guess_object = {PLAY_ID: play['play_id'],
                            MEMBER_ID: str(message.author.id),
                            GUESSED_NUMBER: guess_value,
                            MEMBER_NAME: str(message.author.name)}

            if guess_dao.insert(guess_object):
                await message.add_reaction(emoji="\N{THUMBS UP SIGN}")

    # Closes off the active play to be ready for the next set
    if content.startswith('!resolve'):
        # try:
        pitch_value = __parse_resolve_play__(content)
        if pitch_value is None:
            await message.channel.send("Hey " + "<@" + str(message.author.id) + ">, I'm not sure what you meant. "
                                                                                "You need real, numeric, values for this command to work.  "
                                                                                "Use !resolve <pitch number> and try again.")

        # Check if we have an active play
        if not play_dao.is_active_play():
            await message.channel.send("You confused me.  There's no active play so I have nothing to close!")
        else:
            play = play_dao.resolve_play(pitch_value)
            guess_dao.set_differences(pitch_value, play['play_id'])
            closest_guess = guess_dao.get_closest_on_play(play['play_id'])

            await message.channel.send(
                "Closed this play! " + "<@" + str(closest_guess[MEMBER_ID]) +
                "> was the closest with a guess of " + closest_guess[GUESSED_NUMBER] +
                " resulting in a difference of " + closest_guess[DIFFERENCE] + ".")

        # Likely due to too few parameters but could be any number of things
        # except :
        #     await message.channel.send( "Hey " + "<@" + str(message.author.id) + ">, you confused me with that message.  "
        #                             "To close an active pitch, the proper command is !resolve <pitch number> <swing_number>.  "
        #                             "Use that format and try again, ok?")

    if content.startswith('!leaderboard'):
        leaderboard_config = __parse_leaderboard_message__(content)

        if leaderboard_config.should_sort_by_pure_closest():
            values = guess_dao.fetch_closest(10)

            string_to_send = ''
            for i, value in enumerate(values):
                string_to_send += str(i + 1) + ': ' + value['member_name'] + ', ' + value['difference'] + '\n'

            await message.channel.send(string_to_send)

        elif leaderboard_config.should_sort_by_best_average():
            pass
        else:
            await message.channel.send(
                "I don't understand that leaderboard command, sorry!  I know it's a little confusing, so send me"
                " a !help message if you want the full rundown for how to make this work!")

    if content.startswith("!points"):
        pass #TODO

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
                   "!resolve <PITCH_NUMBER> --- Uses the pitch number and real swing number " \
                   "to figure out who was closest and ends the active play.\n" \
                   "<HELP MESSAGE NEEDS DOCUMENTATION FOR LEADERBOARD COMMAND!  PING KALI IF YOU'RE ANGRY!>\n"

    return help_message


def __parse_leaderboard_message__(message_content):
    return LeaderboardConfig(message_content)


def __parse_guess__(message_content):
    pieces = message_content.split(' ')
    try:
        return pieces[1]
    except TypeError:
        return None


def __parse_resolve_play__(message_content):
    pieces = message_content.split(' ')
    try:
        return pieces[1]
    except TypeError:
        return None


if __name__ == '__main__':
    args = sys.argv
    token = args[1]
    file_path = args[2]

    configs = Configs(file_path)
    databaseSession = DatabaseSession()

    play_dao = PlayDAO()
    guess_dao = GuessDAO()
    bot.run(token)

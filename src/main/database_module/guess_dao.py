from copy import deepcopy

from src.main.database_module.database_classes.db_classes import Guess
from src.main.db_session import DatabaseSession


MEMBER_ID = 'member_id'
PLAY_ID = 'play_id'
GUESSED_NUMBER = 'guessed_number'
DIFFERENCE = 'difference'
MEMBER_NAME = 'member_name'

class GuessDAO():
    db_string = None
    session = None
    Session = None
    engine = None

    _database_session = None

    def __init__(self):
        self._database_session = DatabaseSession()

    def insert(self, guess_info, allow_update=False):
        session = self._database_session.get_or_create_session()

        guess = Guess(
            member_id=guess_info[MEMBER_ID],
            play_id = guess_info[PLAY_ID],
            guessed_number = guess_info[GUESSED_NUMBER],
            member_name = guess_info[MEMBER_NAME]
        )

        existing_guess = self.__convert_all__(session\
            .query(Guess)\
            .filter(Guess.member_id == guess_info[MEMBER_ID], Guess.play_id == guess_info[PLAY_ID]))

        if len(existing_guess) == 0:
            session.add(guess)
            session.commit()
            return True
        elif allow_update:
            session\
                .query(Guess)\
                .filter(Guess.member_id == guess_info[MEMBER_ID], Guess.play_id == guess_info[PLAY_ID], Guess.member_name == guess_info[MEMBER_NAME])\
                .update({Guess.guessed_number: guess_info[GUESSED_NUMBER]})
            return True
        else:
            return False

    '''
       Converts the database object into a Dictionary, so that the database object is not passed out of the
       datastore layer.
    '''
    def __convert_all__(self, games):
        converted_games = []
        for game in games:
            game_dict = {}
            for column in game.__dict__:
                game_dict[column] = str(getattr(game, column))

            converted_games.append(deepcopy(game_dict))

        return converted_games

    def set_differences(self, pitch_value, play_id):
        session = self._database_session.get_or_create_session()
        games_to_update = self.__convert_all__(session.query(Guess).filter(Guess.play_id == play_id))

        for game in games_to_update:
            difference = self.calculate_difference(pitch_value, game[GUESSED_NUMBER])
            session.query(Guess).filter(Guess.member_id == game[MEMBER_ID], Guess.play_id == game[PLAY_ID]).update({Guess.difference: difference})

        session.commit()

    def calculate_difference(self, pitch_value, guess_value):
        pitched_number = int(pitch_value)
        possible_value = abs(int(guess_value) - pitched_number)

        if possible_value > 500:
            return 1000 - possible_value
        else:
            return possible_value

    def fetch_closest(self, num_to_fetch):
        session = self._database_session.get_or_create_session()

        return self.__convert_all__(
            session\
                .query(Guess)\
                .order_by(Guess.difference)\
                .limit(num_to_fetch)
        )

    def refresh(self):
        self._database_session.__create_new_session__() # I know, I know.  It's fine.

    def get_all_guesses_for_plays(self, play_ids):
        session = self._database_session.get_or_create_session()
        return self.__convert_all__(
            session
                .query(Guess)
                .filter(Guess.play_id.in_(play_ids))
        )

    def get_closest_on_play(self, play):
        session = self._database_session.get_or_create_session()

        # TODO: Make this a MAX query for ties
        converted_guesses = self.__convert_all__(
            session
                .query(Guess)
                .filter(Guess.play_id == play)
                .order_by(Guess.difference)
                .limit(1)
        )

        if len(converted_guesses) > 1:
            raise AssertionError("More than one best guess!  Can't continue!")
        elif len(converted_guesses) == 0:
            return None
        else:
            return converted_guesses[0]
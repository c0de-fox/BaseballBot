from copy import deepcopy

from src.main.db_session import DatabaseSession
from src.main.database_module.database_classes.db_classes import Play

PLAY_ID = 'play_id'
PITCH_VALUE = 'pitch_value'
CREATION_DATE = 'creation_date'

class PlayDAO():
    db_string = None
    session = None
    Session = None
    engine = None

    def __init__(self):
        pass

    def insert(self, play_info):
        session = DatabaseSession.session

        play = Play(
            play_id = play_info[PLAY_ID],
            pitch_value = play_info[PITCH_VALUE] if PITCH_VALUE in play_info else None,
            creation_date = play_info[CREATION_DATE]
        )

        session.add(play)
        session.commit()

    def get_play_by_id(self, input_id):
        session = DatabaseSession.session
        return self.__convert_all__(session.query(Play).filter(Play.play_id == input_id))

    '''
        Checks to see if there is a play that is currently active or not
    '''
    def is_active_play(self):
        return self.get_active_play() != None

    def get_active_play(self):
        session = DatabaseSession.session
        plays = self.__convert_all__(session.query(Play).filter(Play.pitch_value == None))

        if len(plays) > 1:
            raise AssertionError("More than one active play!  Can't continue!")
        elif len(plays) == 0:
            return None
        else:
            return plays[0]

    def resolve_play(self, input_pitch):
        session = DatabaseSession.session
        active_id = self.get_active_play()

        session\
            .query(Play)\
            .filter(Play.pitch_value == None)\
            .update({Play.pitch_value: input_pitch})
        session.commit()

        return active_id

    '''
       Converts the database object into a Dictionary, so that the database object is not passed out of the
       datastore layer.
    '''
    def __convert_all__(self, plays):
        converted_plays = []
        for play in plays:
            play_dict = {}
            for column in play.__dict__:
                play_dict[column] = str(getattr(play, column))

            converted_plays.append(deepcopy(play_dict))

        return converted_plays

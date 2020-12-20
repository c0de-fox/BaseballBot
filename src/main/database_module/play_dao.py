from copy import deepcopy
from sqlalchemy.sql.expression import and_

from src.main.db_session import DatabaseSession
from src.main.database_module.database_classes.db_classes import Play

import datetime

PLAY_ID = 'play_id'
PITCH_VALUE = 'pitch_value'
CREATION_DATE = 'creation_date'
SERVER_ID = 'server_id'

class PlayDAO():
    db_string = None
    session = None
    Session = None
    engine = None
    _database_session = None

    def __init__(self):
        self._database_session = DatabaseSession()

    def insert(self, play_info):
        session = self._database_session.get_or_create_session()

        play = Play(
            play_id = play_info[PLAY_ID],
            pitch_value = play_info[PITCH_VALUE] if PITCH_VALUE in play_info else None,
            creation_date = play_info[CREATION_DATE],
            server_id = play_info[SERVER_ID]
        )

        session.add(play)
        session.commit()

    def get_play_by_id(self, input_id):
        session = self._database_session.get_or_create_session()
        return self.__convert_all__(session.query(Play).filter(Play.play_id == input_id))

    def get_all_plays_after(self, timestamp, input_server_id):
        session = self._database_session.get_or_create_session()
        return self.__convert_all__(session.query(Play).filter(and_(Play.server_id == str(input_server_id), Play.creation_date > timestamp)))

    def get_all_plays_on_server(self, input_server_id, earliest_timestamp):
        session = self._database_session.get_or_create_session()
        converted_datetime = datetime.datetime.fromtimestamp(earliest_timestamp / 1000.0)

        return self.__convert_all__(session.query(Play).filter(and_(Play.server_id == str(input_server_id), Play.creation_date > converted_datetime)))

    '''
        Checks to see if there is a play that is currently active or not
    '''
    def is_active_play(self, server_id):
        return self.get_active_play(server_id) != None

    def get_active_play(self, input_server_id):
        session = self._database_session.get_or_create_session()
        plays = self.__convert_all__(session.query(Play).filter(and_(Play.pitch_value == None, Play.server_id == str(input_server_id))))

        if len(plays) > 1:
            raise AssertionError("More than one active play!  Can't continue!")
        elif len(plays) == 0:
            return None
        else:
            return plays[0]

    def resolve_play(self, input_pitch, input_server_id):
        session = self._database_session.get_or_create_session()
        active_id = self.get_active_play(input_server_id)

        session\
            .query(Play)\
            .filter(and_(Play.pitch_value == None, Play.server_id == str(input_server_id)))\
            .update({Play.pitch_value: input_pitch})
        session.commit()

        return active_id

    def refresh(self):
        self._database_session.__create_new_session__() # I know, I know.  It's fine.

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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import sqlite3
sys.path.append('../../../../../../src')

from src.main.configs import Configs, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME

'''
Stores a database session for use throughout the application.  Must be initialized at startup before any database calls
are made and AFTER the Configurations are setup.

This shouldn't need to be touched after startup.  To use, see the sqlalchemy docs...or just start by calling Session()
and then use it to handle the necessary CRUD operations.

You should NOT instantiate this in any method except the main application runner
'''
class DatabaseSession():
    _session = None

    def __init__(self):
        self.__create_new_session__()

    def __create_new_session__(self):
        if self._session is not None:
            self._session.close()

        config_map = Configs.configs
        db_string = self._pgsql_conn_string_(config_map)
        Session = sessionmaker(create_engine(db_string))
        self._session = Session()

        return self._session

    def get_or_create_session(self):
        try:
            self._session.connection()
            return self._session
        except: # The linter can scream all it wants, this makes sense.  If it's this broke, we want a new one anyway.
            return self.__create_new_session__()

    # Look, this kinda sucks.  But it's for fun and friends and I'm doing it quick and dirty.
    def _pgsql_conn_string_(self, config_map):
        return 'postgresql://%s:%s@%s/%s' % \
               (config_map[DATABASE_USERNAME], config_map[DATABASE_PASSWORD], config_map[DATABASE_HOST], config_map[DATABASE_NAME])

    def _sqlite_conn_string(self, config_map):
        return "sqlite:///ghostball.db"
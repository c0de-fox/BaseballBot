from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append('../../../../../src')

from src.main.configs import Configs, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME

'''
Stores a database session for use throughout the application.  Must be initialized at startup before any database calls
are made and AFTER the Configurations are setup.

This shouldn't need to be touched after startup.  To use, see the sqlalchemy docs...or just start by calling Session()
and then use it to handle the necessary CRUD operations.

You should NOT instantiate this in any method except the main application runner
'''
class DatabaseSession():
    session = None

    def __init__(self):
        config_map = Configs.configs
        db_string = 'postgresql://%s:%s@%s/%s' % \
                    (config_map[DATABASE_USERNAME], config_map[DATABASE_PASSWORD], config_map[DATABASE_HOST], config_map[DATABASE_NAME])
        Session = sessionmaker(create_engine(db_string))
        DatabaseSession.session = Session()
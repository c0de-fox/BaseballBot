# Names of Configurations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_USERNAME = 'ghost_user'
DATABASE_PASSWORD = 'root'
DATABASE_HOST = '192.168.0.11'
DATABASE_PORT = '5432'
DATABASE_NAME = 'ghostball'
SEASON_1_SPREADSHEET_ID = 's1_spreadsheet_id'
SEASON_2_SPREADSHEET_ID = 's2_spreadsheet_id'
PLAYER_SPREADSHEET = 'player_spreadsheet'

'''
Main source for configurations fetched from a startup configuration file.  Includes the ability to fetch all, or fetch
one configuration once the file is loaded.

You'll find the names of these configs above as constants that can be used throughout the rest of this repository
'''
class Configs():
    configs = {}

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.__load_configs__()

    '''
    Fetches a single configuration by the name of that configuration.
    Returns None if that configuration does not exist
    '''
    def get_config_by_name(self, name):
        try:
            return Configs.configs[name]
        except KeyError:
            return None

    '''
    Fetches all configurations and returns them as a dictionary of config_key -> config_value
    '''
    def get_all_configs(self):
        return Configs.configs

    '''
    Performs the initial load of configurations from a startup configuration file
    '''
    def __load_configs__(self):
        Configs.configs = {}
        config_file = open(self.config_file_path, 'r')
        for line in config_file:
            split_line = line.split('=')
            Configs.configs[split_line[0]] = split_line[1].strip('\n')
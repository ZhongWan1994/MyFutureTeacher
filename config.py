import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# 读取 General 节的配置项
LANGUAGE = config.get('General', 'LANGUAGE')
SPEED = config.get('General', 'EN_SPEED')
VOB_LIB = config.get('General', 'EN_VOB_LIB')
REVIEW = config.getboolean('General', 'REVIEW')
EPISODE_LEN = config.getint('General', 'EPISODE_LEN')
SAMPLE_VOCAB_NUM = config.getint('General', 'SAMPLE_EN_VOCAB_NUM')

# 读取 Paths 节的配置项
SELECT_HISTORY_PATH = config.get('Paths', 'SELECT_HISTORY_PATH')
SELECT_PATH = config.get('Paths', 'SELECT_PATH')
TOPIC_PATH = config.get('Paths', 'TOPIC_PATH')
TOPIC_HISTORY_PATH = config.get('Paths', 'TOPIC_HISTORY_PATH')
DIALOGUE_BOARD_PATH = config.get('Paths', 'DIALOGUE_BOARD_PATH')
EN_TEXT2AUDIO_PATH = config.get('Paths', 'EN_TEXT2AUDIO_PATH')
JAP_TEXT2AUDIO_PATH = config.get('Paths', 'JAP_TEXT2AUDIO_PATH')
AUDIO2TEXT_PATH = config.get('Paths', 'AUDIO2TEXT_PATH')
AUDIO_OUTPUT_PATH = config.get('Paths', 'AUDIO_OUTPUT_PATH')

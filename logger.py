import logging
from config import Config
from logging.handlers import WatchedFileHandler

LOG_FILE = Config().log_file


class Logger:
    logger = logging
    handler_name = 'unknown'
    FORMAT = '[%(asctime)s] %(message)s'

    def __init__(self):
        self.ch = WatchedFileHandler(LOG_FILE)
        logging.basicConfig(
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=(self.ch, ),
            format=self.FORMAT)

    def log(self, message):
        self.logger.info(f'[{self.handler_name}] {message}')

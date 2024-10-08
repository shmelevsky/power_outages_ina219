import os


class Config:
    _instance = None

    def __init__(self):
        try:
            envir = os.environ
            # DataBase Settings
            self.db_host: str = envir['db_host']
            self.db_name: str = envir['db_name']
            self.db_user: str = envir['db_user']
            self.db_pass: str = envir['db_pass']
            # Logger
            self.log_file: str = envir['log_file']
            # Telegram
            self.telega_token: str = envir['telega_token']
            self.telega_chat_id: int = int(envir['telega_chat_id'])
            self.message_thread_id: int = int(envir['message_thread_id'])
            # Device
            self.device: str = envir.get('device', 'ina219')
            self.i2c_address =  int(envir.get('i2c_address', '0x42'), 16)
            self.i2c_busnum = int(envir.get('i2c_busnum', 1))
        except Exception as err:
            print(f'You should define an environment variable: {err}')
            exit(1)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

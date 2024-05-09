import requests
from config import Config
from typing import Optional
config = Config()

TOKEN = config.telega_token
CHAT_ID = config.telega_chat_id
MSG_THREAD_ID = config.message_thread_id


class Error:
    """
    Initialize an Error instance.

    Args:
    error (str): The error message.
    """
    def __init__(self, error: str, status_code: int):
        self.error: str = error
        self.status_code: int = status_code


class TelegaMSGsender:
    def __init__(self, token: str = TOKEN, chat_id: int = CHAT_ID, message_thread_id:int=MSG_THREAD_ID) -> None:
        """
        Initialize a TelegaMSGsender instance.

        Args:
        token (str): The Telegram bot token.
        chat_id (int): The Telegram chat ID.
        """
        self.token: str = token
        self.chat_id: int = chat_id
        self.message_thread_id: int = message_thread_id

    def send_msg(self, msg: str) -> Optional[Error]:
        """
        Send a message to a Telegram chat.

        Args:
        msg (str): The message to send.

        Returns:
        Optional[Error]: An Error instance if there was an error in sending the message, None otherwise.
        """
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?message_thread_id={self.message_thread_id}&chat_id={self.chat_id}&text={msg}"
        response = requests.get(url)
        if response.status_code == 200:
            return
        else:
            error = Error(
                error=response.text,
                status_code=response.status_code
            )
            return error

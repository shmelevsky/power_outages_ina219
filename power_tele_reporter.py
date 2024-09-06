from db import ConnectToDB
from telega_msg_sender import TelegaMSGsender
from typing import Tuple, Optional
from logger import Logger
import traceback
from datetime import datetime
from time import sleep


class PowerTeleReporter(Logger):
    def __init__(self):
        """
        Initialize the PowerTeleReporter class.
        """
        super().__init__()
        self.handler_name = 'PowerTeleReporter'

    def get_events_from_db(self) -> Tuple[bool, Optional[list]]:
        """
        Get power events from the database that have not been sent to Telegram yet.

        Returns: Tuple[bool, Optional[list]]: A tuple with a boolean indicating the success of the operation and a
        list of events. - The first boolean, if False, means there was an error in retrieving data from the database.
        - The list contains tuples of (date, event, sent), where date is the timestamp of the event, event is a
        boolean representing the event type (True for power available, False for power outage), and sent is a boolean
        indicating if the event has been sent to Telegram.
        """

        try:
            with ConnectToDB() as conn:
                conn.cur.execute('SELECT * FROM  outages WHERE sent=false order by DATE;')
                events = conn.cur.fetchall()
                return True, events

        except Exception as err:
            self.log(f'DataBase. Error getting data from database {err}')
            self.log("=======================TraceBack================================")
            self.log(traceback.format_exc())
            self.log("================================================================")
            return False, None

    @staticmethod
    def convert_time(unix_time: int) -> str:
        """
        Convert a Unix timestamp to a formatted datetime string.

        Args:
        unix_time (int): The Unix timestamp to convert.

        Returns:
        str: The formatted datetime string in the format 'YYYY-MM-DD HH:MM'.
        """
        return datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M')

    def send_msg(self, msg: str) -> bool:
        """
        Send a message to a Telegram chat using TelegaMSGsender.

        Args:
        msg (str): The message to send.

        Returns:
        bool: True if the message was sent successfully, False otherwise.
        """
        tg_sender = TelegaMSGsender()
        try:
            error = tg_sender.send_msg(msg)
            if not error:
                return True
            else:
                self.log(
                    f'Error sending messages to Telegram. Status_code:{error.status_code}. Message: {error.error}'
                )
            return False
        except Exception as err:
            self.log(f'DataBase. Error sending messages to Telegram {err}')
            self.log("=======================TraceBack================================")
            self.log(traceback.format_exc())
            self.log("================================================================")
            return False

    def update_status_to_sent(self, date: int) -> bool:
        """
        Update the status of an event in the database to indicate it has been sent to Telegram.

        Args:
        date (int): The timestamp of the event to update.

        Returns:
        bool: True if the update was successful, False otherwise.
        """
        try:
            with ConnectToDB() as conn:
                conn.cur.execute(f"UPDATE outages SET sent=true where date={date}")
                conn.db.commit()
                return True
        except Exception as err:
            self.log(f'DataBase. Error updating data in database. Method: update_status_to_sent.  {err}')
            self.log("=======================TraceBack================================")
            self.log(traceback.format_exc())
            self.log("================================================================")
            return False

    @staticmethod
    def format_time(seconds:int):
        if seconds < 3600:  # Less than an hour
            minutes = seconds // 60
            return f"{minutes} min"
        elif seconds < 86400:  # Less than a day
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hr {minutes} min"
        else:  # More than a day
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            return f"{days} d {hours} hr {minutes} min"


if __name__ == '__main__':
    reporter = PowerTeleReporter()
    while True:

        status, events = reporter.get_events_from_db()
        if not status:
            # Something wrong with Database
            sleep(1)
            continue

        for ev in events:
            date, event, _, duration = ev
            dt = reporter.convert_time(date)
            if duration:
                duration_formated = reporter.format_time(duration)
            else:
                duration_formated = 'Не вдалося визначити'
            if not event:
                msg = f'\U0000274c {dt} Відсутнє електропостачання.\nЕлектроенергія була: {duration_formated}'
            else:
                msg = f'\U00002705 {dt} Електропостачання відновлено!\nТривалісь знеструмлення: {duration_formated}'

            result = reporter.send_msg(msg)

            if result:
                reporter.update_status_to_sent(date)
            sleep(1)

        sleep(1)

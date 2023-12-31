from ina219_interface import INA219Interface
from db import ConnectToDB
from time import sleep, time
from logger import Logger
from typing import Tuple, Optional
import traceback


class PowerChecker(Logger):
    def __init__(self):
        super().__init__()
        self.handler_name = 'PowerChecker'
        self.log('Starting PowerChecker')

    def get_power_status(self) -> Tuple[bool, bool]:
        """
        it returns Tuple[boot, bool]
        1st boolean, if it returns false, it means the sensor didn't trigger, and a reattempt is needed.
        2nd boolean, if it returns false, it means a power outage occurred.
        """
        ina219 = INA219Interface()
        error, power = ina219.get_power()
        if error:
            self.logger(f'INA219. Error getting power state {error.error}')
            return False, False
        if power < 1:
            return True, False
        else:
            return True, True

    def get_last_status_from_db(self) -> Tuple[bool, Optional[bool]]:
        """
        It returns two booleans.
        The first boolean, if false, means it couldn't retrieve data from the database; the database does not work.
        The second boolean represents the last record of electricity state changes.
        """
        try:
            with ConnectToDB() as conn:
                conn.cur.execute('SELECT * FROM  outages ORDER BY date DESC')
                _, event, _ = conn.cur.fetchone()
                return True, event

        except Exception as err:
            self.log(f'DataBase. Error getting data from database {err}')
            self.log("=======================TraceBack================================")
            self.log(traceback.format_exc())
            self.log("================================================================")
            return False, None

    def insert_result(self, event: bool) -> None:
        try:
            with ConnectToDB() as conn:
                sql = "INSERT INTO outages VALUES ({},{},{})".format(int(time()), event, False)
                conn.cur.execute(sql)
                conn.db.commit()
        except Exception as err:
            self.log(f'DataBase. Error insert data to database {err}')
            self.log("=======================TraceBack================================")
            self.log(traceback.format_exc())
            self.log("================================================================")


if __name__ == '__main__':
    power_checker = PowerChecker()
    while True:
        ina219_work_status, power_status = power_checker.get_power_status()
        # If the sensor failed to trigger for any reason, we skip the iteration.
        if not ina219_work_status:
            sleep(2)
            continue
        db_status, last_event = power_checker.get_last_status_from_db()

        if not db_status:
            sleep(2)
            continue

        if (last_event is None) or (last_event != power_status):
            power_checker.insert_result(power_status)

        sleep(1)

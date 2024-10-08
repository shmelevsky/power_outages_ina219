from ina219_interface import INA219Interface
from db import ConnectToDB
from time import sleep, time
from logger import Logger
from typing import Tuple, Optional
import traceback
from config import Config

config = Config()
DEVICE = config.device
i2c_address = config.i2c_address
i2c_busnum = config.i2c_busnum

class PowerChecker(Logger):
    def __init__(self):
        super().__init__()
        self.handler_name = 'PowerChecker'
        self.log('Starting PowerChecker')


    def get_power_status(self) -> Tuple[bool, bool, Optional[int|float]]:
        """
        it returns Tuple[boot, bool, Optional[int|float]]
        1st boolean, if it returns false, it means the sensor didn't trigger, and a reattempt is needed.
        2nd boolean, if it returns false, it means a power outage occurred.
        Optional[int|float] - cur current or power
        """
        ina219 = INA219Interface(address=i2c_address, busnum=i2c_busnum)
        if DEVICE == 'ups_hut_b':
            return self._check_ups_hut_b(ina219)
        else:
            return self._check_default_device(ina219)

    def _check_ups_hut_b(self, ina219: INA219Interface) -> Tuple[bool, bool, Optional[int|float]]:
        below_threshold_attempts = 0
        above_threshold_attempts = 0
        total_attempts = 0
        while True:
            error, current = ina219.get_current()
            if error:
                self.log(f'INA219. Error getting current state {error.error}')
                return False, False, None
            if total_attempts == 100:
                self.log(f'INA219. Seems current is flapping. More than 100 total attempts')
                return False, False, None
            if current < -320:
                if below_threshold_attempts >= 3:
                    # self.log(f'Detect power outage. Current: {current} mA')
                    return True, False, current
                below_threshold_attempts += 1
                above_threshold_attempts = 0
            else:
                if above_threshold_attempts >= 3:
                    # self.log(f'Electricity is back. Current: {current} mA')
                    return True, True, current
                above_threshold_attempts += 1
                below_threshold_attempts = 0
            total_attempts += 1
            sleep(1)

    def _check_default_device(self, ina219: INA219Interface) -> Tuple[bool, bool, Optional[int|float]]:
        # The INA219 is connected in series with the UPS LX-2BUPS.
        error, power = ina219.get_power()
        if error:
            self.log(f'INA219. Error getting power state {error.error}')
            return False, False, None
        if power < 1:
            return True, False, power
        else:
            return True, True, power

    def get_last_status_from_db(self) -> Tuple[bool, Optional[bool], Optional[int]]:
        """
        It returns two booleans.
        The first boolean, if false, means it couldn't retrieve data from the database; the database does not work.
        The second boolean represents the last record of electricity state changes.
        """
        try:
            with ConnectToDB() as conn:
                conn.cur.execute('SELECT * FROM  outages ORDER BY date DESC')
                date_time, event, _, _ = conn.cur.fetchone()
                return True, date_time, event

        except Exception as err:
            self.log(f'DataBase. Error getting data from database {err}')
            self.log("=======================TraceBack================================")
            self.log(traceback.format_exc())
            self.log("================================================================")
            return False, None, None

    def insert_result(self, event: bool, event_duration:int) -> None:
        try:
            with ConnectToDB() as conn:
                sql = "INSERT INTO outages VALUES ({},{},{},{})".format(int(time()), event, False, event_duration)
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
        ina219_work_status, power_status, current_or_power  = power_checker.get_power_status()
        # If the sensor failed to trigger for any reason, we skip the iteration.
        if not ina219_work_status:
            sleep(2)
            continue
        try:
            db_status, date,last_event = power_checker.get_last_status_from_db()
        # probably no records in db. It whill be first
        except TypeError:
            duration = 0
            power_checker.insert_result(power_status, duration)
            continue

        if not db_status:
            sleep(2)
            continue

        if DEVICE == 'ups_hut_b':
            unit = 'mA'
        else:
            unit = 'W'

        if (last_event is None) or (last_event != power_status):
            power_checker.log(f'Power state is changed. Now {current_or_power} {unit}')
            duration = int(time()) - date
            power_checker.insert_result(power_status, duration)
        sleep(1)

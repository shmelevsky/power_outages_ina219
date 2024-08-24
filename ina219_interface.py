#!/usr/bin/env python
from ina219 import INA219
from ina219 import DeviceRangeError
from typing import Optional, Tuple


class Error:
    def __init__(self, err: DeviceRangeError | str ):
        self.error: DeviceRangeError | str = err


class INA219Interface:
    def __init__(self, busnum:int = 0) -> None:
        SHUNT_OHMS = 0.1
        self.ina = INA219(SHUNT_OHMS, busnum=busnum)
        self.ina.configure()

    def get_power(self) -> Tuple[Optional[Error], Optional[int | float]]:
        try:
            return None, self.ina.power()
        except DeviceRangeError as e:
            # Current out of device range with specified shunt resistor
            return Error(err=e), None
        except Exception as e:
            error = Error(err=f'unexpected error: {e}')
            return error, None

    def get_current(self) -> Tuple[Optional[Error], Optional[int | float]]:
        try:
            return None, self.ina.current()
        except DeprecationWarning as e:
            # Current out of device range with specified shunt resistor
            return Error(err=e), None
        except Exception as e:
            error = Error(err=f'unexpected error: {e}')
            return error, None

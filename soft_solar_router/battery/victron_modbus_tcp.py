from datetime import datetime, time, timedelta
from typing import List
import logging
from pymodbus.constants import Defaults
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder

from soft_solar_router.application.interfaces.battery import (
    Battery,
    BatteryData,
    PowerUnit,
)

logger = logging.getLogger("victron_modbus_tcp")


class VictronModbusTcp(Battery):
    def __init__(self, host, max_duration: time) -> None:
        """
        Initialize the Victron Modbus TCP client.

        Parameters:
            host (str): The host IP address.
            max_duration (time): The maximum duration of the time series. older data
                that are older than `max_duration` will be discarded.

        Initializes the Modbus client with the given host and port, sets the timeout
        and retries, and initializes the duration and serie.

        Returns:
            None
        """
        Defaults.Timeout = 25
        Defaults.Retries = 5
        self.client = ModbusClient(host, port="502")
        self.duration = timedelta(
            hours=max_duration.hour,
            minutes=max_duration.minute,
            seconds=max_duration.second,
        )
        self.serie = []

    def get(self, now: datetime) -> List[BatteryData]:
        self.constraint_serie(now)
        return self.serie

    def update(self, now: datetime) -> BatteryData:
        
        sample = BatteryData(
            timestamp=now,
            instant_power=PowerUnit.FromWatts(0),
            soc_percent=-11,
            state="error",
        )
        
        try:
            sample = BatteryData(
                timestamp=now,
                instant_power=self.read_power(),
                soc_percent=self.read_soc(),
                state=self.read_state(),
            )
        except Exception as e:
            logger.error(e)
      
        self.serie.append(sample)
        self.constraint_serie(now)
        logger.debug(sample)
        return sample
    
    def ensure_min_soc(self, value: float) -> None:
        """
        Set the minimum SOC configured in the ESS.
        """
        try:
            min_soc = self.read_min_soc()
            if abs(min_soc - value) > 0.5:
                logger.info(f"Updating min_soc from {min_soc} to {value}")
                self.set_min_soc(value)
        except Exception as e:
            logger.error(e)
    

    def read_battery_life_state(self) -> int:
        result = self.client.read_input_registers(2900, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big
        )
        return decoder.decode_16bit_uint()

    def read_ess_mode(self) -> int:
        result = self.client.read_input_registers(2902, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big
        )
        return decoder.decode_16bit_uint()

    def read_min_soc(self) -> int:
        """
        Read the minimum SOC configured in the ESS.
        """
        result = self.client.read_input_registers(2901, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big
        )
        return decoder.decode_16bit_uint() / 10

    def set_min_soc(self, value: float) -> None:
        """
        Set the minimum SOC configured in the ESS.

        Parameters:
            value (float): The minimum SOC percentage (0-100).
        """
        self.client.write_register(2901, int(value * 10))

    def read_power(self) -> PowerUnit:
        result = self.client.read_input_registers(842, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big
        )
        return PowerUnit.FromWatts(decoder.decode_16bit_int())

    def read_soc(self) -> int:
        result = self.client.read_input_registers(843, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big
        )
        return decoder.decode_16bit_uint()

    def read_state(self) -> str:

        result = self.client.read_input_registers(844, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big
        )
        state_id = decoder.decode_16bit_uint()
        state = "Idle"
        if state_id == 1:
            state = "Charging"
        if state_id == 2:
            state = "Discharging"
        return state

    def constraint_serie(self, now: datetime):
        """
        remove from serie all the sample older than duration

        given a datetime `now`, this function will remove all the BatteryData
        from the serie that are older than `now` - `duration`.

        This is typically used to remove old data from the serie when a new
        BatteryData is available
        """

        def fresh_data(sample: BatteryData):
            return sample.timestamp > now - self.duration

        self.serie = list(filter(fresh_data, self.serie))

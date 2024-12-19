from DFRobot_MultiGasSensor import *
import serial
import time


class COSensor:
    def __init__(self, i2c_1, address):
        self.i2c_1 = i2c_1
        self.address = address
        self.sensor = DFRobot_MultiGasSensor_I2C(i2c_1, address)

    def read_co_sensor(self):
        con = self.sensor.read_gas_concentration()
        gas_data = {"concentration": con}
        return gas_data

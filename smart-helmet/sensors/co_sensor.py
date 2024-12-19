import asyncio
from DFRobot_MultiGasSensor import *


class COSensor:
    def __init__(self, i2c_1, address):
        self.i2c_1 = i2c_1
        self.address = address
        self.sensor = DFRobot_MultiGasSensor_I2C(i2c_1, address)

    async def read_co_sensor(self):
        # Use asyncio.to_thread to run the blocking read in a separate thread
        con = await asyncio.to_thread(self.sensor.read_gas_concentration)
        gas_data = {"concentration": con}
        return gas_data


async def main():
    co_sensor = COSensor(i2c_1, address)
    data = await co_sensor.read_co_sensor()
    print(data)

# Run the main function
asyncio.run(main())

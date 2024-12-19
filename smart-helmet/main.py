import time
import json
import board
import asyncio
import threading
from sensors.gnss_sensor import GSMModule
from sensors.LoRa_module import LoRaModule
from sensors.bluetooth_module import collect_ble_data
from sensors.co_sensor import COSensor
from sensors.temp_sensor import TemperatureSensor
from sensors.imu_sensor import IMUSensor
from mqtt.mqtt_module import *
#from sreaming.camera_stream import *



class HelmetApp:
    def __init__(self):
        # Initialize sensors
        self.imu = IMUSensor(i2c=board.I2C())
        self.temp = TemperatureSensor(i2c=board.I2C())
        self.co = COSensor(i2c_1=0x01, address=0x74)
        self.gsm = GSMModule()
        self.lora = LoRaModule()

    async def check_connectivity(self):
        for _ in range(3):  # Try 3 times
            if await self.lora.check_connection():
                print("LoRa is the best connection.")
                return "LoRa"
            if await self.gsm.check_connection():
                print("4G is the best connection.")
                return "4G"
        print("Failed to connect to LoRa or GSM!")
        return None

    async def run(self):
        while True:
            connection = await self.check_connectivity()
            if connection == "LoRa":
                await self.lora.send_data("Real-time data")
            elif connection == "4G":
                self.gsm.send_data("Real-time data")
            else:
                print("No valid connection. Retrying...")
            await asyncio.sleep(5)  # Recheck every 5 seconds



if __name__ == "__main__":
    app = HelmetApp()
    asyncio.run(app.run())

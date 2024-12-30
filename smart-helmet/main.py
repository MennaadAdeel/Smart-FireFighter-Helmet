import time
import json
import asyncio
import logging
import subprocess
from sensors.gnss_sensor import *
from mqtt.mqtt_module import *
from streaming.camera_stream import *
from streaming.mice_stream import *
from streaming.speaker_stream import *


# GSM module's config
SERIAL_PORT = '/dev/ttyS0'  
BAUDRATE = 115200

# MQTT config
broker_address = "broker.emqx.io"
broker_port = 1883
broker_topic = "helmet/data"
client_id = "client_id"

mqtt_message = {'latitude': 0, 'longitude': 0}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class HelmetApp:
    def __init__(self):
        # Initialize sensors
        self.gsm = GSMModule(SERIAL_PORT, BAUDRATE) 
        self.client = init_mqtt_client(broker_address, broker_port)
        self.mediamtx_process = None

    async def check_connectivity(self):
        # Check Network Connectivity
        await self.bt_manager.scan_devices(timeout=5)  # Increased timeout for scanning
        for _ in range(3):  # Try 3 times
            if await self.gsm.is_connected():
                logging.info("GSM module is connected to the network.")
                strength = await self.gsm.get_signal_strength()
            
                # Interpret RSSI value
                if strength == 99:
                    logging.warning("Signal strength unknown or not detectable.")
                    await self.gsm.restart()
                elif strength <= 17:
                    logging.warning("Weak signal detected.")
                    await self.bt_manager.communicate_with_device("ESP32_LoRa", "Weak signal, be careful.")
                elif 18 <= strength <= 31:
                    logging.info("Good signal.")
                    break
            else:
                logging.error("No GSM signal detected.")
                await self.bt_manager.communicate_with_device("ESP32_LoRa", "No signal detected")
    
    async def collect_sensor_data(self):
        try:
            # Get GPS location 
            gps_latitude, gps_longitude = await self.gsm.get_gps_location()
            if gps_latitude and gps_longitude:
                mqtt_message["latitude"] = gps_latitude
                mqtt_message["longitude"] = gps_longitude
            else:
                logging.error("Failed to get GPS location.")
           
                
        except Exception as e:
            logging.error(f"Error collecting sensor data: {e}")

    async def publish_data(self, client, topic, message):
            try:
                # Convert the message to a JSON format if necessary
                json_message = json.dumps(message)
                
                # Publish the message
                result = client.publish(topic, json_message)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logging.info(f"Successfully published data to {topic}")
                else:
                    logging.error(f"Failed to publish data to {topic}, result: {result.rc}")
            except Exception as e:
                logging.error(f"Error publishing data: {e}")
         

    async def run(self):
        # Start MediaMTX process asynchronously
        await self.start_mediamtx()
        
        while True:
            await self.check_connectivity()
            await asyncio.sleep(3)  # Scan every 60 seconds
            
            # Collect sensor data
            await self.collect_sensor_data()
            
            # Publish data to MQTT
            await self.publish_data(self.client, broker_topic, mqtt_message)
            await asyncio.sleep(1)  # Give some time before repeating
        


if __name__ == "__main__":
    print("Running updated script version.")
    app = HelmetApp()
    asyncio

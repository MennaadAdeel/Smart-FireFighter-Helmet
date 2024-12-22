import time
import json
import asyncio
import logging
import subprocess
from sensors.gnss_sensor import GSMModule
from sensors.bluetooth_module import BluetoothManager
from sensors.co_sensor import COSensor
from mqtt.mqtt_module import init_mqtt_client, publish_data
from streaming.camera_stream import CameraStream
from streaming.mice_stream import MicrophoneStream
from streaming.speaker_stream import SpeakerStream


# GSM module's config
SERIAL_PORT = '/dev/ttyS0'  
BAUDRATE = 115200

# MQTT config
broker_address = "broker_address"
broker_port = 1883
broker_topic = "helmet/data"
client_id = "client_id"
mqtt_message = {'co': 0, 'latitude': 0, 'longitude': 0, 'imu': 0, 'temp': 0, 'heartrate': 0}
flash_to_Heartrate = {'flash1': 0, 'flash2': 0}

# Bluetooth setup
device_names = ["ESP32_LoRa", "ESP32_Flash_1", "ESP32_Flash_2", "ESP32_HeartRate"]

# Configuration for MediaMTX
MEDIA_MTX_PATH = "/home/Helmet/myenv/stream/mediamtx"
CONFIG_FILE = "/home/Helmet/myenv/stream/mediamtx.yml"
STREAM_PATH = "cam1"
HOST = "192.168.1.11"
WEBRTC_PORT = 8889

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class HelmetApp:
    def __init__(self):
        # Initialize sensors
        self.gsm = GSMModule(SERIAL_PORT, BAUDRATE) 
        self.bt_manager = BluetoothManager(device_names) 
        self.client = init_mqtt_client(broker_address, broker_port, client_id)
        self.mediamtx_process = None

    async def check_connectivity(self):
        # Check Network Connectivity
        await self.bt_manager.scan_devices()
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

    # Function to start MediaMTX server
    async def start_mediamtx(self):
        logging.info("Starting MediaMTX...")
        try:
            self.mediamtx_process = subprocess.Popen(
                [MEDIA_MTX_PATH, "-conf", CONFIG_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return self.mediamtx_process
        except Exception as e:
            logging.error(f"Failed to start MediaMTX: {e}")
            return None

    # Function to generate WebRTC stream URL
    def generate_webrtc_url(self):
        return f"http://{HOST}:{WEBRTC_PORT}/{STREAM_PATH}"

    # Function to monitor MediaMTX logs (optional)
    def monitor_mediamtx_logs(self):
        if self.mediamtx_process:
            try:
                while self.mediamtx_process.poll() is None:
                    output = self.mediamtx_process.stdout.readline()
                    if output:
                        logging.info(output.decode().strip())
            except KeyboardInterrupt:
                logging.info("Shutting down MediaMTX...")
                self.mediamtx_process.terminate()
    
    async def collect_sensor_data(self):
        try:
            # Get GPS location 
            gps_latitude, gps_longitude = await self.gsm.get_gps_location()
            if gps_latitude and gps_longitude:
                mqtt_message["latitude"] = gps_latitude
                mqtt_message["longitude"] = gps_longitude
            else:
                logging.error("Failed to get GPS location.")
                
            # Receive data from ESP32_LoRa (IMU , Temp)
            imu_temp_data = await self.bt_manager.communicate_with_device("ESP32_LoRa")
            if imu_temp_data:
                mqtt_message["imu"] = imu_temp_data   # Append IMU and Temp to MQTT message
            else:
                logging.error("Failed to get IMU and Temp data.")
            
            # Receive data from ESP32_Flash_1 
            flash1_data = await self.bt_manager.communicate_with_device("ESP32_Flash_1")
            if flash1_data:
                flash_to_Heartrate['flash1'] = flash1_data # Append Flash1 data to Heart rate
            else:
                logging.error("Failed to get Flash1 data.")
            
            # Receive data from ESP32_Flash_2
            flash2_data, flash2_co = await self.bt_manager.communicate_with_device("ESP32_Flash_2")
            if flash2_data:
                flash_to_Heartrate['flash2'] = flash2_data # Append Flash2 data to Heart rate
                flash_to_Heartrate['co'] = flash2_co        # Append CO data to Heart rate
            else:
                logging.error("Failed to get Flash2 data.")
                
            # Send data to heart rate module
            await self.bt_manager.communicate_with_device("ESP32_HeartRate", flash_to_Heartrate)
            
            # Receive data from heart rate module
            heartrate_data = await self.bt_manager.communicate_with_device("ESP32_HeartRate")
            if heartrate_data:
                mqtt_message['heartrate'] = heartrate_data    # Append Heart rate data to MQTT message
            else:
                logging.error("Failed to get Heart rate data.")
                
        except Exception as e:
            logging.error(f"Error collecting sensor data: {e}")

    
      

    async def run(self):
        # Start MediaMTX process asynchronously
        await self.start_mediamtx()
        
        while True:
            await self.check_connectivity()
            await asyncio.sleep(1)  # Give some time to connect
            
            # Collect sensor data
            await self.collect_sensor_data()
            
            # Publish data to MQTT
            await self.publish_data(self.client, broker_topic, mqtt_message)
            await asyncio.sleep(1)  # Give some time before repeating
            
            # Clear the data after publishing
            flash_to_Heartrate.clear()
            mqtt_message.clear()


if __name__ == "__main__":
    app = HelmetApp()
    asyncio.run(app.run())

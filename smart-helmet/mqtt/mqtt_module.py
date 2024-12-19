import paho.mqtt.client as mqtt
import json
import logging


logging.basicConfig(filename='mqtt_connection.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to the broker successfully.")
        
    else:
        logging.error(f"Failed to connect. Return code: {rc}")


def init_Mqtt_Client(broker_address, broker_port, client_id):
    client = mqtt.Client(client_id)
    client.on_connect = on_connect  # Set the on_connect callback
    try:
        client.connect(broker_address, broker_port, 60)  # Connect to the broker
    except Exception as e:
        logging.error(f"Error connecting to the broker: {e}")
    return client

def publish_data(client, topic, data):
    json_data = json.dumps(data)
    client.publish(topic, json_data)
    
    
    


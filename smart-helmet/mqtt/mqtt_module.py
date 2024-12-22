import paho.mqtt.client as mqtt
import json
import logging
import time

# Configure logging
logging.basicConfig(filename='mqtt_connection.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to the broker successfully.")
        userdata['connected'] = True
    else:
        logging.error(f"Failed to connect. Return code: {rc}")
        userdata['connected'] = False


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warning("Unexpected disconnection.")
    userdata['connected'] = False


def init_mqtt_client(broker_address, broker_port, client_id):
    client = mqtt.Client(client_id)
    client.user_data_set({'connected': False})
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        logging.info("Attempting to connect to the broker...")
        client.connect(broker_address, broker_port, 60)
    except Exception as e:
        logging.error(f"Error connecting to the broker: {e}")
    
    return client


def publish_data(client, topic, data):
    try:
        json_data = json.dumps(data)
        result = client.publish(topic, json_data)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"Data published to topic '{topic}': {data}")
        else:
            logging.warning(f"Failed to publish data to topic '{topic}': {result.rc}")
    except Exception as e:
        logging.error(f"Error while publishing data: {e}")


def reconnect_if_needed(client):
    if not client._userdata['connected']:
        try:
            logging.info("Reconnecting to the broker...")
            client.reconnect()
        except Exception as e:
            logging.error(f"Error while reconnecting: {e}")

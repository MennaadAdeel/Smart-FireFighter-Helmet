import asyncio
import json
import logging
from gmqtt import Client as MQTTClient

# Configure logging
logging.basicConfig(filename='mqtt_connection.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define on_connect callback
async def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to the broker successfully.")
    else:
        logging.error(f"Failed to connect. Return code: {rc}")

# Initialize MQTT client
async def init_Mqtt_Client(broker_address, broker_port, client_id):
    client = MQTTClient(client_id)
    client.on_connect = on_connect  # Set the on_connect callback
    try:
        await client.connect(broker_address, broker_port)
    except Exception as e:
        logging.error(f"Error connecting to the broker: {e}")
    return client

# Publish data
async def publish_data(client, topic, data):
    json_data = json.dumps(data)
    await client.publish(topic, json_data)

# Main function to run the MQTT client and publish data
async def main():
    broker_address = "your_broker_address"
    broker_port = 1883
    client_id = "your_client_id"
    
    # Initialize MQTT client
    client = await init_Mqtt_Client(broker_address, broker_port, client_id)
    
    # Example data to publish
    data = {"key": "value"}
    
    # Publish the data
    await publish_data(client, "your_topic", data)

    # Run the client loop
    await client.loop_forever()

# Start the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())

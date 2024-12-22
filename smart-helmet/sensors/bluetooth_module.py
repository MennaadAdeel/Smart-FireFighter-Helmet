# Bluetooth Module for Raspberry Pi (Python using Bleak)
# This module provides reusable functions for BLE scanning, connecting, and communication.

import asyncio
from bleak import BleakClient, BleakScanner

# UUIDs (these should match the ESP32 configurations)
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "abcdef01-1234-5678-1234-56789abcdef0"

class BluetoothManager:
    def __init__(self, device_names):
        self.device_names = device_names
        self.devices = {}

    async def scan_devices(self):
        """Scan for BLE devices and store addresses of matching devices."""
        print("Scanning for devices...")
        found_devices = await BleakScanner.discover()

        for device in found_devices:
            if device.name in self.device_names:
                self.devices[device.name] = device.address

        print("Found devices:", self.devices)

    async def communicate_with_device(self, device_name, message):
        """Connect to a device by name and perform read/write operations."""
        if device_name not in self.devices:
            print(f"Device {device_name} not found in scanned devices.")
            return

        address = self.devices[device_name]
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                async with BleakClient(address) as client:
                    print(f"Connected to {device_name} ({address})")

                    # Write data
                    await client.write_gatt_char(CHARACTERISTIC_UUID, message.encode())
                    print(f"[{device_name}] Sent: {message}")

                    # Read response
                    response = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    print(f"[{device_name}] Received: {response.decode()}")

                    return response.decode()

            except Exception as e:
                retries += 1
                print(f"Error communicating with {device_name}: {e}. Retrying ({retries}/{max_retries})...")

        print(f"Failed to communicate with {device_name} after {max_retries} retries.")
        return None

# Usage example
if __name__ == "__main__":
    async def main():
        device_names = ["ESP32_Device_1", "ESP32_Device_2", "ESP32_Device_3", "ESP32_Device_4"]
        bt_manager = BluetoothManager(device_names)

        await bt_manager.scan_devices()

        # Example task: Send a runtime message to each device
        for device_name in device_names:
            response = await bt_manager.communicate_with_device(device_name, "Hello from Raspberry Pi!")
            print(f"Response from {device_name}: {response}")

    asyncio.run(main())

"the esp32 code is in my disktop"

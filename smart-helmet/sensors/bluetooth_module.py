from bleak import BleakScanner, BleakClient

async def connect_to_esp32(address):
    async with BleakClient(address) as client:
        print(f"Connected to {address}")
        services = await client.get_services()
        for service in services:
            print(service)

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
        if "ESP32" in d.name:
            await connect_to_esp32(d.address)

import asyncio
asyncio.run(main())

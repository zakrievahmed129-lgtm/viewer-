import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning for Bluetooth devices (with RSSI)...")
    try:
        devices = await BleakScanner.discover(return_adv=True, timeout=5.0)
        print(f"Found {len(devices)} devices:")
        for addr, (device, adv) in devices.items():
            name = device.name if device.name else "(BLE Beacon)"
            print(f"  Name: {name:30} | Addr: {device.address} | RSSI: {adv.rssi} dBm")
    except Exception as e:
        print(f"Bluetooth scan error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import sys
from typing import List

import bleak


# I didn't write this, but it takes the raw BT data and spits out the data of interest
def temp_hum(values, battery, address):
    # the data has a 1 bit in the first position if it's negative.
    mult = 1
    if values[0] & 0x80 == 128:
        print(f"value: {values}")
        mult = -1
        values = (values[0] & 0x7F).to_bytes(1, "big") + values[1:]
    values = int.from_bytes(values, "big")
    temp = float(values / 10000) * mult
    hum = float((values % 1000) / 10)
    if temp < 0:
        print(f"temperature in C: {temp}")
        print(f"raw data: {values}")

    # this print looks like this:
    # 2021-12-27T11:22:17.040469 BDAddress('A4:C1:38:9F:1B:A9') Temp: 45.91 F  Humidity: 25.8 %  Battery: 100 %
    # LAGER.info(f"decoded values: {address} Temp: {c2f(temp)} F  Humidity: {hum} %  Battery: {battery}")
    # this code originally just printed the data, but we need it to publish to mqtt.
    # added the return values to be used elsewhere
    return temp, hum, battery


async def find_some(timeout: int = 5):

    devices = await bleak.BleakScanner.discover(timeout=10)
    return devices


async def main():

    while True:
        devices = None
        while devices is None or len(devices) <= 0:
            print("polling 10s:")
            devices = await find_some(timeout=10)

        for d in devices:
            print(d)
            if d.name == "GVH5075_5DD0":
                mfg_data = d.metadata["manufacturer_data"]
                print("  Manufacturing data for GVH5075:")
                print(mfg_data)
                if 60552 in mfg_data:
                    temp, hum, battery = temp_hum(mfg_data[60552][3:6], 0, d.address)
                    print(f"temp: {temp}, humidity: {hum}, battery: {battery}")
                else:
                    print("Required data is missing from this advert, skipping.")


asyncio.run(main())

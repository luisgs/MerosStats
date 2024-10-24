import asyncio
import os

import sys, logging, time

from meross_iot.controller.mixins.electricity import ElectricityMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

# http server to provide tempand humid data via http
from prometheus_client import Gauge, start_http_server

# Setup logging to the Systemd Journal
formatter = "%(asctime)s;%(levelname)s;%(message)s"
logging.basicConfig(format=formatter, stream=sys.stdout, level=logging.DEBUG)

try:
    # MEROSS - USER and PASSWORD
    EMAIL = os.environ.get('MEROSS_EMAIL') or "email"
    PASSWORD = os.environ.get('MEROSS_PASSWORD') or "email"
    DEVICE_NAME = os.environ.get('DEVICE_NAME') or "device"
    # DEFAULT VARS
    METRICS_PORT = os.environ.get('METRICS_PORT') or 8040
    READ_INTERVAL = os.environ.get('READ_INTERVAL') or 60

    logging.info("Variables:" + EMAIL + " password:" + PASSWORD)
except RuntimeError as e:
    logging.error("Error while obtaining VARs from OS.ENVIRON or predefined")
    logging.error("RuntimeError: {}".format(e))
    exit


# Promethues metrics set up
# Create Prometheus gauges for POWER, VOLTAGE and CURRENT
gp = Gauge('POWER',
           'POWER consumption measured by the smart plug', ['scale'])
gv = Gauge('VOLTAGE',
            'VOLTAGE consumption measured by the smart plug', ['scale'])
gc = Gauge('CURRENT',
            'CURRENT consumption measured by the smart plug', ['scale'])


async def main():
    try:
        # Setup the HTTP client API from user-password
        http_api_client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-eu.meross.com',
                                                                          email=EMAIL, password=PASSWORD)
    except:
        logging.error("ERROR: MEROSS login, exiting...")
        exit()

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve device that implement the electricity mixin and your name
    await manager.async_device_discovery()

    if DEVICE_NAME:
        logging.info("Device Name: " + str(DEVICE_NAME))
        devs = manager.find_devices(device_name=DEVICE_NAME, device_class=ElectricityMixin)
    else:
        devs = manager.find_devices(device_class=ElectricityMixin)

    if len(devs) < 1:
        logging.info("No electricity-capable device found...")
    else:
        dev = devs[0]

        # Update device status: this is needed only the very first time we play with this device (or if the
        #  connection goes down)
        await dev.async_update()

        # Start HTTP server for exposing data
        start_http_server(int(METRICS_PORT))
        logging.info("Serving POWER, VOLTAGE and CURRENT of your sensor on port: {}".format(METRICS_PORT))

        while True:
            # Read the electricity power/voltage/current
            instant_consumption = await dev.async_get_instant_metrics()
            logging.info(f"Current consumption data: {instant_consumption}")
            # logging.info(f"-> Current POWER: {instant_consumption.power}")
            # logging.info(f"-> Current VOLTAGE: {instant_consumption.voltage}")
            # logging.info(f"-> Current CURRENT: {instant_consumption.current}")

            # Adding values to our prometheus http indicators.
            gp.labels('power').set(instant_consumption.power)
            gv.labels('volts').set(instant_consumption.voltage)
            gc.labels('amperes').set(instant_consumption.current)
            logging.info("Next read will be trigger in " + str(READ_INTERVAL) + "s")
            time.sleep(int(READ_INTERVAL))

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
#    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()

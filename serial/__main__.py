import time
import json
import sys

sys.path.append('/srv/datalogger_reg_fijo/')
from serial_lib import SerialLib
from lib.usb_dev_node import USBDevnode

# Config
f = open('/srv/datalogger_reg_fijo/config_reg_fijo.json')
config:dict = json.load(f)

# Global variables
USB_SERIAL_SENSOR = config["SENSOR"]["PORT"]
CALIBRATION_LEVEL_CURVE = config["SENSOR"]["LEVEL_CURVE"] # Lista con min and max voltage signal: [v_min, v_max]
SERVER_IP = config["SERVER"]["IP"]
SERVER_PORT = config["SERVER"]["PORT"]

if __name__ == "__main__":
    devnode = USBDevnode(USB_SERIAL_SENSOR)
    RX = SerialLib(devnode, level_curve= CALIBRATION_LEVEL_CURVE, log_id="SERIAL")
    RX.set_server(SERVER_IP, SERVER_PORT)
    RX.set_panic_command("systemctl restart mining-serial")
    RX.log("mining serial, initialized")

    counter = 0
    while True:
        # Breathe
        silence_period = time.time() - RX.last_timestamp
        if int(silence_period) > 20:
            RX.panic("Too much RX silence")
        print("last_sensor_timestamp: %s" % str(silence_period))
        time.sleep(1)


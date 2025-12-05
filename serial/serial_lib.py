import threading
import json
from serial import Serial, serialutil
from time import time, sleep
from lib.utils import Utils

class SerialLib(Utils):
    def __init__(self, usbdevnode, level_curve, baudrate: int = 115200, log_id = "SERIAL"):
        self.baudrate = baudrate
        self.timeout = 0.5
        self.log_id = log_id
        self.usbdevnode = usbdevnode
        self.v_min, self.v_max = level_curve
        self.last_timestamp = time()

        threading.Thread(target=self.connect_read).start()
        threading.Thread(target=self.connect_write).start()
    
    def connect_read(self) -> None:
        """
        This function attempts to establish a serial connection with the specified USB device node.

        """

        try:
            self.log(f"Try to connect serial port: {self.usbdevnode.get_devnode()}")
            self.serial_module = Serial(self.usbdevnode.get_devnode(), self.baudrate, timeout=self.timeout)
            self.read()

        except Exception as Ex:
            self.log(Ex)

    def connect_write(self) -> None:
        """
        This function attempts to establish a serial connection with the specified USB device node.

        """

        try:
            self.log(f"Try to connect serial port: {self.usbdevnode.get_devnode()}")
            self.serial_module = Serial(self.usbdevnode.get_devnode(), self.baudrate, timeout=self.timeout)
            self.send_command()

        except Exception as Ex:
            self.log(Ex)

    def read(self) -> None:
        """
        This function continuously reads lines from the serial module and processes them.
        If the line is empty, the function skips it.

        """
        self.log("Reading line from serial")
        while True:
            try:
                raw_line = self.serial_module.readline().decode("utf-8")
                line = raw_line.strip()
                if line =="":
                    pass
                else:
                    self.log(f"GOT: {line}")
                    if "modo" in line:self.process_line(line)
                sleep(0.01)
            except:
                self.log("Error decoding line")

    def process_line(self, line: str) -> None:
        """
        This function processes a line of data received from the serial module.
        It extracts the sensor level and computes the corresponding voltage.

        :param line: The line of data received from the serial module.
        """
        try:
            # 1. Process data 
            data_dict = {}
            data_split = line.split(';')
            for data in data_split:
                if not data: continue
                data = data.upper()
                self.log(f"Data: {data}")
                
        except:
            self.traceback() 

    def write(self, command: str) -> None:
        """
        This function writes a command to the serial module.

        :param command: The command to be written to the serial module.
        """
        try:
            self.serial_module.write(command.encode('utf-8'))
            self.log(f"Written command: {command}")
        except:
            self.log("Error writing command to serial")
        
    def send_command(self) -> None:
        """
        This function sends a command to the serial module.
        """
        while True:
            try:
                command = input("Enter command to send: ")
                self.write(command + "\n")
            except:
                self.log("Error sending command")
import threading
from serial import Serial, SerialException
from time import sleep
from queue import Queue, Empty
from lib.utils import Utils
from time import time, sleep

class SerialLib(Utils):
    def __init__(self, usbdevnode, level_curve, baudrate=115200, log_id="SERIAL"):
        self.usbdevnode = usbdevnode
        self.baudrate = baudrate
        self.timeout = 0.5
        self.log_id = log_id
        self.v_min, self.v_max = level_curve
        self.last_timestamp = time()

        self.serial = None
        self.running = threading.Event()
        self.running.set()

        self.tx_queue = Queue()

        self._connect()

        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.write_thread = threading.Thread(target=self._write_loop, daemon=True)

        self.read_thread.start()
        self.write_thread.start()

    def _connect(self):
        while self.running.is_set():
            try:
                dev = self.usbdevnode.get_devnode()
                self.log(f"Connecting to serial port: {dev}")
                self.serial = Serial(dev, self.baudrate, timeout=self.timeout)
                self.log("Serial connected")
                return
            except SerialException as e:
                self.log(f"Connection error: {e}")
                sleep(2)

    def _read_loop(self):
        while self.running.is_set():
            try:
                line = self.serial.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                
                self.last_timestamp = time() 
                self.log(f"GOT: {line}")

                if "modo" in line.lower():
                    self.process_line(line)

            except SerialException as e:
                self.log(f"Read error: {e}")
                self._reconnect()

    def _write_loop(self):
        while self.running.is_set():
            try:
                command = self.tx_queue.get(timeout=0.5)
                self.serial.write(command.encode("utf-8"))
                self.log(f"SENT: {command}")
            except Empty:
                continue
            except SerialException as e:
                self.log(f"Write error: {e}")
                self._reconnect()

    def send_command(self, command: str):
        self.tx_queue.put(command)

    def process_line(self, line: str):
        try:
            data_split = line.split(";")
            for data in data_split:
                if not data:
                    continue
                self.log(f"Data: {data.upper()}")
        except Exception:
            self.traceback()

    def _reconnect(self):
        try:
            if self.serial:
                self.serial.close()
        except Exception:
            pass

        self._connect()

    def stop(self):
        self.running.clear()
        if self.serial:
            self.serial.close()

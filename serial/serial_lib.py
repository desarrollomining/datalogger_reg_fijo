import threading
from serial import Serial, SerialException
from time import sleep
from queue import Queue, Empty
from lib.utils import Utils
from time import time, sleep
import re

class SerialLib(Utils):
    def __init__(self, usbdevnode, level_curve, baudrate=115200, log_id="SERIAL"):
        self.usbdevnode = usbdevnode
        self.baudrate = baudrate
        self.timeout = 0.5
        self.log_id = log_id
        self.v_min, self.v_max = level_curve
        self.last_timestamp = time()
        self.rx_buffer = ""
        self.pending_off = False
        self.ignore_until = 0

        self.serial = None
        self.running = threading.Event()
        self.running.set()

        self.tx_queue = Queue()

        self._connect()

        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
        self.auto_arm_thread = threading.Thread(target=self._auto_arm_loop, daemon=True)

        self.read_thread.start()
        self.write_thread.start()
        self.auto_arm_thread.start()

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
                data = self.serial.read(256).decode("utf-8", errors="ignore")
                if not data:
                    continue

                if hasattr(self, "ignore_until") and time() < self.ignore_until:
                    continue

                self.rx_buffer += data

                while True:
                    start = self.rx_buffer.find("*")
                    if start == -1:
                        self.rx_buffer = ""
                        break

                    end = self.rx_buffer.find("*", start + 1)
                    if end == -1:
                        self.rx_buffer = self.rx_buffer[start:]
                        break

                    raw_msg = self.rx_buffer[start:end + 1]
                    self.rx_buffer = self.rx_buffer[end + 1:]

                    self.last_timestamp = time()
                    self.log(f"GOT: {raw_msg}")
                    self.process_line(raw_msg)
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
            if line.count("*") < 2:
                return
            pattern = re.compile(r"\*((?:SEN|CON)-\d+):.*:(\d:\d)\*")
            match = pattern.search(line)
            if not match:
                return
            sensor_name = match.group(1)
            state = match.group(2)
            self.log(f"Sensor: {sensor_name}, Estado: {state}")
            p, r = map(int, state.split(":"))
            if sensor_name not in ("SEN-01", "SEN-02", "CON-01"):
                return
            if (p == 1 or r == 1) and not self.pending_off:
                self.pending_off = True
            if self.pending_off and p == 0 and r == 0:
                msg = "000000000000"
                self.send_command(msg)
                self.pending_off = False
        except Exception:
            self.traceback()

    def _auto_arm_loop(self):
        while self.running.is_set():
            self.send_command("010000000000")
            sleep(15)


    def _reconnect(self):
        try:
            if self.serial:
                self.serial.close()
        except Exception:
            pass

        self.rx_buffer = ""
        self.pending_off = False
        self.ignore_until = time() + 0.3

        self._connect()

    def stop(self):
        self.running.clear()
        if self.serial:
            self.serial.close()

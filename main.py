"""
NFC Tag Programming Utility
Tool for writing user IDs to NFC tags
"""
import logging
import threading
import time
from core.event_bus import EventBus
from core.task import TaskManager
from manager.button_manager import ButtonManager
from manager.display_manager import DisplayManager
from manager.nfc_manager import NFCManager
import RPi.GPIO as GPIO
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# Инициализация
# -------------------------
reader = NFCManager(uart_port="/dev/serial0", baudrate=115200, hmac_secret=config.HMAC_SECRET)
reader.initialize()
bus = EventBus()
tasks = TaskManager()
buttons = ButtonManager(config.BUTTON_PINS, bus)

def rfid_loop(stop_event, queue):
    print("📡 RFID reading loop started")
    reader.start_reading()

    while stop_event.is_set():
        uid = reader.read_tag()
        if uid:
            print("✅ Valid tag:", uid)
            queue.put(("rfid.uid", uid))

        time.sleep(0.3)

    reader.stop_reading()
    print("🛑 RFID reading loop stopped")

def rfid_write_loop(stop_event):
    print("📡 RFID writing loop started")
    reader.start_writing()

    while stop_event.is_set():
        result = reader.write_tag("966243980")
        if result:
            print("✅ Tag was writed")
        time.sleep(0.3)

    reader.stop_writing()
    print("🛑 RFID writing loop stopped")

ui = DisplayManager(bus, tasks)
tasks.register("rfid", lambda e: rfid_loop(e, ui.queue))
tasks.register("rfid_write", rfid_write_loop)

# bus.subscribe("btn.SET", lambda: tasks.toggle("rfid"))
# bus.subscribe("btn.RST", lambda: tasks.toggle("rfid_write"))

buttons.start()

try:
    while True:
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Exiting...")
    buttons.stop()
    GPIO.cleanup()
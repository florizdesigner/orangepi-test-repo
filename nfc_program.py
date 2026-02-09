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
from manager.display_menu_manager import DisplayMenu
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

class ToggleTask:
    def __init__(self, target):
        self.target = target
        self.event = threading.Event()
        self.thread = None
        self.lock = threading.Lock()

    def toggle(self):
        with self.lock:
            if self.thread and self.thread.is_alive():
                print("🛑 Остановка задачи")
                self.event.clear()
                return

            print("▶️ Запуск задачи")
            self.event.set()
            self.thread = threading.Thread(
                target=self._runner,
                daemon=True
            )
            self.thread.start()

    def _runner(self):
        self.target(self.event)


def rfid_loop(stop_event):
    print("📡 RFID reading loop started")
    reader.start_reading()

    while stop_event.is_set():
        uid = reader.read_tag()
        if uid:
            print("✅ Valid tag:", uid)
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

# tasks.register("rfid", rfid_loop)
# tasks.register("rfid_write", rfid_write_loop)

# bus.subscribe("btn.SET", lambda: tasks.toggle("rfid"))
# bus.subscribe("btn.RST", lambda: tasks.toggle("rfid_write"))
menu = DisplayMenu(bus, tasks)
buttons.start()

try:
    while True:
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Exiting...")
    buttons.stop()
    GPIO.cleanup()
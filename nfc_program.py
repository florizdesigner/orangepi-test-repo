"""
NFC Tag Programming Utility
Tool for writing user IDs to NFC tags
"""
import logging
import threading
import time
from joystick_test import BUTTON_PINS, ButtonManager
from nfc_manager import NFCManager
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

manager = ButtonManager(BUTTON_PINS)

reader_event = threading.Event()

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
    print("📡 RFID loop started")

    while stop_event.is_set():
        reader.start_reading()

        uid = reader.read_tag()
        if uid:
            print("✅ Valid tag:", uid)
        else:
            print("❌ Invalid or no tag")
        time.sleep(0.3)

    print("🛑 RFID loop stopped")

rfid_task = ToggleTask(rfid_loop)

manager.subscribe("SET", rfid_task.toggle)

# Подписываемся на события
# manager.subscribe("UP", lambda: print("⬆️  ВВЕРХ"))
# manager.subscribe("DOWN", lambda: print("⬇️  ВНИЗ"))
# manager.subscribe("LEFT", lambda: print("⬅️  ВЛЕВО"))
# manager.subscribe("RIGHT", lambda: print("➡️  ВПРАВО"))
# manager.subscribe("MID", lambda: print("🔘 КНОПКА НАЖАТА"))
# manager.subscribe("RST", lambda: print("🔄 RST НАЖАТА"))
# manager.subscribe("SET", lambda: print("⚙️  SET НАЖАТА"))

print("Менеджер кнопок запущен. Нажмите Ctrl+C для выхода.")
print("-" * 40)
manager.start()

try:
    while True:
        time.sleep(1)  # основной поток ничего не делает
except KeyboardInterrupt:
    print("\nВыход...")
finally:
    manager.stop()
    reader.cleanup()
    GPIO.cleanup()

# -------------------------
# Запись на метку
# -------------------------
# reader.start_writing()
# success = reader.write_tag("USER_1001")
# if success:
#     print("✅ Tag written successfully")
# else:
#     print("❌ Failed to write tag")
# reader.stop_writing()

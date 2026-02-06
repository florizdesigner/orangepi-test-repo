import RPi.GPIO as GPIO
import time
from threading import Thread

UP = 21
DOWN = 20
LEFT = 26
RIGHT = 16
MID = 19
RST = 13
SET = 6
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BUTTON_PINS = {
    "UP": UP,
    "DOWN": DOWN,
    "LEFT": LEFT,
    "RIGHT": RIGHT,
    "MID": MID,
    "RST": RST,
    "SET": SET
}

class ButtonManager:
    def __init__(self, pins, event_bus, debounce=0.15):
        self.pins = pins
        self.bus = event_bus
        self.debounce = debounce
        self.running = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        self.running = True
        Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self):
        last = {k: GPIO.input(p) for k, p in self.pins.items()}

        while self.running:
            for name, pin in self.pins.items():
                cur = GPIO.input(pin)
                if cur == GPIO.LOW and last[name] == GPIO.HIGH:
                    self.bus.emit(f"btn.{name}")
                    time.sleep(self.debounce)
                last[name] = cur
            time.sleep(0.01)
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from threading import Thread

# --------------------------
# Пины джойстика
# --------------------------
UP = 40
DOWN = 38
LEFT = 37
RIGHT = 36
MID = 35
RST = 33
SET = 31

# --------------------------
# Настройка GPIO
# --------------------------
GPIO.setmode(GPIO.BOARD)
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

for pin in BUTTON_PINS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --------------------------
# Менеджер кнопок (Observer)
# --------------------------
class ButtonManager:
    def __init__(self, pins):
        self.pins = pins
        self.subscribers = {name: [] for name in pins.keys()}
        self._running = False

    def subscribe(self, button_name, callback):
        """Подписаться на событие нажатия кнопки"""
        if button_name in self.subscribers:
            self.subscribers[button_name].append(callback)
        else:
            raise ValueError(f"Неизвестная кнопка: {button_name}")

    def notify(self, button_name):
        """Уведомить всех подписчиков"""
        for callback in self.subscribers.get(button_name, []):
            callback()

    def _poll_buttons(self):
        """Постоянно проверяем кнопки"""
        last_state = {name: GPIO.input(pin) for name, pin in self.pins.items()}
        while self._running:
            for name, pin in self.pins.items():
                state = GPIO.input(pin)
                if state == GPIO.LOW and last_state[name] == GPIO.HIGH:
                    self.notify(name)
                last_state[name] = state
            time.sleep(0.05)

    def start(self):
        """Запуск в отдельном потоке"""
        self._running = True
        self.thread = Thread(target=self._poll_buttons, daemon=True)
        self.thread.start()

    def stop(self):
        self._running = False
        self.thread.join()


# --------------------------
# Пример использования
# --------------------------
def main():
    manager = ButtonManager(BUTTON_PINS)

    # Подписываемся на события
    manager.subscribe("UP", lambda: print("⬆️  ВВЕРХ"))
    manager.subscribe("DOWN", lambda: print("⬇️  ВНИЗ"))
    manager.subscribe("LEFT", lambda: print("⬅️  ВЛЕВО"))
    manager.subscribe("RIGHT", lambda: print("➡️  ВПРАВО"))
    manager.subscribe("MID", lambda: print("🔘 КНОПКА НАЖАТА"))
    manager.subscribe("RST", lambda: print("🔄 RST НАЖАТА"))
    manager.subscribe("SET", lambda: print("⚙️  SET НАЖАТА"))

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
        GPIO.cleanup()


if __name__ == "__main__":
    main()

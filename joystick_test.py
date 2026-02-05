#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from threading import Event, Lock, Thread

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
        self.toggle_threads = {}  # Активные toggle-потоки
        self.toggle_events = {}   # События для управления toggle
        self.lock = Lock()        # Для безопасного доступа к словарям
        self._running = False

    def subscribe(self, button_name, callback, toggle=False):
        """Подписка на кнопку. toggle=True если callback может работать циклом"""
        if button_name not in self.subscribers:
            raise ValueError(f"Неизвестная кнопка: {button_name}")

        self.subscribers[button_name].append((callback, toggle))

    def notify(self, button_name):
        """Вызываем всех подписчиков"""
        for callback, toggle in self.subscribers.get(button_name, []):
            if toggle:
                self._handle_toggle(button_name, callback)
            else:
                Thread(target=callback).start()  # обычный callback в отдельном потоке

    def _handle_toggle(self, button_name, callback):
        """Запуск или остановка toggle-цикла"""
        with self.lock:
            # Если цикл уже работает — останавливаем
            if button_name in self.toggle_threads and self.toggle_threads[button_name].is_alive():
                print(f"Останавливаем цикл для {button_name}")
                self.toggle_events[button_name].clear()  # сигнал остановки
                return

            # Запуск нового цикла
            print(f"Запускаем цикл для {button_name}")
            stop_event = Event()
            stop_event.set()
            self.toggle_events[button_name] = stop_event

            def loop():
                while stop_event.is_set():
                    callback()
                    time.sleep(0.5)  # задержка между итерациями цикла

            t = Thread(target=loop, daemon=True)
            self.toggle_threads[button_name] = t
            t.start()

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
        self._running = True
        self.thread = Thread(target=self._poll_buttons, daemon=True)
        self.thread.start()

    def stop(self):
        self._running = False
        self.thread.join()
        # Остановим все toggle-потоки
        with self.lock:
            for event in self.toggle_events.values():
                event.clear()
            for thread in self.toggle_threads.values():
                thread.join()



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

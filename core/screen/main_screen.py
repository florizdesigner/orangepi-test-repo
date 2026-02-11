import subprocess
import time
from datetime import datetime

from core.screen.base_screen import BaseScreen

class MainScreen(BaseScreen):

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.items = [
            ("Scan", "scan"),
            ("Wifi", "wifi"),
            ("Write", "write"),
        ]
        self.selected = 0
        # Информация о системе / статусе
        self.wifi_status = "WiFi: ---"
        self.cpu_temp = "--°C"
        self.time_str = "--:--"
        self._sysinfo_last_update = 0.0
        # Подписку на кнопки переносим в on_enter/on_exit,
        # чтобы можно было безопасно отписываться

    def on_enter(self):
        self.ui.bus.subscribe("btn.UP", self.before)
        self.ui.bus.subscribe("btn.DOWN", self.next)
        self.ui.bus.subscribe("btn.MID", self.select)

    def on_exit(self):
        self.ui.bus.unsubscribe("btn.UP", self.before)
        self.ui.bus.unsubscribe("btn.DOWN", self.next)
        self.ui.bus.unsubscribe("btn.MID", self.select)

    def next(self):
        self.selected = (self.selected + 1) % len(self.items)

    def before(self):
        self.selected = (self.selected - 1) % len(self.items)

    def select(self):
        screen_name = self.items[self.selected][1]
        self.manager.set(screen_name)

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 0))

        # Обновляем системную информацию не чаще раза в секунду
        now_ts = time.time()
        if now_ts - self._sysinfo_last_update > 1.0:
            self._update_sysinfo()
            self._sysinfo_last_update = now_ts

        # ---------- Заголовок ----------
        title = "Velow /cc"
        d.text((20, 15), title, font=self.ui.font_big, fill=(0, 255, 180))

        # Подзаголовок / слоган
        d.text(
            (20, 50),
            "Регистрация участников",
            font=self.ui.font_small,
            fill=(150, 150, 150),
        )

        # ---------- Меню ----------
        y = 90
        for i, (name, _) in enumerate(self.items):
            is_selected = i == self.selected

            # Фон для выбранного пункта
            if is_selected:
                d.rectangle(
                    (15, y - 5, self.ui.W - 15, y + 40),
                    fill=(10, 40, 60),
                    outline=(0, 255, 180),
                )

            prefix = ">" if is_selected else " "
            color = (255, 255, 255) if is_selected else (180, 180, 180)
            d.text((30, y), f"{prefix} {name}", font=self.ui.font_big, fill=color)
            y += 50

        # ---------- Нижняя панель статуса ----------
        footer_y = self.ui.H - 40

        # Время
        d.text(
            (20, footer_y),
            self.time_str,
            font=self.ui.font_mid,
            fill=(255, 255, 255),
        )

        # Статус Wi‑Fi
        d.text(
            (120, footer_y),
            self.wifi_status,
            font=self.ui.font_small,
            fill=(0, 200, 255),
        )

        # Температура CPU
        d.text(
            (20, footer_y + 20),
            f"CPU: {self.cpu_temp}",
            font=self.ui.font_small,
            fill=(255, 180, 0),
        )

        self.ui.disp.display(self.ui.image)

    # ---------- Системная информация ----------

    def _update_sysinfo(self):
        # Время
        self.time_str = datetime.now().strftime("%H:%M")

        # Температура CPU (типичный путь для Raspberry Pi / OrangePi;
        # если недоступно, оставляем прошлое значение)
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                raw = f.read().strip()
            millis = int(raw)
            self.cpu_temp = f"{millis / 1000.0:.1f}°C"
        except Exception:
            # Не трогаем self.cpu_temp, если не получилось прочитать
            pass

        # Статус Wi‑Fi (через nmcli, если доступен)
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"],
                text=True,
            )
            current_ssid = None
            for line in out.splitlines():
                parts = line.split(":")
                if len(parts) >= 2 and parts[0] == "yes":
                    current_ssid = parts[1].strip()
                    break

            if current_ssid:
                self.wifi_status = f"WiFi: {current_ssid}"
            else:
                self.wifi_status = "WiFi: нет подключения"
        except Exception:
            self.wifi_status = "WiFi: недоступно"

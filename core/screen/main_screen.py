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
            ("Info", "info"),
            ("Write", "write"),
            ("MenuItem1", "write"),
            ("MenuItem2", "write"),
            ("MenuItem3", "write"),
        ]
        self.selected = 0
        # Информация о статусе (Wi‑Fi + время)
        self.wifi_status = "WiFi: ---"
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
        d.text((16, 10), title, font=self.ui.font_big, fill=(0, 255, 180))

        # Подзаголовок / слоган
        d.text(
            (16, 40),
            "Регистрация участников",
            font=self.ui.font_small,
            fill=(150, 150, 150),
        )

        # ---------- Меню (адаптация под 240x240) ----------
        max_items = 4  # одновременно показываем не больше трёх пунктов
        total = len(self.items)
        start = 0
        if total > max_items:
            # Пытаемся держать выбранный пункт по центру "окна"
            start = max(0, self.selected - max_items // 2)
            start = min(start, total - max_items)
        end = min(total, start + max_items)

        y = 70
        step = 35  # вертикальный шаг между пунктами

        for idx in range(start, end):
            name, _ = self.items[idx]
            is_selected = idx == self.selected

            if is_selected:
                d.rectangle(
                    (10, y - 4, self.ui.W - 10, y + 28),
                    fill=(10, 40, 60),
                    outline=(0, 255, 180),
                )

            prefix = ">" if is_selected else " "
            color = (255, 255, 255) if is_selected else (180, 180, 180)
            d.text((22, y), f"{prefix} {name}", font=self.ui.font_big, fill=color)
            y += step

        # ---------- Нижняя панель статуса ----------
        footer_y = self.ui.H - 20

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
            font=self.ui.font_mid,
            fill=(0, 200, 255),
        )

        self.ui.disp.display(self.ui.image)

    # ---------- Системная информация для главного экрана ----------

    def _update_sysinfo(self):
        # Время
        self.time_str = datetime.now().strftime("%H:%M")

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

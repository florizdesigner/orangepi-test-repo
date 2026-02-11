import os
import subprocess
import time
from datetime import datetime

from core.screen.base_screen import BaseScreen


class InfoScreen(BaseScreen):
    """
    Экран с системной информацией:
    - время и аптайм
    - температура CPU
    - загрузка (load average)
    - объём свободной памяти (упрощённо)
    """

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.time_str = "--:--"
        self.uptime_str = "--"
        self.cpu_temp = "--°C"
        self.load_avg = "--"
        self.mem_free = "--"
        self._last_update = 0.0

    # ---------- Жизненный цикл ----------

    def on_enter(self):
        self.ui.bus.subscribe("btn.RST", self._back)
        self._update_info(force=True)

    def on_exit(self):
        self.ui.bus.unsubscribe("btn.RST", self._back)

    def _back(self):
        self.manager.set("main")

    # ---------- Обновление информации ----------

    def _update_info(self, force: bool = False):
        now_ts = time.time()
        if not force and now_ts - self._last_update < 1.0:
            return
        self._last_update = now_ts

        # Время
        self.time_str = datetime.now().strftime("%H:%M:%S")

        # Аптайм
        try:
            with open("/proc/uptime", "r") as f:
                seconds = float(f.read().split()[0])
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            self.uptime_str = f"{hrs}ч {mins}м"
        except Exception:
            pass

        # Температура CPU
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                raw = f.read().strip()
            millis = int(raw)
            self.cpu_temp = f"{millis / 1000.0:.1f}°C"
        except Exception:
            pass

        # Load average
        try:
            load1, load5, load15 = os.getloadavg()
            self.load_avg = f"{load1:.2f} {load5:.2f} {load15:.2f}"
        except Exception:
            pass

        # Память (свободная) — берём MemAvailable из /proc/meminfo
        try:
            mem_available_kb = None
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            mem_available_kb = int(parts[1])
                        break
            if mem_available_kb is not None:
                self.mem_free = f"{mem_available_kb / 1024:.0f} МБ"
        except Exception:
            pass

    # ---------- Рендер ----------

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 0))

        # Обновляем данные
        self._update_info()

        # Заголовок
        d.text(
            (20, 15),
            "System Info",
            font=self.ui.font_big,
            fill=(0, 255, 180),
        )

        y = 70
        line_h = 25

        d.text(
            (20, y),
            f"Time: {self.time_str}",
            font=self.ui.font_mid,
            fill=(255, 255, 255),
        )
        y += line_h

        d.text(
            (20, y),
            f"Uptime: {self.uptime_str}",
            font=self.ui.font_mid,
            fill=(200, 200, 200),
        )
        y += line_h

        d.text(
            (20, y),
            f"CPU: {self.cpu_temp}",
            font=self.ui.font_mid,
            fill=(255, 180, 0),
        )
        y += line_h

        d.text(
            (20, y),
            f"Load: {self.load_avg}",
            font=self.ui.font_mid,
            fill=(0, 200, 255),
        )
        y += line_h

        d.text(
            (20, y),
            f"RAM free: {self.mem_free}",
            font=self.ui.font_mid,
            fill=(180, 255, 180),
        )
        y += line_h

        # Подсказка выхода
        d.text(
            (20, self.ui.H - 30),
            "RST = Назад",
            font=self.ui.font_small,
            fill=(150, 150, 150),
        )

        self.ui.disp.display(self.ui.image)


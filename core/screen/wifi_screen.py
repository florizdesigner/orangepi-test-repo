import subprocess
from typing import List, Dict

from core.screen.base_screen import BaseScreen


class WifiScreen(BaseScreen):
    """
    Экран управления Wi‑Fi:
    - при входе сканирует доступные сети
    - позволяет выбрать сеть джойстиком и попытаться подключиться к ней через nmcli
    """

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.networks: List[Dict] = []
        self.selected = 0
        self.status: str | None = None

    # ---------- Жизненный цикл ----------

    def on_enter(self):
        # Подписываемся на кнопки
        self.ui.bus.subscribe("btn.UP", self._up)
        self.ui.bus.subscribe("btn.DOWN", self._down)
        self.ui.bus.subscribe("btn.MID", self._connect_selected)
        self.ui.bus.subscribe("btn.RST", self._back)

        self.status = "Сканирование сетей..."
        self._scan_networks()

    def on_exit(self):
        # Отписываемся от кнопок
        self.ui.bus.unsubscribe("btn.UP", self._up)
        self.ui.bus.unsubscribe("btn.DOWN", self._down)
        self.ui.bus.unsubscribe("btn.MID", self._connect_selected)
        self.ui.bus.unsubscribe("btn.RST", self._back)

    # ---------- Обработка кнопок ----------

    def _up(self):
        if not self.networks:
            return
        self.selected = (self.selected - 1) % len(self.networks)

    def _down(self):
        if not self.networks:
            return
        self.selected = (self.selected + 1) % len(self.networks)

    def _connect_selected(self):
        if not self.networks:
            return
        ssid = self.networks[self.selected]["ssid"]
        if not ssid:
            self.status = "Невозможно подключиться: пустой SSID"
            return

        # Пытаемся подключиться через NetworkManager / nmcli.
        # Для открытых или уже сконфигурированных сетей этого достаточно.
        try:
            self.status = f"Подключение к {ssid}..."
            subprocess.check_call(["nmcli", "dev", "wifi", "connect", ssid])
            self.status = f"Подключено к {ssid}"
        except Exception as e:
            # Детали ошибки в логах, пользователю краткое сообщение.
            self.status = f"Ошибка подключения к \n{ssid}"

    def _back(self):
        self.manager.set("main")

    # ---------- Работа с Wi‑Fi ----------

    def _scan_networks(self):
        """
        Сканирует доступные Wi‑Fi сети через nmcli.
        Ожидает наличие NetworkManager и утилиты nmcli в системе.
        """
        try:
            # Формат: ssid:signal:security
            output = subprocess.check_output(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"],
                text=True,
            )
        except Exception:
            self.networks = []
            self.status = "Ошибка: nmcli недоступен"
            return

        nets: List[Dict] = []
        seen = set()
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split(":")
            # nmcli может вернуть меньше полей, подстрахуемся
            ssid = parts[0].strip() if len(parts) > 0 else ""
            signal = parts[1].strip() if len(parts) > 1 else ""
            security = parts[2].strip() if len(parts) > 2 else ""

            # Пропускаем совсем пустые строки / дубликаты SSID
            key = (ssid, security)
            if not ssid or key in seen:
                continue
            seen.add(key)

            nets.append(
                {
                    "ssid": ssid,
                    "signal": signal,
                    "security": security,
                }
            )

        self.networks = nets
        self.selected = 0 if self.networks else 0
        if not self.networks:
            self.status = "Сети не найдены"
        else:
            self.status = "Выберите сеть и нажмите MID"

    # ---------- Рендер ----------

    def _draw_content(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 0))

        # Заголовок
        d.text((20, 20), "WiFi", font=self.ui.font_big, fill=(0, 255, 255))

        y = 70
        max_items = 3  # сколько сетей показывать одновременно

        if self.networks:
            start = max(0, self.selected - max_items // 2)
            end = min(len(self.networks), start + max_items)

            for idx in range(start, end):
                net = self.networks[idx]
                prefix = ">" if idx == self.selected else " "

                # Отрисовываем SSID
                text = f"{prefix} {net['ssid']}"
                d.text((20, y), text, font=self.ui.font_mid, fill=(255, 255, 255))

                # Отрисовываем уровень сигнала и "замок" при наличии защиты
                info_x = 20
                info_y = y + 24
                if net["signal"]:
                    d.text(
                        (info_x, info_y),
                        f"Signal: {net['signal']}",
                        font=self.ui.font_small,
                        fill=(150, 150, 150),
                    )
                    info_x += 120
                if net["security"] and net["security"] != "--":
                    d.text(
                        (info_x, info_y),
                        "LOCK",
                        font=self.ui.font_small,
                        fill=(255, 100, 100),
                    )

                y += 50
        else:
            d.text(
                (20, y),
                self.status or "Нет доступных сетей",
                font=self.ui.font_mid,
                fill=(200, 200, 200),
            )

        # Статус / подсказка
        status_text = self.status or ""
        if status_text:
            d.text(
                (20, self.ui.H - 30),
                status_text,
                font=self.ui.font_small,
                fill=(150, 150, 150),
            )


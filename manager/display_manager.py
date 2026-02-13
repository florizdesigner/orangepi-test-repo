import ST7789 as ST7789
from PIL import Image, ImageDraw, ImageFont
from queue import Queue
import threading
import time

from core.screen.main_screen import MainScreen
from core.screen.scan_screen import ScanScreen
from core.screen.wifi_screen import WifiScreen
from core.screen.info_screen import InfoScreen
from manager.screen_manager import ScreenManager

class DisplayManager:
    def __init__(self, bus, tasks, api_client=None):
        self.bus = bus
        self.tasks = tasks
        self.api_client = api_client

        # ------------------ INIT дисплея ------------------
        self.disp = ST7789.ST7789(
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT,
            dc=24,
            rst=25,
            backlight=27,
            mode=3,
            spi_speed_hz=80 * 1000 * 1000
        )
        self.disp.begin()  # обязательно

        # Буфер и рисование
        self.W = self.disp.width
        self.H = self.disp.height
        self.image = Image.new("RGB", (self.W, self.H))
        self.draw = ImageDraw.Draw(self.image)

        # Шрифты
        self.font_big = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        self.font_mid = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        self.font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

        # ------------------ Queue для событий ------------------
        self.queue = Queue()

        # ------------------ ScreenManager ------------------
        self.manager = ScreenManager(self)

        # Регистрируем экраны
        self.manager.register("main", MainScreen)
        self.manager.register("scan", ScanScreen)
        self.manager.register("wifi", WifiScreen)
        self.manager.register("info", InfoScreen)
        # self.manager.register("write", WriteScreen)

        # Стартовый экран
        self.manager.set("main")

        # ------------------ UI loop ------------------
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            # Обработка очереди событий
            while not self.queue.empty():
                evt, data = self.queue.get()
                self.manager.event(evt, data)

            # Рисуем текущий экран
            self.manager.draw()
            time.sleep(0.05)

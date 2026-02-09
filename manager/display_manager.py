import threading
import time
from core.screen.main_screen import MainScreen
from manager.screen_manager import ScreenManager
import ST7789 as ST7789
from PIL import Image, ImageDraw, ImageFont


class DisplayManager:
    def __init__(self, bus, tasks):

        self.bus = bus
        self.tasks = tasks

        self.disp = ST7789.ST7789(
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT,
            dc=24,
            rst=25,
            backlight=27,
            mode=3,
            spi_speed_hz=80 * 1000 * 1000
        )
        self.disp.begin()

        self.W = self.disp.width
        self.H = self.disp.height

        self.image = Image.new("RGB", (self.W, self.H))
        self.draw = ImageDraw.Draw(self.image)

        self.font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        self.font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)


        self.manager = ScreenManager()
        self.manager.set(MainScreen(self, self.manager))

        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            self.manager.draw()
            time.sleep(0.2)

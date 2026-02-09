import ST7789 as ST7789
from PIL import Image, ImageDraw, ImageFont
import threading

class DisplayMenu:
    def __init__(self, bus, tasks):
        self.bus = bus
        self.tasks = tasks

        self.W = 240
        self.H = 240

        self.disp = ST7789.ST7789(
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT,
            dc=24,
            rst=25,
            backlight=27,
            mode=3,
            spi_speed_hz=80 * 1000 * 1000
        )

        self.image = Image.new("RGB", (self.W, self.H))
        self.draw = ImageDraw.Draw(self.image)

        self.font = ImageFont.load_default()

        self.items = [
            ("RFID scan", "rfid"),
            ("RFID write", "rfid_write"),
        ]

        self.selected = 0
        self.lock = threading.Lock()

        self.bus.subscribe("btn.DOWN", self.next)
        self.bus.subscribe("btn.MID", self.select)
        self.disp.begin()
        self.redraw()

    def next(self):
        with self.lock:
            self.selected = (self.selected + 1) % len(self.items)
        self.redraw()

    def select(self):
        name = self.items[self.selected][1]
        self.tasks.toggle(name)
        self.redraw()

    def redraw(self):
        self.draw.rectangle((0, 0, self.W, self.H), fill=(0, 0, 0))

        y = 40
        for i, (label, task) in enumerate(self.items):
            active = (self.tasks.active == task)

            prefix = "▶ " if i == self.selected else "  "
            status = "🟢" if active else "🔴"

            text = f"{prefix}{label} {status}"

            color = (0, 255, 0) if active else (180, 180, 180)
            if i == self.selected:
                color = (255, 255, 255)

            self.draw.text((20, y), text, font=self.font, fill=color)
            y += 40

        self.disp.display(self.image)

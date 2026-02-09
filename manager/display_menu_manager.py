import ST7789 as ST7789
from PIL import Image, ImageDraw, ImageFont
import threading
import time
import os
import psutil
import socket

class DisplayMenu:
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

        self.items = [
            ("Scan", "rfid"),
            ("Write", "rfid_write"),
        ]

        self.selected = 0
        self.lock = threading.Lock()

        self.ip = self.get_ip()

        self.bus.subscribe("btn.DOWN", self.next)
        self.bus.subscribe("btn.MID", self.select)

        self.running = True
        threading.Thread(target=self.auto_refresh, daemon=True).start()

        self.redraw()

    # ---------------- SYSTEM ----------------

    def get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "0.0.0.0"

    def uptime(self):
        t = int(time.time() - psutil.boot_time())
        h = t // 3600
        m = (t % 3600) // 60
        s = t % 60
        return f"{h:02}:{m:02}:{s:02}"

    # ---------------- UI ----------------

    def next(self):
        with self.lock:
            self.selected = (self.selected + 1) % len(self.items)
        self.redraw()

    def select(self):
        task = self.items[self.selected][1]
        self.tasks.toggle(task)
        self.redraw()

    def auto_refresh(self):
        while self.running:
            self.redraw()
            time.sleep(0.5)

    def redraw(self):
        self.draw.rectangle((0, 0, self.W, self.H), fill=(0, 0, 0))

        # Header
        self.draw.text((10, 6), "RFID TOOL v1.0", font=self.font_mid, fill=(0, 200, 255))
        self.draw.text((10, 28), f"IP: {self.ip}", font=self.font_small, fill=(180, 180, 180))

        self.draw.line((0, 52, self.W, 52), fill=(60, 60, 60))

        # Menu
        y = 70
        for i, (label, task) in enumerate(self.items):
            active = (self.tasks.active == task)

            prefix = ">" if i == self.selected else " "
            state = "ON" if active else "OFF"

            color = (0, 255, 0) if active else (200, 200, 200)
            if i == self.selected:
                color = (255, 255, 255)

            self.draw.text((15, y), f"{prefix} {label}", font=self.font_big, fill=color)
            self.draw.text((150, y + 4), f"[ {state} ]", font=self.font_mid,
                           fill=(0, 255, 0) if active else (255, 80, 80))

            y += 50

        self.draw.line((0, 180, self.W, 180), fill=(60, 60, 60))

        # Status bar
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        self.draw.text((10, 190), f"CPU: {cpu:>3.0f}%  MEM: {mem:>3.0f}%",
                        font=self.font_small, fill=(160, 160, 160))

        self.draw.text((10, 210), f"UPTIME: {self.uptime()}",
                        font=self.font_small, fill=(160, 160, 160))

        self.disp.display(self.image)

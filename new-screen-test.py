import board
import busio
import digitalio
from adafruit_rgb_display import st7789
from PIL import Image, ImageDraw

# Настройка пинов
dc = digitalio.DigitalInOut(board.D24)
rst = digitalio.DigitalInOut(board.D25)

# SPI
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)

# Инициализация без CS
display = st7789.ST7789(
    spi,
    height=240,
    width=240,
    y_offset=0,
    x_offset=0,
    dc=dc,
    rst=rst,
    cs=None,  # Без CS
    baudrate=40000000,
    rotation=0
)

# Тест
image = Image.new("RGB", (240, 240), (255, 0, 0))  # Красный
draw = ImageDraw.Draw(image)
draw.rectangle((50, 50, 190, 190), fill=(0, 255, 0))  # Зелёный квадрат
draw.text((80, 110), "Works!", fill=(255, 255, 255))

display.image(image)
print("Готово!")
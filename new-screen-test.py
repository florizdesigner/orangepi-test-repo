import board
import digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

# Пины
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Инициализация БЕЗ cs (передаём None или не указываем)
display = st7789.ST7789(
    board.SPI(),
    dc=dc_pin,
    rst=reset_pin,
    cs=None,  # Нет CS пина
    width=240,
    height=240,
    baudrate=40000000,  # Можно попробовать выше
    rotation=0
)

# Тест
image = Image.new("RGB", (240, 240), (0, 100, 200))
draw = ImageDraw.Draw(image)
draw.ellipse((70, 70, 170, 170), fill=(255, 255, 0), outline=(255, 0, 0))
draw.text((90, 110), "Hello!", fill=(0, 0, 0))

display.image(image)
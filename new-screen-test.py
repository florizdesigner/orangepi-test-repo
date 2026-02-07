import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# Настройка пинов
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Инициализация дисплея ST7789
display = st7789.ST7789(
    board.SPI(),
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    width=240,
    height=240,
    baudrate=24000000,
    x_offset=0,  # Если изображение смещено, подберите offset
    y_offset=0
)

# Создание изображения
image = Image.new("RGB", (240, 240))
draw = ImageDraw.Draw(image)

# Рисуем градиент и текст
for y in range(240):
    color = int(255 * y / 240)
    draw.line([(0, y), (240, y)], fill=(color, 0, 255 - color))

draw.text((60, 110), "Raspberry Pi", fill=(255, 255, 255))

# Выводим на экран
display.image(image)
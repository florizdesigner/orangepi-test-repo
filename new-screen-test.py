import ST7789
from PIL import Image, ImageDraw, ImageFont

disp = ST7789.ST7789(
    port=0,
    cs=1,
    dc=24,
    rst=25,
    backlight=None,
    width=240,
    height=240,
    rotation=0,
    spi_speed_hz=60000000
)

disp.begin()

# Создаём красивую картинку
img = Image.new('RGB', (240, 240), color=(0, 50, 100))
draw = ImageDraw.Draw(img)

# Градиент
for y in range(240):
    color = int(255 * y / 240)
    draw.line([(0, y), (240, y)], fill=(color, 100, 255-color))

# Текст
draw.text((60, 100), "Raspberry Pi", fill=(255, 255, 255))
draw.text((70, 130), "ST7789 OK!", fill=(0, 255, 0))

# Круг
draw.ellipse((90, 50, 150, 110), fill=(255, 255, 0), outline=(255, 0, 0))

disp.display(img)
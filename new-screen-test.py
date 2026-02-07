import board
import displayio
from adafruit_st7789 import ST7789
import terminalio
from adafruit_display_text import label

# Освобождаем дисплей если занят
displayio.release_displays()

# Настройка SPI
spi = board.SPI()
tft_dc = board.D24
tft_res = board.D25

# Создаём шину без CS
display_bus = displayio.FourWire(
    spi, 
    command=tft_dc, 
    reset=tft_res,
    baudrate=40000000
)

# Инициализация ST7789
display = ST7789(
    display_bus, 
    width=240, 
    height=240,
    rotation=0,
    rowstart=0,
    colstart=0
)

# Создаём группу для отображения
splash = displayio.Group()
display.root_group = splash

# Создаём цветную палитру
color_bitmap = displayio.Bitmap(240, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFF0000  # Красный

# Добавляем фон
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Добавляем текст
text = "Hello Pi!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=80, y=120)
splash.append(text_area)

print("Дисплей инициализирован!")

# Экран должен стать красным с белым текстом
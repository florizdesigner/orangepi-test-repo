import spidev
import RPi.GPIO as GPIO
import time

# Настройка GPIO
DC_PIN = 24
RST_PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(RST_PIN, GPIO.OUT)

# Сброс дисплея
print("Сброс дисплея...")
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.1)

# Открываем SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 24000000

def write_command(cmd):
    GPIO.output(DC_PIN, GPIO.LOW)  # Command mode
    spi.writebytes([cmd])

def write_data(data):
    GPIO.output(DC_PIN, GPIO.HIGH)  # Data mode
    if isinstance(data, list):
        spi.writebytes(data)
    else:
        spi.writebytes([data])

# Инициализация ST7789
print("Инициализация ST7789...")

write_command(0x01)  # Software reset
time.sleep(0.15)

write_command(0x11)  # Sleep out
time.sleep(0.5)

write_command(0x3A)  # Pixel format
write_data(0x55)     # 16-bit color

write_command(0x36)  # Memory access control
write_data(0x00)     # RGB order

write_command(0x29)  # Display on
time.sleep(0.1)

# Заливаем экран красным
print("Заливка красным...")

write_command(0x2A)  # Column address
write_data([0x00, 0x00, 0x00, 0xEF])  # 0-239

write_command(0x2B)  # Row address
write_data([0x00, 0x00, 0x00, 0xEF])  # 0-239

write_command(0x2C)  # Memory write

# Красный цвет в RGB565: 0xF800
GPIO.output(DC_PIN, GPIO.HIGH)
red_pixel = [0xF8, 0x00]
for i in range(240 * 240):
    spi.writebytes(red_pixel)
    if i % 10000 == 0:
        print(f"Прогресс: {i}/{240*240}")

print("Готово! Экран должен быть красным.")

spi.close()
GPIO.cleanup()
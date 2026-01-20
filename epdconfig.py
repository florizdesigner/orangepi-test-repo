import OPi.GPIO as GPIO
import spidev
import time

# Pin definition (BOARD numbering)
RST_PIN   = 11  # GPIO 226
DC_PIN    = 22  # GPIO 262
CS_PIN    = 24  # GPIO 229
BUSY_PIN  = 18  # GPIO 228

# Для SPI используются фиксированные пины:
# Pin 19 (GPIO 231) - MOSI
# Pin 23 (GPIO 230) - CLK
# Pin 24 (GPIO 229) - CS

# SPI device, bus = 1, device = 0
SPI = spidev.SpiDev(1, 0)

def digital_write(pin, value):
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(pin)

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(data):
    SPI.writebytes(data)

def module_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.setup(BUSY_PIN, GPIO.IN)
    
    SPI.max_speed_hz = 4000000
    SPI.mode = 0b00
    return 0

def module_exit():
    GPIO.output(RST_PIN, 0)
    GPIO.output(DC_PIN, 0)
    SPI.close()
    GPIO.cleanup()

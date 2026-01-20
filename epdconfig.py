import gpiod
import spidev
import time

# Chip name для Orange Pi Zero 2W
CHIP_NAME = "gpiochip0"

# GPIO numbers (из вашей таблицы BOARD)
RST_PIN   = 226  # Pin 11
DC_PIN    = 262  # Pin 22
CS_PIN    = 229  # Pin 24
BUSY_PIN  = 228  # Pin 18

# GPIO lines
chip = None
rst_line = None
dc_line = None
cs_line = None
busy_line = None

# SPI device
SPI = spidev.SpiDev(1, 0)

def digital_write(pin, value):
    if pin == RST_PIN:
        rst_line.set_value(value)
    elif pin == DC_PIN:
        dc_line.set_value(value)
    elif pin == CS_PIN:
        cs_line.set_value(value)

def digital_read(pin):
    if pin == BUSY_PIN:
        return busy_line.get_value()
    return 0

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(data):
    SPI.writebytes(data)

def module_init():
    global chip, rst_line, dc_line, cs_line, busy_line
    
    chip = gpiod.Chip(CHIP_NAME)
    
    # Request GPIO lines
    rst_line = chip.get_line(RST_PIN)
    dc_line = chip.get_line(DC_PIN)
    cs_line = chip.get_line(CS_PIN)
    busy_line = chip.get_line(BUSY_PIN)
    
    # Configure as output/input
    rst_line.request(consumer="epd", type=gpiod.LINE_REQ_DIR_OUT)
    dc_line.request(consumer="epd", type=gpiod.LINE_REQ_DIR_OUT)
    cs_line.request(consumer="epd", type=gpiod.LINE_REQ_DIR_OUT)
    busy_line.request(consumer="epd", type=gpiod.LINE_REQ_DIR_IN)
    
    # SPI setup
    SPI.max_speed_hz = 4000000
    SPI.mode = 0b00
    
    return 0

def module_exit():
    rst_line.set_value(0)
    dc_line.set_value(0)
    
    rst_line.release()
    dc_line.release()
    cs_line.release()
    busy_line.release()
    
    SPI.close()
    chip.close()

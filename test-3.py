#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spidev
import gpiod
import time
from PIL import Image, ImageDraw, ImageFont

class EPD:
    """Драйвер для 3-дюймового e-ink дисплея Waveshare"""
    
    def __init__(self):
        # Параметры дисплея (для 3" обычно 400x240)
        self.width = 400
        self.height = 240
        
        # Настройка GPIO пинов (измените под свою распиновку)
        # Обычно для Orange Pi Zero 2W:
        self.RST_PIN = 17  # Reset
        self.DC_PIN = 25   # Data/Command
        self.CS_PIN = 8    # Chip Select (обычно управляется SPI)
        self.BUSY_PIN = 24 # Busy
        
        # Инициализация gpiod 2.4.0
        # Открываем линии напрямую
        self.rst_line = gpiod.request_lines(
            '/dev/gpiochip0',
            consumer='eink',
            config={self.RST_PIN: gpiod.LineSettings(direction=gpiod.line.Direction.OUTPUT)}
        )
        
        self.dc_line = gpiod.request_lines(
            '/dev/gpiochip0',
            consumer='eink',
            config={self.DC_PIN: gpiod.LineSettings(direction=gpiod.line.Direction.OUTPUT)}
        )
        
        self.busy_line = gpiod.request_lines(
            '/dev/gpiochip0',
            consumer='eink',
            config={self.BUSY_PIN: gpiod.LineSettings(direction=gpiod.line.Direction.INPUT)}
        )
        
        # Инициализация SPI
        self.spi = spidev.SpiDev()
        self.spi.open(1, 0)  # bus=1, device=0 (может быть 0,0 - проверьте через ls /dev/spi*)
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0
        
    def digital_write(self, line_request, pin, value):
        """Запись в GPIO"""
        gpio_value = gpiod.line.Value.ACTIVE if value else gpiod.line.Value.INACTIVE
        line_request.set_value(pin, gpio_value)
        
    def digital_read(self, line_request, pin):
        """Чтение из GPIO"""
        return line_request.get_value(pin) == gpiod.line.Value.ACTIVE
        
    def reset(self):
        """Аппаратный сброс дисплея"""
        self.digital_write(self.rst_line, self.RST_PIN, 1)
        time.sleep(0.2)
        self.digital_write(self.rst_line, self.RST_PIN, 0)
        time.sleep(0.01)
        self.digital_write(self.rst_line, self.RST_PIN, 1)
        time.sleep(0.2)
        
    def send_command(self, command):
        """Отправка команды"""
        self.digital_write(self.dc_line, self.DC_PIN, 0)  # Command mode
        self.spi.writebytes([command])
        
    def send_data(self, data):
        """Отправка данных"""
        self.digital_write(self.dc_line, self.DC_PIN, 1)  # Data mode
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)
            
    def wait_until_idle(self):
        """Ожидание готовности дисплея"""
        print("Ожидание готовности дисплея...")
        while self.digital_read(self.busy_line, self.BUSY_PIN) == 1:
            time.sleep(0.1)
        print("Дисплей готов")
        
    def init(self):
        """Инициализация дисплея (для 3" Waveshare)"""
        self.reset()
        
        # Последовательность инициализации для 3-дюймового дисплея
        # Эти команды могут отличаться в зависимости от модели!
        self.send_command(0x01)  # POWER_SETTING
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x3f)
        self.send_data(0x3f)
        
        self.send_command(0x04)  # POWER_ON
        time.sleep(0.1)
        self.wait_until_idle()
        
        self.send_command(0x00)  # PANEL_SETTING
        self.send_data(0x1F)     # LUT from OTP
        
        self.send_command(0x61)  # RESOLUTION_SETTING
        self.send_data(0x01)     # Width: 400
        self.send_data(0x90)
        self.send_data(0x00)     # Height: 240
        self.send_data(0xF0)
        
        self.send_command(0x15)
        self.send_data(0x00)
        
        self.send_command(0x50)  # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x10)
        self.send_data(0x07)
        
        self.send_command(0x60)  # TCON_SETTING
        self.send_data(0x22)
        
        print("Инициализация завершена")
        
    def display(self, image):
        """Вывод изображения на дисплей"""
        if image.mode != '1':
            image = image.convert('1')
            
        buf = [0xFF] * (self.width * self.height // 8)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        
        # Преобразование изображения в буфер
        for y in range(imheight):
            for x in range(imwidth):
                if pixels[x, y] == 0:
                    buf[(x + y * self.width) // 8] &= ~(0x80 >> (x % 8))
                    
        # Отправка буфера на дисплей
        self.send_command(0x13)  # WRITE_RAM
        self.send_data(buf)
        
        self.send_command(0x12)  # DISPLAY_REFRESH
        time.sleep(0.1)
        self.wait_until_idle()
        
    def clear(self):
        """Очистка дисплея (белый экран)"""
        buf = [0xFF] * (self.width * self.height // 8)
        
        self.send_command(0x13)
        self.send_data(buf)
        
        self.send_command(0x12)
        time.sleep(0.1)
        self.wait_until_idle()
        
    def sleep(self):
        """Перевод дисплея в режим сна"""
        self.send_command(0x02)  # POWER_OFF
        self.wait_until_idle()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)
        
    def cleanup(self):
        """Освобождение ресурсов"""
        self.spi.close()
        self.rst_line.release()
        self.dc_line.release()
        self.busy_line.release()


def main():
    """Тестовый пример"""
    try:
        print("Инициализация e-ink дисплея...")
        epd = EPD()
        epd.init()
        
        print("Очистка дисплея...")
        epd.clear()
        
        # Создание тестового изображения
        print("Создание тестового изображения...")
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Рисование фигур
        draw.rectangle((10, 10, 390, 230), outline=0)
        draw.rectangle((20, 20, 380, 220), outline=0)
        
        # Текст (нужен шрифт, или используйте стандартный)
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 50), 'Orange Pi Zero 2W', font=font, fill=0)
        draw.text((50, 100), 'E-ink Display Test', font=font, fill=0)
        draw.text((50, 150), 'Waveshare 3"', font=font, fill=0)
        
        # Геометрические фигуры
        draw.ellipse((250, 80, 350, 180), outline=0)
        draw.line((30, 200, 200, 200), fill=0, width=3)
        
        print("Отображение изображения...")
        epd.display(image)
        
        print("Готово! Переход в режим сна...")
        time.sleep(2)
        epd.sleep()
        
        print("Завершение работы")
        epd.cleanup()
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import serial
from PIL import Image, ImageDraw, ImageFont
import time
import epaper

# ===== Настройки =====
UART_PORT = '/dev/serial0'  # UART порт для PN532
BAUDRATE = 115200

# Словарь меток и связанной с ними информации
NFC_DATABASE = {
    '04A1B2C3D4E5F6': 'Ключ от офиса\nДоступ: Администратор',
    '04B2C3D4E5F6A1': 'Пропуск сотрудника\nИван Иванов',
    '04C3D4E5F6A1B2': 'Карта доступа\nСклад #3',
}

# ===== Класс для работы с PN532 =====
class PN532_UART:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)
        self.wake_up()
        self.SAM_configuration()
    
    def wake_up(self):
        """Пробуждение модуля"""
        self.serial.write(b'\x55\x55\x00\x00\x00')
        time.sleep(0.1)
        self.serial.reset_input_buffer()
    
    def send_command(self, command):
        """Отправка команды в PN532"""
        frame = self._build_frame(command)
        self.serial.write(frame)
        time.sleep(0.1)
        return self._read_response()
    
    def _build_frame(self, data):
        """Построение фрейма команды"""
        length = len(data) + 1
        lcs = (~length + 1) & 0xFF
        dcs = (~sum(data) + 1) & 0xFF
        
        frame = bytearray([0x00, 0x00, 0xFF, length, lcs])
        frame.extend([0xD4])
        frame.extend(data)
        frame.append(dcs)
        frame.append(0x00)
        
        return bytes(frame)
    
    def _read_response(self):
        """Чтение ответа от PN532"""
        response = self.serial.read(64)
        return response
    
    def SAM_configuration(self):
        """Настройка SAM"""
        self.send_command([0x14, 0x01, 0x00, 0x00])
    
    def read_passive_target(self):
        """Чтение пассивной метки (ISO14443A)"""
        response = self.send_command([0x4A, 0x01, 0x00])
        
        if len(response) > 20 and response[0:6] == b'\x00\x00\xFF':
            # Извлечение UID
            uid_length = response[12]
            uid = response[13:13 + uid_length]
            return binascii.hexlify(uid).decode('utf-8').upper()
        
        return None

# ===== Класс для работы с e-ink дисплеем =====
# Замените на библиотеку вашего конкретного дисплея
# Например, для Waveshare используйте их библиотеки

class EinkDisplay:
    def __init__(self):
        """
        Инициализация дисплея
        Для конкретной модели используйте соответствующую библиотеку:
        - Waveshare: from waveshare_epd import epd2in13_V2
        - Pimoroni: import inky
        """
        self.width = 400
        self.height = 168
        
        # Пример для Waveshare (раскомментируйте и адаптируйте):
#!/usr/bin/env python3
        self.epd = epaper.epaper('epd3in7').EPD()
        self.epd.init()
        self.epd.Clear(0xFF)
    
    def display_text(self, text, title="NFC Сканер"):
        """Отображение текста на дисплее"""
        # Создание изображения
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Загрузка шрифтов (можно использовать системные)
        try:
            font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
            font_text = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        # Отрисовка заголовка
        draw.text((10, 10), title, font=font_title, fill=0)
        draw.line((10, 35, self.width - 10, 35), fill=0, width=2)
        
        # Отрисовка основного текста
        y_position = 50
        for line in text.split('\n'):
            draw.text((10, y_position), line, font=font_text, fill=0)
            y_position += 20
        
        # Вывод на дисплей
        # Для Waveshare:
        # self.epd.display(self.epd.getbuffer(image))
        
        # Для тестирования сохраняем как картинку
        image.save('/tmp/nfc_display.png')
        print(f"Изображение сохранено в /tmp/nfc_display.png")
        print(f"Заголовок: {title}")
        print(f"Текст:\n{text}")
    
    def clear(self):
        """Очистка дисплея"""
        # self.epd.Clear(0xFF)
        pass

# ===== Основная программа =====
def main():
    print("Инициализация NFC-ридера и дисплея...")
    
    # Инициализация устройств
    try:
        nfc = PN532_UART(UART_PORT, BAUDRATE)
        display = EinkDisplay()
        print("✓ Устройства инициализированы")
    except Exception as e:
        print(f"✗ Ошибка инициализации: {e}")
        return
    
    # Отображение приветственного сообщения
    display.display_text("Приложите\nNFC-метку", "Готов к работе")
    
    print("\nОжидание NFC-метки...")
    last_uid = None
    
    while True:
        try:
            # Попытка чтения метки
            uid = nfc.read_passive_target()
            
            if uid and uid != last_uid:
                print(f"\n✓ Обнаружена метка: {uid}")
                last_uid = uid
                
                # Поиск информации о метке
                if uid in NFC_DATABASE:
                    info = NFC_DATABASE[uid]
                    print(f"  Информация: {info.replace(chr(10), ' | ')}")
                    display.display_text(info, f"Метка: {uid[:8]}...")
                else:
                    info = f"Неизвестная метка\nUID: {uid}"
                    print(f"  {info}")
                    display.display_text(info, "Не в базе")
                
                # Ожидание убирания метки
                time.sleep(2)
            
            elif not uid and last_uid:
                # Метка убрана
                print("Метка убрана")
                last_uid = None
                display.display_text("Приложите\nNFC-метку", "Готов к работе")
            
            time.sleep(0.3)
            
        except KeyboardInterrupt:
            print("\n\nЗавершение работы...")
            display.clear()
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()

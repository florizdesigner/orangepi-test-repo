#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd3in0g

# Словарь с предложениями
sentences = [
    "Привет, мир!",
    "E-ink дисплей работает",
    "Python + Pillow",
    "Waveshare EPD 3.0",
    "Быстрое обновление",
    "Тестовый режим",
    "Отлично работает!",
    "Энергоэффективно",
]

def main():
    try:
        print("Инициализация дисплея...")
        epd = epd3in0g.EPD()
        epd.init()
        epd.Clear()
        
        # Параметры дисплея
        width = 400
        height = 168
        
        # Загружаем шрифт (используем стандартный или укажите путь к .ttf)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        print("Начинаем вывод текста...")
        
        while True:
            # Выбираем случайное предложение
            text = random.choice(sentences)
            
            # Создаем изображение с белым фоном
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            # Получаем размеры текста для центрирования
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Вычисляем позицию для центрирования
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Рисуем черный текст
            draw.text((x, y), text, font=font, fill='black')
            
            # Отображаем на дисплее (быстрое обновление)
            epd.display(epd.getbuffer(image))
            
            print(f"Отображено: {text}")
            
            # Ждем 3 секунды
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nПрограмма остановлена")
        epd.Clear()
        epd.sleep()
        
    except Exception as e:
        print(f"Ошибка: {e}")

if name == "__main__":
    main()
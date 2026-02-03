#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Настройка пинов (измените под свои)
UP = 40
DOWN = 38
LEFT = 37
RIGHT = 36
MID = 35

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MID, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Тест джойстика запущен. Нажмите Ctrl+C для выхода.")
print("-" * 40)

try:
    while True:
        if GPIO.input(UP) == GPIO.LOW:
            print("⬆️  ВВЕРХ")
            time.sleep(0.2)
            
        if GPIO.input(DOWN) == GPIO.LOW:
            print("⬇️  ВНИЗ")
            time.sleep(0.2)
            
        if GPIO.input(LEFT) == GPIO.LOW:
            print("⬅️  ВЛЕВО")
            time.sleep(0.2)
            
        if GPIO.input(RIGHT) == GPIO.LOW:
            print("➡️  ВПРАВО")
            time.sleep(0.2)
            
        if GPIO.input(MID) == GPIO.LOW:
            print("🔘 КНОПКА НАЖАТА")
            time.sleep(0.2)
            
        time.sleep(0.05)
        
except KeyboardInterrupt:
    print("\n\nТест завершён.")
    GPIO.cleanup()

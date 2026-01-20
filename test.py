#!/usr/bin/python3
import OPi.GPIO as GPIO
import time

# Используем BOARD нумерацию
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Тест пинов
RST_PIN = 11
DC_PIN = 22
BUSY_PIN = 18

GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

print("Тест RST (pin 11)...")
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.5)

print("Тест DC (pin 22)...")
GPIO.output(DC_PIN, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(DC_PIN, GPIO.LOW)

print(f"BUSY pin (pin 18) состояние: {GPIO.input(BUSY_PIN)}")

GPIO.cleanup()
print("Тест завершен!")

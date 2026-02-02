import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.uart import PN532_UART

# Инициализация UART
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0.1)

# Создание объекта PN532
pn532 = PN532_UART(uart, debug=False)

# Получение версии прошивки
try:
    ic, ver, rev, support = pn532.firmware_version
    print('Найден чип PN532 с версией прошивки: {0}.{1}'.format(ver, rev))
    
    # Настройка для чтения карт
    pn532.SAM_configuration()
    print('Ожидание карты MiFare/RFID...')
    
    while True:
        # Проверка наличия карты
        uid = pn532.read_passive_target(timeout=0.5)
        
        if uid is not None:
            print('Найдена карта с UID:', [hex(i) for i in uid])
        
except RuntimeError as e:
    print('Ошибка:', e)
except Exception as e:
    print('Неожиданная ошибка:', e)

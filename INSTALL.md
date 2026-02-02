# Инструкция по установке и настройке

## Шаг 1: Подготовка Raspberry Pi

### 1.1 Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### 1.2 Включение UART для NFC-считывателя

Отредактируйте файл config.txt:

```bash
sudo nano /boot/config.txt
```

Добавьте в конец файла:

```
# Enable UART for NFC Reader
enable_uart=1
dtoverlay=disable-bt
```

Сохраните (Ctrl+O, Enter, Ctrl+X).

### 1.3 Включение SPI для E-ink дисплея

```bash
sudo raspi-config
```

Выберите:
- 3 Interface Options
- I4 SPI
- Yes (включить)
- OK
- Finish

Перезагрузите:

```bash
sudo reboot
```

## Шаг 2: Физическое подключение

### 2.1 NFC Reader PN532

Подключите к Raspberry Pi:

| PN532 | Raspberry Pi |
|-------|--------------|
| VCC   | 3.3V (Pin 1) |
| GND   | GND (Pin 6)  |
| TX    | RX (GPIO 15, Pin 10) |
| RX    | TX (GPIO 14, Pin 8)  |

### 2.2 Waveshare E-ink Display

Подключение зависит от модели дисплея. Обычно используются следующие пины:

| Display | Raspberry Pi |
|---------|--------------|
| VCC     | 3.3V         |
| GND     | GND          |
| DIN     | MOSI (GPIO 10, Pin 19) |
| CLK     | SCLK (GPIO 11, Pin 23) |
| CS      | CE0 (GPIO 8, Pin 24)   |
| DC      | GPIO 25 (Pin 22)       |
| RST     | GPIO 17 (Pin 11)       |
| BUSY    | GPIO 24 (Pin 18)       |

**ВАЖНО:** Проверьте схему подключения для вашей конкретной модели дисплея!

### 2.3 Кнопка (опционально)

Подключите кнопку между GPIO 17 (Pin 11) и GND (Pin 9).

## Шаг 3: Установка программного обеспечения

### 3.1 Установка зависимостей

```bash
# Базовые инструменты
sudo apt install python3 python3-pip git -y

# Библиотеки для работы с GPIO и SPI
sudo apt install python3-rpi.gpio python3-spidev -y

# Библиотеки для работы с изображениями
sudo apt install python3-pil -y
```

### 3.2 Загрузка проекта

```bash
cd ~
git clone <URL_РЕПОЗИТОРИЯ> nfc-registration-system
cd nfc-registration-system
```

Или создайте директорию и скопируйте файлы вручную:

```bash
mkdir -p ~/nfc-registration-system
cd ~/nfc-registration-system
# Скопируйте все файлы проекта в эту директорию
```

### 3.3 Установка Python зависимостей

```bash
pip3 install -r requirements.txt
```

### 3.4 Установка библиотеки Waveshare E-ink

**ВАЖНО:** Замените `epd2in9` на вашу модель дисплея!

```bash
cd ~
git clone https://github.com/waveshare/e-Paper
cd e-Paper/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install
```

Доступные модели:
- epd1in54 (1.54 inch)
- epd2in9 (2.9 inch)
- epd2in9b (2.9 inch B/W/Red)
- epd2in9d (2.9 inch flexible)
- epd3in7 (3.7 inch)
- epd4in2 (4.2 inch)
- и другие...

Проверьте документацию вашего дисплея!

## Шаг 4: Настройка приложения

### 4.1 Создание файла .env для аутентификации

**ВАЖНО:** API требует аутентификацию через `/api/users/auth`

Создайте файл `.env` на основе примера:

```bash
cd ~/nfc-registration-system
cp .env.example .env
nano .env
```

Заполните ваши учетные данные:

```bash
# API Authentication
API_USERNAME=your_username_here
API_PASSWORD=your_password_here

# Optional: если у вас уже есть токен
# API_TOKEN=your_bearer_token_here
```

**ВАЖНО:** Файл `.env` содержит секретные данные! Никогда не делитесь им и не добавляйте в git!

### 4.2 Редактирование config.py

```bash
cd ~/nfc-registration-system
nano config.py
```

Настройте следующие параметры:

```python
# API Configuration
API_BASE_URL = "https://api.velowcyclingclub.ru/v3"
API_TOKEN = None  # Установите токен, если требуется

# Display Configuration
DISPLAY_MODEL = "epd2in9"  # ИЗМЕНИТЕ НА ВАШУ МОДЕЛЬ!

# NFC Reader Configuration
NFC_UART_PORT = "/dev/serial0"  # Или "/dev/ttyAMA0"

# GPIO Configuration
BUTTON_GPIO_PIN = 17  # Пин кнопки (если используете)

# Development/Testing
USE_MOCK_NFC = False  # True для тестирования без NFC
USE_MOCK_DISPLAY = False  # True для тестирования без дисплея
```

### 4.2 Редактирование config.py

```bash
cd ~/nfc-registration-system
nano config.py
```

Настройте следующие параметры:

```python
# Display Configuration (для 400x168 дисплея)
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 168
DISPLAY_MODEL = "epd3in7"  # 3.7" дисплей Waveshare

# NFC Reader Configuration
NFC_UART_PORT = "/dev/serial0"  # Или "/dev/ttyAMA0"

# GPIO Configuration
BUTTON_GPIO_PIN = 17  # ИЗМЕНИТЕ на ваш пин, когда установите кнопку!

# Development/Testing
USE_MOCK_NFC = False  # True для тестирования без NFC
USE_MOCK_DISPLAY = False  # True для тестирования без дисплея
```

**ПРИМЕЧАНИЕ:** API_USERNAME и API_PASSWORD берутся из файла `.env`

### 4.3 Редактирование display_manager.py

**Для дисплея 400x168 (3.7")** - файл уже настроен правильно!

Если ваш дисплей другой модели, откройте файл:

```bash
nano display_manager.py
```

Найдите строки в начале файла:

```python
try:
    from waveshare_epd import epd3in7
    EPD = epd3in7.EPD()
```

Замените `epd3in7` на вашу модель дисплея, если отличается.

### 4.4 Создание директории для медиа-файлов

```bash
mkdir -p ~/nfc-registration-system/media
```

Поместите файл `velow.png` в эту директорию.

## Шаг 5: Тестирование

### 5.1 Тест API

```bash
cd ~/nfc-registration-system
python3 test_api.py
```

Для полного теста с user ID:

```bash
python3 test_api.py USER123
```

### 5.2 Тест NFC считывателя

Чтение метки:

```bash
python3 nfc_program.py read
```

Запись ID на метку:

```bash
python3 nfc_program.py write USER001
```

### 5.3 Тест основного приложения

Запуск с mock-компонентами (без hardware):

```bash
# В config.py установите:
# USE_MOCK_NFC = True
# USE_MOCK_DISPLAY = True
python3 main.py
```

Запуск с реальным hardware:

```bash
# В config.py установите:
# USE_MOCK_NFC = False
# USE_MOCK_DISPLAY = False
python3 main.py
```

## Шаг 6: Настройка автозапуска

### 6.1 Создание systemd service

```bash
sudo nano /etc/systemd/system/nfc-registration.service
```

Содержимое:

```ini
[Unit]
Description=NFC Registration System for Velow Cycling Club
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nfc-registration-system
ExecStart=/usr/bin/python3 /home/pi/nfc-registration-system/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 6.2 Активация service

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable nfc-registration.service

# Запуск сервиса
sudo systemctl start nfc-registration.service

# Проверка статуса
sudo systemctl status nfc-registration.service
```

### 6.3 Управление сервисом

```bash
# Остановка
sudo systemctl stop nfc-registration.service

# Перезапуск
sudo systemctl restart nfc-registration.service

# Просмотр логов
sudo journalctl -u nfc-registration.service -f

# Просмотр последних 100 строк логов
sudo journalctl -u nfc-registration.service -n 100
```

## Шаг 7: Отладка

### 7.1 Проверка UART

```bash
# Проверка доступности порта
ls -l /dev/serial0
ls -l /dev/ttyAMA0

# Если порта нет, проверьте config.txt
cat /boot/config.txt | grep uart
```

### 7.2 Проверка SPI

```bash
# Проверка модуля SPI
lsmod | grep spi

# Должны быть строки:
# spi_bcm2835
```

### 7.3 Проверка GPIO

```bash
# Установка утилиты
sudo apt install raspi-gpio

# Проверка статуса пинов
raspi-gpio get
```

### 7.4 Просмотр логов приложения

```bash
# Логи systemd
sudo journalctl -u nfc-registration.service -f

# Или если запускаете вручную
python3 main.py 2>&1 | tee app.log
```

## Распространенные проблемы

### NFC не читается

1. Проверьте подключение проводов
2. Убедитесь, что UART включен (`enable_uart=1` в config.txt)
3. Попробуйте `/dev/ttyAMA0` вместо `/dev/serial0`
4. Проверьте, что скорость 115200

### Дисплей не работает

1. Проверьте, что SPI включен (`sudo raspi-config`)
2. Убедитесь, что установлена библиотека для вашей модели
3. Проверьте физическое подключение
4. Попробуйте примеры из репозитория Waveshare

### API не отвечает

1. Проверьте интернет: `ping api.velowcyclingclub.ru`
2. Проверьте правильность `API_BASE_URL` в config.py
3. Проверьте, нужна ли авторизация (установите `API_TOKEN`)

### Кнопка не работает

1. Проверьте физическое подключение
2. Убедитесь, что `RPi.GPIO` установлен
3. Проверьте номер пина в `config.py`

## Дополнительно

### Обновление приложения

```bash
cd ~/nfc-registration-system
git pull
sudo systemctl restart nfc-registration.service
```

### Резервное копирование

```bash
# Создание бэкапа конфигурации
cp config.py config.py.backup

# Создание бэкапа всего проекта
cd ~
tar -czf nfc-registration-backup-$(date +%Y%m%d).tar.gz nfc-registration-system/
```

### Мониторинг системы

```bash
# CPU температура
vcgencmd measure_temp

# Использование памяти
free -h

# Использование диска
df -h
```

## Контакты для поддержки

Email: support@velowcyclingclub.ru

Документация API: https://api.velowcyclingclub.ru/v3/api-docs

# NFC Registration System для Velow Cycling Club

Система регистрации участников через NFC-метки на базе Raspberry Pi Zero 2 W.

## Компоненты

- **Raspberry Pi Zero 2 W** - основной контроллер
- **PN532 NFC Reader** - считыватель NFC-меток (UART, 115200 baud)
- **Waveshare 3.7" E-ink Display** - дисплей 400x168 пикселей для вывода информации (SPI)

## Архитектура

### Модули

1. **main.py** - главный файл приложения с машиной состояний
2. **api_client.py** - клиент для работы с REST API бэкенда
3. **nfc_reader.py** - менеджер NFC-считывателя PN532
4. **display_manager.py** - менеджер E-ink дисплея

### Логика работы

```
[IDLE] Показ лого velow.png
   ↓
[Нажатие кнопки - не реализовано]
   ↓
[WAITING_NFC] "Приложите ваш NFC-брелок"
   ↓
[Считывание NFC]
   ↓
[PROCESSING] "Пожалуйста, подождите..."
   ↓
[Проверка активного события] → Если нет: "Упс! Активных эвентов нет"
   ↓
[Запрос пользователя GET /api/users/{id}]
   ↓
   ├─ Не найден → "Пользователь не найден"
   └─ Найден
      ↓
[Завершение регистрации POST /api/events/finish/{id}]
      ↓
      ├─ Ошибка → "{user.name}, упс! Что-то пошло не так"
      └─ Успех → "✓ Регистрация для пользователя {username} завершена"
      ↓
[Задержка 2 секунды]
   ↓
[Возврат в WAITING_NFC]
```

## Установка

### 1. Настройка Raspberry Pi

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip git -y

# Включение UART (для NFC)
# Добавьте в /boot/config.txt:
# enable_uart=1
# dtoverlay=disable-bt

# Включение SPI (для дисплея)
sudo raspi-config
# Interface Options → SPI → Enable
```

### 2. Установка зависимостей

```bash
# Клонирование проекта
git clone <repository_url>
cd nfc-registration-system

# Установка Python зависимостей
pip3 install -r requirements.txt

# Установка библиотеки Waveshare E-ink
# ВАЖНО: Замените на вашу модель дисплея (например, epd2in9, epd3in7)
git clone https://github.com/waveshare/e-Paper
cd e-Paper/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install
cd ../../..
```

### 3. Настройка hardware

**NFC Reader PN532:**
- TX → RX (GPIO 15)
- RX → TX (GPIO 14)
- VCC → 3.3V
- GND → GND

**E-ink Display:**
- Подключается к SPI интерфейсу согласно схеме вашего дисплея
- Обычно: MOSI, MISO, SCLK, CS, DC, RST, BUSY

**Кнопка (опционально):**
- Один контакт → GPIO (например, GPIO 17)
- Второй контакт → GND

### 4. Настройка приложения

Создайте файл `.env` для аутентификации API:

```bash
cp .env.example .env
nano .env
```

Заполните учетные данные:

```bash
API_USERNAME=your_username_here
API_PASSWORD=your_password_here
```

Отредактируйте `config.py` при необходимости (для кнопки, mock режимов и т.д.)

### 5. Подготовка медиа-файлов

Создайте директорию и поместите логотип:

```bash
mkdir media
# Поместите файл velow.png в директорию media/
```

## Запуск

### Тестовый запуск (с mock-компонентами)

Для тестирования без hardware:

```bash
python3 main.py
```

Mock-компоненты автоматически активируются, если библиотеки недоступны.

### Продакшн запуск

```bash
# Запуск приложения
python3 main.py

# Запуск в фоне с логированием
nohup python3 main.py > app.log 2>&1 &
```

### Автозапуск при загрузке

Создайте systemd service:

```bash
sudo nano /etc/systemd/system/nfc-registration.service
```

Содержимое:

```ini
[Unit]
Description=NFC Registration System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nfc-registration-system
ExecStart=/usr/bin/python3 /home/pi/nfc-registration-system/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nfc-registration.service
sudo systemctl start nfc-registration.service

# Проверка статуса
sudo systemctl status nfc-registration.service

# Просмотр логов
sudo journalctl -u nfc-registration.service -f
```

## Использование

1. При запуске отображается логотип `velow.png`
2. Нажмите кнопку (когда будет установлена) для начала сканирования
3. Приложите NFC-брелок к считывателю
4. Дождитесь результата на экране
5. Система автоматически вернется в режим ожидания

## API

### Аутентификация

API использует приватный метод `/api/users/auth` для аутентификации.  
Учетные данные хранятся в файле `.env`:

```bash
API_USERNAME=your_username
API_PASSWORD=your_password
```

При запуске приложение автоматически получает bearer token и использует его для всех запросов.

### Используемые endpoints

- `POST /api/users/auth` - аутентификация и получение токена
- `GET /api/events` - получение списка событий
- `GET /api/users/{id}` - получение информации о пользователе
- `POST /api/events/finish/{id}` - завершение регистрации

### Формат данных NFC

ID пользователя записан в NFC-метку в **текстовом формате**.

**Способ чтения:**
- Приложение читает UID метки и использует его как ID пользователя
- Альтернативно: можно записать текстовый ID в NDEF формат (требует доработки `_read_ndef_user_id()`)

**Запись ID на метку:**
Используйте утилиту программирования:

```bash
python3 nfc_program.py write USER123
```

Это запишет "USER123" в текстовом формате на NFC-метку.

## Отладка

### Проверка UART

```bash
# Проверка доступности порта
ls -l /dev/serial0
# или
ls -l /dev/ttyAMA0

# Тест скорости
stty -F /dev/serial0 115200
```

### Проверка SPI

```bash
# Проверка включения SPI
lsmod | grep spi
```

### Логирование

Уровень логирования настраивается в `main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Решение проблем

### NFC не читается

1. Проверьте подключение UART
2. Убедитесь, что UART включен в config.txt
3. Проверьте скорость (115200)
4. Попробуйте использовать /dev/ttyAMA0 вместо /dev/serial0

### Дисплей не работает

1. Проверьте, что SPI включен (`sudo raspi-config`)
2. Убедитесь, что установлена правильная библиотека для вашей модели
3. Проверьте физические подключения

### API не отвечает

1. Проверьте интернет-соединение: `ping api.velowcyclingclub.ru`
2. Проверьте правильность API_BASE_URL
3. Если требуется авторизация, установите API_TOKEN

## Структура проекта

```
nfc-registration-system/
├── main.py              # Главное приложение
├── api_client.py        # API клиент
├── nfc_reader.py        # NFC считыватель
├── display_manager.py   # Менеджер дисплея
├── requirements.txt     # Зависимости
├── README.md           # Документация
└── media/              # Медиа-файлы
    └── velow.png       # Логотип
```

## TODO

- [ ] Физическая установка кнопки и настройка GPIO пина в config.py
- [ ] Доработка чтения NDEF текста из NFC-меток (метод `_read_ndef_user_id()`)
- [ ] Улучшенная обработка записи NDEF формата
- [ ] Веб-интерфейс для конфигурации
- [ ] Статистика использования
- [ ] Оффлайн режим с синхронизацией

## Лицензия

Proprietary - Velow Cycling Club

## Контакты

Для вопросов и поддержки: support@velowcyclingclub.ru

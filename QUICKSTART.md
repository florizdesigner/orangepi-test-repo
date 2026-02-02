# Быстрый старт

Краткое руководство для запуска NFC Registration System.

## Предварительные требования

✅ Raspberry Pi Zero 2 W с Raspberry Pi OS  
✅ PN532 NFC Reader подключен к UART  
✅ Waveshare 3.7" E-ink дисплей (400x168) подключен к SPI  
✅ Интернет-соединение  

## Шаги

### 1. Скачать и установить

```bash
cd ~
git clone <repository_url> nfc-registration-system
cd nfc-registration-system
pip3 install -r requirements.txt
```

### 2. Настроить аутентификацию

```bash
cp .env.example .env
nano .env
```

Заполните:
```
API_USERNAME=your_username
API_PASSWORD=your_password
```

### 3. Создать директорию для изображений

```bash
mkdir media
# Поместите velow.png (400x168 px) в media/
```

### 4. Настроить GPIO кнопки (опционально)

Если кнопка установлена, отредактируйте `config.py`:

```python
BUTTON_GPIO_PIN = 17  # Ваш GPIO пин
```

### 5. Протестировать

**Тест API:**
```bash
python3 test_api.py
```

**Тест NFC:**
```bash
python3 nfc_program.py read
```

**Тест приложения (mock режим):**

В `config.py` установите:
```python
USE_MOCK_NFC = True
USE_MOCK_DISPLAY = True
```

Затем:
```bash
python3 main.py
```

### 6. Запустить в продакшн

В `config.py` установите:
```python
USE_MOCK_NFC = False
USE_MOCK_DISPLAY = False
```

Запуск:
```bash
python3 main.py
```

### 7. Настроить автозапуск

```bash
sudo cp systemd/nfc-registration.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nfc-registration.service
sudo systemctl start nfc-registration.service
```

Проверка:
```bash
sudo systemctl status nfc-registration.service
sudo journalctl -u nfc-registration.service -f
```

## Программирование NFC-меток

Запись user ID на метку:

```bash
python3 nfc_program.py write USER001
```

Чтение метки:

```bash
python3 nfc_program.py read
```

## Работа с кнопкой

**Без кнопки:** Приложение автоматически начнет сканирование через 3 секунды после запуска.

**С кнопкой:**
- Первое нажатие → начать сканирование NFC
- Второе нажатие → остановить сканирование, вернуться к экрану с логотипом

## Основные файлы

- **config.py** - настройки приложения
- **.env** - учетные данные API (секретно!)
- **media/velow.png** - логотип для приветственного экрана
- **main.py** - запуск приложения

## Логи

Просмотр логов:

```bash
# Если запущено через systemd
sudo journalctl -u nfc-registration.service -f

# Если запущено вручную
tail -f app.log
```

## Решение проблем

### NFC не читается
```bash
ls -l /dev/serial0
# Если нет - проверьте /boot/config.txt: enable_uart=1
```

### Дисплей не работает
```bash
lsmod | grep spi
# Если пусто - включите SPI в raspi-config
```

### API не отвечает
```bash
ping api.velowcyclingclub.ru
# Проверьте .env файл с учетными данными
```

## Полная документация

- **README.md** - общее описание проекта
- **INSTALL.md** - подробная инструкция по установке

## Поддержка

Email: support@velowcyclingclub.ru

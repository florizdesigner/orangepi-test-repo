"""
Configuration file for NFC Registration System
Edit these settings according to your setup
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_BASE_URL = "https://api.velowcyclingclub.ru/api"

# API Authentication (loaded from .env)
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_TOKEN = os.getenv("API_TOKEN")  # Optional: if you have token directly

# NFC Reader Configuration
NFC_UART_PORT = "/dev/serial0"  # or "/dev/ttyAMA0"
NFC_BAUDRATE = 115200

# Display Configuration
# Waveshare 3" E-ink display - 400x168 pixels
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 168
DISPLAY_MODEL = "epd3in7"  # Waveshare 3.7" display (closest to 400x168)

# GPIO Configuration (for button)
# IMPORTANT: Change this to your actual GPIO pin when you install the button
BUTTON_BOUNCE_TIME = 300  # milliseconds

# Физические пины
BUTTON_START_PIN = 6   # Кнопка START (начать сканирование)
BUTTON_STOP_PIN = 13   # Кнопка STOP (остановить сканирование)

# Application Settings
MEDIA_DIRECTORY = "./media"  # Directory for images
LOGO_FILENAME = "velow.bmp"

# Timing Settings (in seconds)
MESSAGE_DISPLAY_TIME = 2  # How long to show success/error messages
NFC_READ_TIMEOUT = 0.1  # Timeout for NFC tag detection

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Development/Testing
USE_MOCK_NFC = False  # Set to True to use mock NFC reader
USE_MOCK_DISPLAY = False  # Set to True to use mock display

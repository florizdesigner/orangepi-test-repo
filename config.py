"""
Configuration file for NFC Registration System
Edit these settings according to your setup
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_BASE_URL = "10.40.0.3:8080"

# API Authentication (loaded from .env)
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_TOKEN = os.getenv("API_TOKEN")  # Optional: if you have token directly

# NFC Reader Configuration
NFC_UART_PORT = "/dev/serial0"  # or "/dev/ttyAMA0"
NFC_BAUDRATE = 115200

# Display Configuration
# Waveshare 3.7" E-ink display - 400x168 pixels (landscape orientation)
# DISPLAY_WIDTH = 400   # Width in landscape mode
# DISPLAY_HEIGHT = 168  # Height in landscape mode
DISPLAY_HEIGHT = 400
DISPLAY_WIDTH = 168
DISPLAY_MODEL = "epd3in0g"  # Waveshare 3.7" display

# GPIO Configuration (BCM numbering)
# Physical Pin 31 = BCM GPIO 6
BUTTON_START_PIN = 6  # Physical pin 31 - Start scanning
# Physical Pin 33 = BCM GPIO 13  
BUTTON_STOP_PIN = 13  # Physical pin 33 - Stop scanning
BUTTON_BOUNCE_TIME = 300  # milliseconds

# Application Settings
MEDIA_DIRECTORY = "./media"  # Directory for images
LOGO_FILENAME = "velow.bmp"

# Welcome screen text (instead of logo image)
WELCOME_TEXT = "Velow Cycling Club\n\nСистема регистрации"

# Timing Settings (in seconds)
MESSAGE_DISPLAY_TIME = 2  # How long to show success/error messages
NFC_READ_TIMEOUT = 0.1  # Timeout for NFC tag detection

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""
NFC Tag Programming Utility
Tool for writing user IDs to NFC tags
"""
import logging
from nfc_manager import NFCManager
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# Инициализация
# -------------------------
reader = NFCManager(uart_port="/dev/serial0", baudrate=115200, hmac_secret=config.HMAC_SECRET)
reader.initialize()

# -------------------------
# Запись на метку
# -------------------------
reader.start_writing()
success = reader.write_tag("USER_1001")
if success:
    print("✅ Tag written successfully")
else:
    print("❌ Failed to write tag")
reader.stop_writing()

# -------------------------
# Чтение с проверкой HMAC
# -------------------------
reader.start_reading()
uid = reader.read_tag()
if uid:
    print("✅ Valid tag read, uid:", uid)
else:
    print("❌ Invalid or no tag detected")
reader.stop_reading()

# -------------------------
# Очистка
# -------------------------
reader.cleanup()
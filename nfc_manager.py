"""
NFC Reader Manager
Handles NFC tag reading using PN532 via UART
"""
import logging
import time
from typing import Optional
import json
import serial
import config
from encryptor import NFCHMAC

try:
    from adafruit_pn532.uart import PN532_UART
except ImportError:
    # Fallback for development without hardware
    PN532_UART = None


logger = logging.getLogger(__name__)


class NFCManager:
    """Manager for PN532 NFC reader via UART"""
    
    def __init__(self, uart_port: str = "/dev/serial0", baudrate: int = 115200):
        """
        Initialize NFC reader
        
        Args:
            uart_port: UART port (default: /dev/serial0 for Raspberry Pi)
            baudrate: UART baudrate (default: 115200)
        """
        self.uart_port = uart_port
        self.baudrate = baudrate
        self.pn532 = None
        self.uart = None
        self.reading = False
        self.writing = False
        self.signer = None
        
    def initialize(self):
        """Initialize the PN532 NFC reader"""
        if PN532_UART is None:
            logger.error("Adafruit PN532 library not installed")
            raise RuntimeError("PN532 library not available")
        
        try:
            # Initialize UART
            self.uart = serial.Serial(
                self.uart_port,
                baudrate=self.baudrate,
                timeout=1
            )
            
            # Initialize PN532
            self.pn532 = PN532_UART(self.uart, debug=False)
            
            # Configure PN532
            ic, ver, rev, support = self.pn532.firmware_version
            logger.info(f"Found PN532 with firmware version: {ver}.{rev}")
            
            # Configure to read RFID tags
            self.pn532.SAM_configuration()
            
            secret = config.HMAC_SECRET
            self.signer = NFCHMAC(secret)

            logger.info("NFC reader initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NFC reader: {e}")
            raise
    
    def start_reading(self):
        """Start reading mode"""
        self.reading = True
        logger.info("NFC reader started")
    
    def stop_reading(self):
        """Stop reading mode"""
        self.reading = False
        logger.info("NFC reader stopped")

    def start_writing(self):
        """Start reading mode"""
        self.writing = True
        logger.info("NFC writer started")
    
    def stop_writing(self):
        """Stop reading mode"""
        self.writing = False
        logger.info("NFC writer stopped")
    
    def read_tag(self, timeout: float = 0.1) -> Optional[str]:
        """
        Try to read an NFC tag
        
        Args:
            timeout: Timeout in seconds for tag detection
            
        Returns:
            User ID as string if tag detected, None otherwise
        """
        if not self.reading or self.pn532 is None:
            return None
        
        try:
            # Try to read NDEF data (if available)
            valid, uid = self._read_and_verify_hmac(self.signer)
            if valid == None: 
                return None
            
            if valid == True:
                logger.info(f"Successfully readed tag, uid={uid}")
                return uid
            else:
                logger.warning("❌ Invalid or cloned tag")
                    
            return None
            
        except Exception as e:
            logger.error(f"Error reading NFC tag: {e}")
            return None

    def write_tag(self, text: str, timeout: float = 0.1) -> Optional[bool]:
        """
        Try to write an NFC tag
        
        Args:
            timeout: Timeout in seconds for tag detection
            
        Returns:
            User ID as string if tag detected, None otherwise
        """
        if not self.writing or self.pn532 is None:
            return None
        
        try:
            # Try to write a tag (non-blocking)
            return self._write_secure_hmac(text, self.signer, timeout)
            
        except Exception as e:
            logger.error(f"Error writing NFC tag: {e}")
            return None


    def _write_ndef_text(self, text: str, timeout: float = 0.1) -> bool:
        """
        Write NDEF Text record to NFC tag (NTAG213/215/216)

        Args:
            text: Text to write into NFC tag

        Returns:
            True if success, False otherwise
        """
        if self.pn532 is None:
            logger.error("NFC reader not initialized")
            return False

        try:
            logger.info("Waiting for NFC tag to write...")
            uid = self.pn532.read_passive_target(timeout=timeout)

            if uid is None:
                logger.warning("No tag detected")
                return False

            logger.info(f"Tag detected, writing NDEF text: {text}")

            # Build NDEF Text record
            text_bytes = text.encode("utf-8")
            lang = b"en"

            payload = bytes([len(lang)]) + lang + text_bytes
            record = b"\xD1\x01" + bytes([len(payload)]) + b"T" + payload

            ndef_message = b"\x03" + bytes([len(record)]) + record + b"\xFE"

            # Pad to 4-byte blocks
            if len(ndef_message) % 4 != 0:
                ndef_message += b"\x00" * (4 - len(ndef_message) % 4)

            start_block = 4

            for i in range(0, len(ndef_message), 4):
                block_num = start_block + (i // 4)
                block_data = ndef_message[i:i + 4]

                logger.debug(f"Writing block {block_num}: {block_data.hex()}")
                self.pn532.ntag2xx_write_block(block_num, block_data)

            logger.info("NDEF text written successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to write NDEF: {e}")
            return False

    def _write_secure_hmac(self, text: str, hmac_signer: NFCHMAC, timeout: float = 0.1) -> bool:
        """
        Записать text + timestamp + HMAC на NFC метку
        """
        ts = int(time.time())
        payload_dict = {"uid": text, "ts": ts}

        # Генерируем HMAC для text + timestamp
        data_str = json.dumps(payload_dict, separators=(",", ":"))
        payload_dict["hmac"] = hmac_signer.generate(data_str)

        # Превращаем в JSON для записи на метку
        payload_json = json.dumps(payload_dict, separators=(",", ":"))

        return self._write_ndef_text(payload_json, timeout)

    def _read_ndef_text(self, timeout: float = 1.0) -> Optional[str]:
        """
        Read NDEF Text Record from NFC Forum Type 2 Tag

        Args:
            timeout: Timeout for tag detection in seconds

        Returns:
            Text if found, None otherwise
        """
        if self.pn532 is None:
            return None

        try:
            # 1️⃣ Дождаться появления метки
            uid = self.pn532.read_passive_target(timeout=timeout)
            if uid is None:
                return None  # Нет метки

            logger.debug(f"NFC tag detected: UID={' '.join(f'{b:02X}' for b in uid)}")

            # 2️⃣ Читать блоки NDEF
            data = b""
            block = 4  # NDEF начинается с блока 4
            for _ in range(32):  # читаем до 32 блоков (~128 байт)
                chunk = self.pn532.ntag2xx_read_block(block)
                if chunk is None:
                    break
                data += bytes(chunk)
                block += 1
                if b'\xFE' in chunk:
                    break

            if not data or data[0] != 0x03:
                logger.warning("No NDEF TLV found")
                return None

            length = data[1]
            ndef = data[2:2 + length]

            # 3️⃣ Парсинг NDEF Text Record
            if len(ndef) < 4 or ndef[0] != 0xD1:
                logger.warning("Not a valid NDEF Text record")
                return None

            type_length = ndef[1]
            payload_length = ndef[2]
            record_type = ndef[3:3 + type_length]
            if record_type != b"T":
                logger.warning("Record is not TEXT")
                return None

            payload = ndef[3 + type_length:3 + type_length + payload_length]
            lang_len = payload[0]
            text = payload[1 + lang_len:].decode("utf-8", errors="ignore")

            return text

        except Exception as e:
            logger.error(f"NDEF read failed: {e}")
            return None

    def _read_and_verify_hmac(self, hmac_signer: NFCHMAC) -> tuple[bool, str | None]:
        """
        Чтение NDEF с проверкой HMAC
        """
        text = self._read_ndef_text()
        if not text:
            return None, None

        try:
            payload = json.loads(text)
            data_str = json.dumps({"uid": payload["uid"], "ts": payload["ts"]}, separators=(",", ":"))

            if hmac_signer.verify(data_str, payload["hmac"]):
                return True, payload["uid"]

            return False, None

        except Exception:
            return False, None

    def cleanup(self):
        """Clean up resources"""
        self.stop_reading()
        
        if self.uart:
            try:
                self.uart.close()
                logger.info("UART closed")
            except Exception as e:
                logger.error(f"Error closing UART: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reader = NFCManager(config.NFC_UART_PORT, config.NFC_BAUDRATE)
    reader.initialize()
    reader.start_reading()
    
    print("Reading NFC tags... Press Ctrl+C to stop")
    
    try:
        while True:
            text = reader.read_tag()
            if text:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.cleanup()

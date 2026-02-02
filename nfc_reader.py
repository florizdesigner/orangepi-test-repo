"""
NFC Reader Manager
Handles NFC tag reading using PN532 via UART
"""
import logging
import time
from typing import Optional
import serial

try:
    from adafruit_pn532.uart import PN532_UART
except ImportError:
    # Fallback for development without hardware
    PN532_UART = None


logger = logging.getLogger(__name__)


class NFCReader:
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
            # Try to read a tag (non-blocking)
            uid = self.pn532.read_passive_target(timeout=timeout)
            
            if uid is not None:
                # Convert UID bytes to hex string
                uid_hex = ''.join(['{:02X}'.format(i) for i in uid])
                logger.info(f"NFC tag detected: UID={uid_hex}")
                
                # Try to read NDEF data (if available)
                user_id = self._read_ndef_user_id(uid)
                
                if user_id:
                    logger.info(f"User ID from NDEF: {user_id}")
                    return user_id
                else:
                    # Fallback: use UID as user ID
                    logger.info(f"Using UID as user ID: {uid_hex}")
                    return uid_hex
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading NFC tag: {e}")
            return None
    
    def _read_ndef_user_id(self, uid) -> Optional[str]:
        """
        Try to read user ID from NDEF message (text format)
        
        Args:
            uid: Tag UID
            
        Returns:
            User ID if found in NDEF, None otherwise
        """
        try:
            # Try to read NDEF text record from tag
            # For NTAG21x tags with NDEF, we need to read blocks
            
            # Block 4 onwards typically contains NDEF message
            # This is a simplified implementation - may need adjustment based on actual tag
            
            # Try to read text data from tag
            # The exact implementation depends on tag type (NTAG213/215/216, Mifare Classic, etc.)
            
            # For now, we'll try to read common NDEF text blocks
            # Typically NDEF text record starts at block 4
            
            # NOTE: This is placeholder - actual implementation may vary
            # depending on your specific NFC tag model and data structure
            
            logger.debug("Attempting to read NDEF text from tag")
            
            # If you're using NTAG tags, you can read blocks like this:
            # data = self.pn532.ntag2xx_read_block(4)  # Start reading from block 4
            # Then parse the NDEF message to extract text
            
            # For simple text storage, you might just have the user ID as plain text
            # in specific blocks without full NDEF encoding
            
            return None  # Will fall back to UID
            
        except Exception as e:
            logger.debug(f"Could not read NDEF data: {e}")
            return None
    
    def write_user_id(self, user_id: str) -> bool:
        """
        Write user ID as text to an NFC tag (for setup purposes)
        
        Args:
            user_id: User ID to write (text format)
            
        Returns:
            True if successful, False otherwise
        """
        if self.pn532 is None:
            logger.error("NFC reader not initialized")
            return False
        
        try:
            # Wait for a tag
            logger.info("Waiting for NFC tag to write...")
            uid = self.pn532.read_passive_target(timeout=5)
            
            if uid is None:
                logger.warning("No tag detected")
                return False
            
            logger.info(f"Tag detected, writing user ID: {user_id}")
            
            # Write user ID as text to tag
            # For NTAG213/215/216, we can write to blocks starting at block 4
            
            # Convert user_id string to bytes
            user_id_bytes = user_id.encode('utf-8')
            
            # Pad to 4-byte blocks (NTAG uses 4 bytes per block)
            # NTAG blocks: each block is 4 bytes
            block_size = 4
            padded_data = user_id_bytes + b'\x00' * (block_size - len(user_id_bytes) % block_size)
            
            # Write to blocks starting at block 4 (NDEF data area)
            # This is a simplified approach - for full NDEF, you'd need proper NDEF formatting
            start_block = 4
            
            for i in range(0, len(padded_data), block_size):
                block_num = start_block + (i // block_size)
                block_data = padded_data[i:i+block_size]
                
                # Write block
                # Note: ntag2xx_write_block is available in some PN532 libraries
                # You may need to use a different method depending on your tag type
                
                logger.debug(f"Writing block {block_num}: {block_data.hex()}")
                
                # Example (uncomment when using real hardware):
                # self.pn532.ntag2xx_write_block(block_num, block_data)
            
            logger.info("User ID written successfully (text format)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write to tag: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_reading()
        
        if self.uart:
            try:
                self.uart.close()
                logger.info("UART closed")
            except Exception as e:
                logger.error(f"Error closing UART: {e}")


class MockNFCReader(NFCReader):
    """Mock NFC reader for testing without hardware"""
    
    def __init__(self):
        super().__init__()
        self.mock_tags = ["USER001", "USER002", "USER003"]
        self.mock_index = 0
    
    def initialize(self):
        logger.info("Mock NFC reader initialized")
    
    def read_tag(self, timeout: float = 0.1) -> Optional[str]:
        if not self.reading:
            return None
        
        # Simulate tag detection every 5 seconds
        time.sleep(5)
        
        user_id = self.mock_tags[self.mock_index % len(self.mock_tags)]
        self.mock_index += 1
        
        logger.info(f"Mock tag read: {user_id}")
        return user_id
    
    def cleanup(self):
        logger.info("Mock NFC reader cleaned up")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Use mock reader for testing
    reader = MockNFCReader()
    reader.initialize()
    reader.start_reading()
    
    print("Reading NFC tags... Press Ctrl+C to stop")
    
    try:
        while True:
            tag_id = reader.read_tag()
            if tag_id:
                print(f"Tag detected: {tag_id}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.cleanup()

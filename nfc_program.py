#!/usr/bin/env python3
"""
NFC Tag Programming Utility
Tool for writing user IDs to NFC tags
"""
import logging
import sys
from nfc_reader import NFCReader, MockNFCReader
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def program_tag(user_id: str, use_mock: bool = False):
    """
    Program an NFC tag with a user ID
    
    Args:
        user_id: User ID to write to the tag
        use_mock: Use mock reader for testing
    """
    # Initialize NFC reader
    if use_mock:
        reader = MockNFCReader()
        logger.info("Using Mock NFC Reader")
    else:
        reader = NFCReader(config.NFC_UART_PORT, config.NFC_BAUDRATE)
    
    try:
        reader.initialize()
        logger.info(f"Programming NFC tag with user ID: {user_id}")
        
        success = reader.write_user_id(user_id)
        
        if success:
            logger.info("✓ Tag programmed successfully!")
            return True
        else:
            logger.error("✗ Failed to program tag")
            return False
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
    finally:
        reader.cleanup()


def read_tag_info(use_mock: bool = False):
    """
    Read and display information from an NFC tag
    
    Args:
        use_mock: Use mock reader for testing
    """
    # Initialize NFC reader
    if use_mock:
        reader = MockNFCReader()
        logger.info("Using Mock NFC Reader")
    else:
        reader = NFCReader(config.NFC_UART_PORT, config.NFC_BAUDRATE)
    
    try:
        reader.initialize()
        reader.start_reading()
        
        logger.info("Place an NFC tag near the reader...")
        
        # Wait for tag
        import time
        timeout = 10
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            user_id = reader.read_tag(timeout=0.5)
            
            if user_id:
                logger.info(f"✓ Tag detected!")
                logger.info(f"  User ID: {user_id}")
                return user_id
            
            time.sleep(0.1)
        
        logger.warning("No tag detected within timeout")
        return None
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return None
    finally:
        reader.cleanup()


def main():
    """Main function"""
    print("=" * 60)
    print("NFC Tag Programming Utility")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Program tag:  python3 nfc_program.py write <user_id>")
        print("  Read tag:     python3 nfc_program.py read")
        print()
        print("Examples:")
        print("  python3 nfc_program.py write USER001")
        print("  python3 nfc_program.py read")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    use_mock = config.USE_MOCK_NFC
    
    if command == "write":
        if len(sys.argv) < 3:
            print("Error: User ID required")
            print("Usage: python3 nfc_program.py write <user_id>")
            sys.exit(1)
        
        user_id = sys.argv[2]
        
        print(f"Programming tag with User ID: {user_id}")
        print()
        
        success = program_tag(user_id, use_mock)
        
        if success:
            print()
            print("✓ SUCCESS: Tag programmed")
            sys.exit(0)
        else:
            print()
            print("✗ FAILED: Could not program tag")
            sys.exit(1)
    
    elif command == "read":
        print("Reading tag information...")
        print()
        
        user_id = read_tag_info(use_mock)
        
        if user_id:
            print()
            print("✓ SUCCESS: Tag read")
            sys.exit(0)
        else:
            print()
            print("✗ FAILED: Could not read tag")
            sys.exit(1)
    
    else:
        print(f"Error: Unknown command '{command}'")
        print("Valid commands: write, read")
        sys.exit(1)


if __name__ == "__main__":
    main()

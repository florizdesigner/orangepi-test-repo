#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import serial
from PIL import Image, ImageDraw, ImageFont
import time
import epaper

# ===== Settings =====
UART_PORT = '/dev/serial0'  # UART port for PN532
BAUDRATE = 115200

# Dictionary of tags and associated information
NFC_DATABASE = {
    '04A1B2C3D4E5F6': 'Office Key\nAccess: Administrator',
    '04B2C3D4E5F6A1': 'Employee Pass\nJohn Smith',
    '04C3D4E5F6A1B2': 'Access Card\nWarehouse #3',
}

# ===== PN532 Class =====
class PN532_UART:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)
        self.wake_up()
        self.SAM_configuration()
    
    def wake_up(self):
        """Wake up the module"""
        self.serial.write(b'\x55\x55\x00\x00\x00')
        time.sleep(0.1)
        self.serial.reset_input_buffer()
    
    def send_command(self, command):
        """Send command to PN532"""
        frame = self._build_frame(command)
        self.serial.write(frame)
        time.sleep(0.1)
        return self._read_response()
    
    def _build_frame(self, data):
        """Build command frame"""
        length = len(data) + 1
        lcs = (~length + 1) & 0xFF
        dcs = (~sum(data) + 1) & 0xFF
        
        frame = bytearray([0x00, 0x00, 0xFF, length, lcs])
        frame.extend([0xD4])
        frame.extend(data)
        frame.append(dcs)
        frame.append(0x00)
        
        return bytes(frame)
    
    def _read_response(self):
        """Read response from PN532"""
        response = self.serial.read(64)
        return response
    
    def SAM_configuration(self):
        """Configure SAM"""
        self.send_command([0x14, 0x01, 0x00, 0x00])
    
    def read_passive_target(self):
        """Read passive target (ISO14443A)"""
        response = self.send_command([0x4A, 0x01, 0x00])
        print("Response from read_passive_target: " + response)
        
        if len(response) > 20 and response[0:6] == b'\x00\x00\xFF':
            # Extract UID
            uid_length = response[12]
            uid = response[13:13 + uid_length]
            return binascii.hexlify(uid).decode('utf-8').upper()
        
        return None

# ===== E-ink Display Class =====
# Replace with your specific display library
# For example, for Waveshare use their libraries

class EinkDisplay:
    def __init__(self):
        """
        Initialize display
        For specific model use corresponding library:
        - Waveshare: from waveshare_epd import epd2in13_V2
        - Pimoroni: import inky
        """
        self.width = 400
        self.height = 168
        
        # Пример для Waveshare (раскомментируйте и адаптируйте):
#!/usr/bin/env python3
        self.epd = epaper.epaper('epd3in0g').EPD()
        self.epd.init()
        self.epd.Clear(0xFF)
    
    def display_text(self, text, title="NFC Scanner"):
        """Display text on screen"""
        # Create image
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Load fonts (can use system fonts)
        try:
            font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
            font_text = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        # Draw title
        draw.text((10, 10), title, font=font_title, fill=0)
        draw.line((10, 35, self.width - 10, 35), fill=0, width=2)
        
        # Draw main text
        y_position = 50
        for line in text.split('\n'):
            draw.text((10, y_position), line, font=font_text, fill=0)
            y_position += 20
        
        # Display on screen
        # For Waveshare:
        # self.epd.display(self.epd.getbuffer(image))
        
        # For testing, save as image
        image.save('/tmp/nfc_display.png')
        print(f"Image saved to /tmp/nfc_display.png")
        print(f"Title: {title}")
        print(f"Text:\n{text}")
    
    def clear(self):
        """Clear display"""
        # self.epd.Clear(0xFF)
        pass

# ===== Main Program =====
def main():
    print("Initializing NFC reader and display...")
    
    # Initialize devices
    try:
        nfc = PN532_UART(UART_PORT, BAUDRATE)
        display = EinkDisplay()
        print("✓ Devices initialized successfully")
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return
    
    # Display welcome message
    display.display_text("Please present\nNFC tag", "Ready")
    
    print("\nWaiting for NFC tag...")
    last_uid = None
    
    while True:
        try:
            # Try to read tag
            uid = nfc.read_passive_target()
            
            
            if uid and uid != last_uid:
                print(f"\n✓ Tag detected: {uid}")
                last_uid = uid
                
                # Search for tag information
                if uid in NFC_DATABASE:
                    info = NFC_DATABASE[uid]
                    print(f"  Information: {info.replace(chr(10), ' | ')}")
                    display.display_text(info, f"Tag: {uid[:8]}...")
                else:
                    info = f"Unknown tag\nUID: {uid}"
                    print(f"  {info}")
                    display.display_text(info, "Not in database")
                
                # Wait for tag removal
                time.sleep(2)
            
            elif not uid and last_uid:
                # Tag removed
                print("Tag removed")
                last_uid = None
                display.display_text("Please present\nNFC tag", "Ready")
            
            time.sleep(0.3)
            
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            display.clear()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
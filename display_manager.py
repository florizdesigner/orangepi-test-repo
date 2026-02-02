"""
Display Manager for Waveshare E-ink Display
Handles display operations via SPI
"""
import logging
import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import config

try:
    # Try to import Waveshare library
    # For 400x168 display, typically epd3in7 (3.7 inch)
    from waveshare_epd import epd3in7
    EPD = epd3in7.EPD()
except ImportError:
    EPD = None
    logging.warning("Waveshare EPD library not found, using mock display")


logger = logging.getLogger(__name__)


class DisplayManager:
    """Manager for Waveshare E-ink display"""
    
    def __init__(self, display_model: str = None):
        """
        Initialize display manager
        
        Args:
            display_model: Waveshare display model (e.g., 'epd3in7')
        """
        self.display_model = display_model or config.DISPLAY_MODEL
        self.epd = None
        
        # Use dimensions from config (400x168 pixels)
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        
        self.initialized = False
        
        # Font settings
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        self.font_size_normal = 20
        self.font_size_large = 28
    
    def initialize(self):
        """Initialize the E-ink display"""
        if EPD is None:
            logger.warning("Using mock display - EPD library not available")
            self.initialized = True
            return
        
        try:
            # Initialize display
            self.epd = EPD
            self.epd.init()
            
            # Get display dimensions
            self.width = self.epd.width
            self.height = self.epd.height
            
            logger.info(f"E-ink display initialized: {self.width}x{self.height}")
            
            # Clear display
            self.epd.Clear()
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            raise
    
    def show_image(self, image_path: str):
        """
        Display an image from file
        
        Args:
            image_path: Path to image file
        """
        if not self.initialized:
            logger.error("Display not initialized")
            return
        
        try:
            # Load and prepare image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                self.show_text(f"Image not found:\n{os.path.basename(image_path)}")
                return
            
            # Open and resize image
            image = Image.open(image_path)
            
            # Convert to 1-bit (black/white)
            if image.mode != '1':
                image = image.convert('1')
            
            # Resize to fit display
            image = image.resize((self.width, self.height), Image.LANCZOS)
            
            logger.info(f"Displaying image: {image_path}")
            
            if self.epd:
                # Display on real hardware
                self.epd.display(self.epd.getbuffer(image))
            else:
                # Mock display
                logger.info(f"[MOCK DISPLAY] Showing image: {image_path}")
            
        except Exception as e:
            logger.error(f"Failed to display image: {e}")
    
    def show_text(self, text: str, font_size: Optional[int] = None, align: str = "center"):
        """
        Display text on screen
        
        Args:
            text: Text to display
            font_size: Font size (default: normal size)
            align: Text alignment ('left', 'center', 'right')
        """
        if not self.initialized:
            logger.error("Display not initialized")
            return
        
        try:
            # Create blank image
            image = Image.new('1', (self.width, self.height), 255)  # 255 = white
            draw = ImageDraw.Draw(image)
            
            # Load font
            if font_size is None:
                font_size = self.font_size_normal
            
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except OSError:
                logger.warning(f"Font not found: {self.font_path}, using default")
                font = ImageFont.load_default()
            
            # Handle multi-line text
            lines = text.split('\n')
            
            # Calculate text positioning
            y_offset = 20
            line_spacing = 10
            
            for line in lines:
                # Get text bounding box
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Calculate x position based on alignment
                if align == "center":
                    x = (self.width - text_width) // 2
                elif align == "right":
                    x = self.width - text_width - 10
                else:  # left
                    x = 10
                
                # Draw text
                draw.text((x, y_offset), line, font=font, fill=0)  # 0 = black
                
                y_offset += text_height + line_spacing
            
            logger.info(f"Displaying text: {text[:50]}...")
            
            if self.epd:
                # Display on real hardware
                self.epd.display(self.epd.getbuffer(image))
            else:
                # Mock display
                logger.info(f"[MOCK DISPLAY] Text:\n{text}")
            
        except Exception as e:
            logger.error(f"Failed to display text: {e}")
    
    def clear(self):
        """Clear the display"""
        if not self.initialized:
            return
        
        try:
            if self.epd:
                self.epd.Clear()
            logger.info("Display cleared")
        except Exception as e:
            logger.error(f"Failed to clear display: {e}")
    
    def sleep(self):
        """Put display in sleep mode to save power"""
        if not self.initialized or not self.epd:
            return
        
        try:
            self.epd.sleep()
            logger.info("Display in sleep mode")
        except Exception as e:
            logger.error(f"Failed to put display to sleep: {e}")
    
    def cleanup(self):
        """Clean up display resources"""
        if not self.initialized:
            return
        
        try:
            if self.epd:
                self.epd.sleep()
                # Some displays require exit
                if hasattr(self.epd, 'exit'):
                    self.epd.exit()
            
            logger.info("Display cleaned up")
            
        except Exception as e:
            logger.error(f"Error during display cleanup: {e}")


class MockDisplayManager(DisplayManager):
    """Mock display manager for testing without hardware"""
    
    def __init__(self):
        super().__init__()
        # Use config dimensions
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
    
    def initialize(self):
        logger.info("[MOCK] Display initialized")
        self.initialized = True
    
    def show_image(self, image_path: str):
        logger.info(f"[MOCK DISPLAY] Image: {image_path}")
    
    def show_text(self, text: str, font_size: Optional[int] = None, align: str = "center"):
        logger.info(f"[MOCK DISPLAY] Text ({align}):\n{text}")
    
    def clear(self):
        logger.info("[MOCK DISPLAY] Cleared")
    
    def sleep(self):
        logger.info("[MOCK DISPLAY] Sleep mode")
    
    def cleanup(self):
        logger.info("[MOCK DISPLAY] Cleaned up")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Use mock display for testing
    display = MockDisplayManager()
    display.initialize()
    
    # Test text display
    display.show_text("Hello, World!\nThis is a test")
    
    import time
    time.sleep(2)
    
    # Test image display
    display.show_image("/media/velow.png")
    
    time.sleep(2)
    
    # Cleanup
    display.cleanup()

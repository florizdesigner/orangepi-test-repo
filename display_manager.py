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
    from waveshare_epd import epd3in0g
    EPD = epd3in0g.EPD()
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
        
        # Image cache to avoid reloading
        self._image_cache = {}
        
        # Last displayed content (for partial updates)
        self._last_image = None
    
    def initialize(self):
        """Initialize the E-ink display"""
        if EPD is None:
            logger.warning("Using mock display - EPD library not available")
            self.initialized = True
            return
        
        try:
            # Initialize display
            self.epd = EPD
            
            logger.info("Initializing E-ink display (this may take a few seconds)...")
            self.epd.init()
            
            # Get display dimensions
            self.width = self.epd.width
            self.height = self.epd.height
            
            logger.info(f"E-ink display initialized: {self.width}x{self.height}")
            
            # Clear display once
            logger.info("Clearing display...")
            self.epd.Clear()
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            raise
    
    def _load_and_prepare_image(self, image_path: str) -> Optional[Image.Image]:
        """
        Load and prepare image with caching
        
        Args:
            image_path: Path to image file
            
        Returns:
            Prepared PIL Image or None
        """
        # Check cache first
        if image_path in self._image_cache:
            logger.debug(f"Using cached image: {image_path}")
            return self._image_cache[image_path].copy()
        
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Open image
            image = Image.open(image_path)
            
            # Convert to 1-bit (black/white)
            if image.mode != '1':
                image = image.convert('1')
            
            # Resize to fit display in landscape orientation (400x168)
            image.thumbnail((self.width, self.height), Image.LANCZOS)
            
            # Create a white background of exact display size
            background = Image.new('1', (self.width, self.height), 255)
            
            # Center the image on the background
            x_offset = (self.width - image.width) // 2
            y_offset = (self.height - image.height) // 2
            background.paste(image, (x_offset, y_offset))
            
            # Cache the prepared image
            self._image_cache[image_path] = background.copy()
            
            return background
            
        except Exception as e:
            logger.error(f"Failed to prepare image: {e}")
            return None
    
    def show_image(self, image_path: str, fast_update: bool = False):
        """
        Display an image from file
        
        Args:
            image_path: Path to image file
            fast_update: Use fast/partial update mode (faster but lower quality)
        """
        if not self.initialized:
            logger.error("Display not initialized")
            return
        
        # Load and prepare image
        background = self._load_and_prepare_image(image_path)
        if background is None:
            self.show_text(f"Image not found:\n{os.path.basename(image_path)}")
            return
        
        logger.info(f"Displaying image: {image_path} (landscape, fast={fast_update})")
        
        if self.epd:
            try:
                if fast_update and hasattr(self.epd, 'displayPartial'):
                    # Fast partial update (if supported)
                    logger.debug("Using partial update mode")
                    self.epd.displayPartial(self.epd.getbuffer(background))
                else:
                    # Full update (slower but higher quality)
                    self.epd.display(self.epd.getbuffer(background))
                    
                self._last_image = background
            except Exception as e:
                logger.error(f"Display update failed: {e}")
        else:
            # Mock display
            logger.info(f"[MOCK DISPLAY] Showing image: {image_path} (400x168 landscape)")
    
    def show_text(self, text: str, font_size: Optional[int] = None, 
                  align: str = "center", fast_update: bool = False):
        """
        Display text on screen in landscape orientation
        Text is always centered both horizontally and vertically
        
        Args:
            text: Text to display
            font_size: Font size (default: normal size)
            align: Text alignment ('left', 'center', 'right') - only affects horizontal
            fast_update: Use fast/partial update mode (faster but lower quality)
        """
        if not self.initialized:
            logger.error("Display not initialized")
            return
        
        try:
            # Create blank image for landscape orientation (400x168)
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
            
            # Calculate dimensions for each line
            line_heights = []
            line_widths = []
            
            for line in lines:
                if line:  # Skip empty lines for measurement
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_width = bbox[2] - bbox[0]
                    line_height = bbox[3] - bbox[1]
                else:
                    line_width = 0
                    line_height = font_size  # Approximate height for empty lines
                
                line_widths.append(line_width)
                line_heights.append(line_height)
            
            # Line spacing
            line_spacing = 10
            
            # Calculate total height
            total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)
            
            # Start Y position - CENTERED VERTICALLY
            y_offset = (self.height - total_text_height) // 2
            
            # Draw each line
            for i, line in enumerate(lines):
                text_width = line_widths[i]
                text_height = line_heights[i]
                
                # Calculate X position - CENTERED HORIZONTALLY by default
                if align == "left":
                    x = 10
                elif align == "right":
                    x = self.width - text_width - 10
                else:  # center (default)
                    x = (self.width - text_width) // 2
                
                # Draw text (skip empty lines)
                if line:
                    draw.text((x, y_offset), line, font=font, fill=0)  # 0 = black
                
                y_offset += text_height + line_spacing
            
            logger.info(f"Displaying text (centered, landscape 400x168, fast={fast_update}): {text[:50]}...")
            
            if self.epd:
                try:
                    if fast_update and hasattr(self.epd, 'displayPartial'):
                        # Fast partial update
                        logger.debug("Using partial update mode")
                        self.epd.displayPartial(self.epd.getbuffer(image))
                    else:
                        # Full update
                        self.epd.display(self.epd.getbuffer(image))
                        
                    self._last_image = image
                except Exception as e:
                    logger.error(f"Display update failed: {e}")
            else:
                # Mock display
                logger.info(f"[MOCK DISPLAY] Text (centered, landscape 400x168):\n{text}")
            
        except Exception as e:
            logger.error(f"Failed to display text: {e}")
    
    def clear(self):
        """Clear the display"""
        if not self.initialized:
            return
        
        try:
            if self.epd:
                logger.info("Clearing display (this takes a few seconds)...")
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
            
            # Clear cache
            self._image_cache.clear()
            
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
        logger.info("[MOCK] Display initialized (400x168 landscape)")
        self.initialized = True
    
    def show_image(self, image_path: str, fast_update: bool = False):
        logger.info(f"[MOCK DISPLAY] Image: {image_path} (fast={fast_update})")
    
    def show_text(self, text: str, font_size: Optional[int] = None, 
                  align: str = "center", fast_update: bool = False):
        logger.info(f"[MOCK DISPLAY] Text (CENTERED, fast={fast_update}):\n--- START ---\n{text}\n--- END ---")
    
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
    
    # Test text display (centered by default)
    display.show_text("Hello, World!\nThis is a test", fast_update=False)
    
    import time
    time.sleep(2)
    
    # Test multi-line centered text
    display.show_text("Velow Cycling Club\n\nСистема регистрации", fast_update=True)
    
    time.sleep(2)
    
    # Cleanup
    display.cleanup()
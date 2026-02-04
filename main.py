"""
NFC Registration System
Main application file with state machine logic
"""
import time
import logging
import os
from enum import Enum
from typing import Optional

from api_client import VelowAPIClient
from nfc_reader import NFCReader
from display_manager import DisplayManager
import config

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available - button functionality disabled")


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class AppState(Enum):
    """Application states"""
    IDLE = "idle"
    WAITING_NFC = "waiting_nfc"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"


class NFCRegistrationApp:
    """Main application class managing the NFC registration flow"""
    
    def __init__(self):
        """Initialize the application"""
        # Initialize API client with authentication
        self.api_client = VelowAPIClient(
            config.API_BASE_URL,
            username=config.API_USERNAME,
            password=config.API_PASSWORD,
            bearer_token=config.API_TOKEN
        )
        
        # Инициализация NFC-ридера и дисплея
        self.nfc_reader = NFCReader(config.NFC_UART_PORT, config.NFC_BAUDRATE)
        self.display = DisplayManager(config.DISPLAY_MODEL)
        

        self.state = AppState.IDLE
        self.active_event_id: Optional[int] = None
        self.running = True
        self.start_button_pressed = False
        self.stop_button_pressed = False
        
        # Setup buttons if GPIO available
        self.buttons_enabled = False
        if GPIO_AVAILABLE:
            try:
                GPIO.setmode(GPIO.BOARD)
                
                GPIO.setup(config.BUTTON_START_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    config.BUTTON_START_PIN,
                    GPIO.FALLING,
                    callback=self._start_button_callback,
                    bouncetime=config.BUTTON_BOUNCE_TIME
                )
                
                GPIO.setup(config.BUTTON_STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    config.BUTTON_STOP_PIN,
                    GPIO.FALLING,
                    callback=self._stop_button_callback,
                    bouncetime=config.BUTTON_BOUNCE_TIME
                )
                
                self.buttons_enabled = True
                logger.info(f"Buttons initialized: Start=GPIO{config.BUTTON_START_PIN} (Pin 31), Stop=GPIO{config.BUTTON_STOP_PIN} (Pin 33)")
            except Exception as e:
                logger.warning(f"Failed to initialize buttons: {e}")
    
    # TODO: переделать все на одну кнопку с инверсией состояния

    def _start_button_callback(self, channel):
        """Callback for start button press"""
        logger.info("Start button pressed!")
        self.start_button_pressed = True
    
    def _stop_button_callback(self, channel):
        """Callback for stop button press"""
        logger.info("Stop button pressed!")
        self.stop_button_pressed = True
        
    def initialize(self):
        """Initialize all hardware components"""
        logger.info("Initializing application...")
        
        try:
            self.display.initialize()
            self.nfc_reader.initialize()
            logger.info("Hardware initialization successful")
            return True
        except Exception as e:
            logger.error(f"Hardware initialization failed: {e}")
            return False
    
    def get_active_event(self) -> Optional[int]:
        """
        Get the currently active event ID
        
        Returns:
            Event ID if found, None otherwise
        """
        try:
            events = self.api_client.get_events()
            
            # Filter for IN_ACTIVE events
            active_events = [e for e in events if e.get('status') == 'IN_ACTIVE']
            
            if not active_events:
                logger.warning("No active events found")
                return None
            
            if len(active_events) > 1:
                logger.warning(f"Multiple active events found: {len(active_events)}, using first")
            
            event_id = active_events[0].get('id')
            logger.info(f"Active event found: ID={event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to get active event: {e}")
            return None
    
    def process_nfc_tag(self, user_id: str):
        """
        Process scanned NFC tag with user ID
        
        Args:
            user_id: User ID read from NFC tag
        """
        logger.info(f"Processing NFC tag for user ID: {user_id}")
        
        # Show processing screen (fast update for temporary message)
        self.display.show_text("Пожалуйста, подождите...")
        
        # Check for active event
        if self.active_event_id is None:
            self.active_event_id = self.get_active_event()
            
            if self.active_event_id is None:
                self.display.show_text("Упс! Активных эвентов нет")
                time.sleep(config.MESSAGE_DISPLAY_TIME)
                self.state = AppState.WAITING_NFC
                self.display.show_text("Приложите ваш NFC-брелок")
                return
        
        # Get user info
        try:
            user = self.api_client.get_user(user_id)
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                self.display.show_text("Пользователь не найден")
                time.sleep(config.MESSAGE_DISPLAY_TIME)
                self.state = AppState.WAITING_NFC
                self.display.show_text("Приложите ваш NFC-брелок")
                return
            
            user_name = user.get('name', 'Unknown')
            logger.info(f"User found: {user_name}")
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            self.display.show_text("Упс! Что-то пошло не так")
            time.sleep(config.MESSAGE_DISPLAY_TIME)
            self.state = AppState.WAITING_NFC
            self.display.show_text("Приложите ваш NFC-брелок")
            return
        
        # Finish event registration
        try:
            result = self.api_client.finish_event(self.active_event_id, user_id)
            
            if result:
                logger.info(f"Registration successful for user: {user_name}")
                self.display.show_text(f"✓ Регистрация для пользователя {user_name} завершена")
                self.state = AppState.SUCCESS
            else:
                logger.error(f"Registration failed for user: {user_name}")
                self.display.show_text(f"{user_name}, упс! Что-то пошло не так")
                self.state = AppState.ERROR
                
        except Exception as e:
            logger.error(f"Failed to finish event: {e}")
            self.display.show_text(f"{user_name}, упс! Что-то пошло не так")
            self.state = AppState.ERROR
        
        # Return to waiting state after delay
        time.sleep(config.MESSAGE_DISPLAY_TIME)
        self.state = AppState.WAITING_NFC
        self.display.show_text("Приложите ваш NFC-брелок")
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            logger.error("Failed to initialize, exiting")
            return
        
        # Show welcome screen with text (instead of logo)
        self.display.show_text(config.WELCOME_TEXT, fast_update=False)
        self.state = AppState.IDLE
        
        logger.info("Application started")
        
        if self.buttons_enabled:
            logger.info("Waiting for START button press (GPIO{}, Pin 31) to begin scanning...".format(config.BUTTON_START_PIN))
        else:
            logger.info("Buttons not available - auto-starting in 3 seconds...")
            time.sleep(3)
            self.start_scanning()
        
        try:
            while self.running:
                # Handle start button press
                if self.start_button_pressed:
                    self.start_button_pressed = False
                    
                    if self.state == AppState.IDLE:
                        # Start scanning
                        self.start_scanning()
                
                # Handle stop button press
                if self.stop_button_pressed:
                    self.stop_button_pressed = False
                    
                    if self.state == AppState.WAITING_NFC:
                        # Stop scanning
                        self.stop_scanning()
                
                # Handle NFC reading
                if self.state == AppState.WAITING_NFC:
                    user_id = self.nfc_reader.read_tag(config.NFC_READ_TIMEOUT)
                    
                    if user_id:
                        self.state = AppState.PROCESSING
                        self.process_nfc_tag(user_id)
                
                # Small delay to prevent CPU spinning
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        finally:
            self.cleanup()
    
    def start_scanning(self):
        """Start NFC scanning mode"""
        logger.info("Starting NFC scanning...")
        self.display.show_text("Приложите ваш NFC-брелок")
        self.state = AppState.WAITING_NFC
        self.nfc_reader.start_reading()
        
        # Get active event on start
        self.active_event_id = self.get_active_event()
    
    def stop_scanning(self):
        """Stop NFC scanning mode"""
        logger.info("Stopping NFC scanning...")
        self.nfc_reader.stop_reading()
        self.state = AppState.IDLE
        # Show welcome text (full update for better quality)
        self.display.show_text(config.WELCOME_TEXT, fast_update=False)
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        self.nfc_reader.cleanup()
        self.display.cleanup()
        
        # Cleanup GPIO
        if GPIO_AVAILABLE and self.buttons_enabled:
            try:
                GPIO.cleanup()
                logger.info("GPIO cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up GPIO: {e}")


if __name__ == "__main__":
    # Create and run application (config is loaded from config.py)
    app = NFCRegistrationApp()
    app.run()
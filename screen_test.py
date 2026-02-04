#!/usr/bin/env python3
"""
Quick E-ink Display Test
Simple script to quickly test the display with random messages
"""

import time
import random
import sys

# Add parent directory to path to import modules
sys.path.insert(0, '.')

from display_manager import DisplayManager
import config

# Test messages
MESSAGES = [
    "Velow Cycling Club",
    "Приложите\nNFC-брелок",
    "Пожалуйста,\nподождите...",
    "✓ Успех!",
    "Тест дисплея",
    "Hello World",
    "Привет Мир",
    "1 2 3 4 5",
    "Test\nDisplay\nWorking",
    "Работает!",
]

print("=" * 50)
print("Quick E-ink Display Test")
print("=" * 50)

display = DisplayManager(config.DISPLAY_MODEL)

try:
    # Initialize
    print("Initializing display...")
    display.initialize()
    print("✓ Display ready!\n")
    
    print(f"Will show {len(MESSAGES)} different random messages")
    print("Changing every 3 seconds")
    print("Press Ctrl+C to stop\n")
    print("-" * 50)
    
    count = 0
    while True:
        # Pick random message
        message = random.choice(MESSAGES)
        count += 1
        
        print(f"\n[{count}] Showing: '{message.replace(chr(10), ' / ')}'")
        
        # Display with fast update
        display.show_text(message, fast_update=True)
        
        print("Waiting 3 seconds...")
        time.sleep(3)

except KeyboardInterrupt:
    print(f"\n\n✓ Test stopped. Total messages shown: {count}")

except Exception as e:
    print(f"\n✗ Error: {e}")

finally:
    print("\nCleaning up...")
    display.cleanup()
    print("Done!\n")
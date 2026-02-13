#!/usr/bin/env python3
"""
API Testing Utility
Tool for testing the Velow Cycling Club API
"""
import logging
import sys
from core.api_client import VelowAPIClient
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_get_events(client):
    """Test getting events"""
    print("\n" + "=" * 60)
    print("Testing: GET /api/events")
    print("=" * 60)
    
    events = client.get_events()
    
    if events:
        print(f"✓ Found {len(events)} events:")
        for event in events:
            event_id = event.get('id', 'N/A')
            name = event.get('name', 'N/A')
            status = event.get('status', 'N/A')
            print(f"  - ID: {event_id}, Name: {name}, Status: {status}")
    else:
        print("✗ No events found or request failed")
    
    return events


def test_get_active_events(client):
    """Test getting active events"""
    print("\n" + "=" * 60)
    print("Testing: GET /api/events?status=IN_ACTIVE")
    print("=" * 60)
    
    events = client.get_events(status='IN_ACTIVE')
    
    if events:
        print(f"✓ Found {len(events)} active events:")
        for event in events:
            event_id = event.get('id', 'N/A')
            name = event.get('name', 'N/A')
            print(f"  - ID: {event_id}, Name: {name}")
    else:
        print("✗ No active events found")
    
    return events


def test_get_user(client, user_id):
    """Test getting user"""
    print("\n" + "=" * 60)
    print(f"Testing: GET /api/users/{user_id}")
    print("=" * 60)
    
    user = client.get_user(user_id)
    
    if user:
        user_name = user.get('name', 'N/A')
        user_email = user.get('email', 'N/A')
        print(f"✓ User found:")
        print(f"  - ID: {user_id}")
        print(f"  - Name: {user_name}")
        print(f"  - Email: {user_email}")
    else:
        print(f"✗ User not found: {user_id}")
    
    return user


def test_finish_event(client, event_id, user_id):
    """Test finishing event registration"""
    print("\n" + "=" * 60)
    print(f"Testing: POST /api/events/finish/{event_id}")
    print(f"User ID: {user_id}")
    print("=" * 60)
    
    success = client.finish_event(event_id, user_id)
    
    if success:
        print("✓ Event registration finished successfully")
    else:
        print("✗ Failed to finish event registration")
    
    return success


def main():
    """Main function"""
    print("=" * 60)
    print("Velow Cycling Club API Test Utility")
    print("=" * 60)
    print(f"\nAPI Base URL: {config.API_BASE_URL}")
    
    # Check if credentials are configured
    if config.API_USERNAME and config.API_PASSWORD:
        print(f"Authentication: Username/Password")
    elif config.API_TOKEN:
        print(f"Authentication: Bearer Token")
    else:
        print("WARNING: No authentication configured!")
        print("Please set API_USERNAME and API_PASSWORD in .env file")
    
    print()
    
    # Create API client
    client = VelowAPIClient(
        config.API_BASE_URL,
        username=config.API_USERNAME,
        password=config.API_PASSWORD,
        bearer_token=config.API_TOKEN
    )
    
    try:
        # Test 1: Get all events
        all_events = test_get_events(client)
        
        # Test 2: Get active events
        active_events = test_get_active_events(client)
        
        # Test 3: Get user (if user_id provided)
        if len(sys.argv) > 1:
            user_id = sys.argv[1]
            user = test_get_user(client, user_id)
            
            # Test 4: Finish event (if user found and active event exists)
            if user and active_events:
                event_id = active_events[0].get('id')
                
                print("\n" + "=" * 60)
                print("WARNING: The next test will actually register the user!")
                print("=" * 60)
                response = input("Continue? (yes/no): ")
                
                if response.lower() == 'yes':
                    test_finish_event(client, event_id, user_id)
                else:
                    print("Skipped event finish test")
        else:
            print("\n" + "=" * 60)
            print("To test user lookup and event finish:")
            print("Usage: python3 test_api.py <user_id>")
            print("=" * 60)
        
        print("\n" + "=" * 60)
        print("All tests completed")
        print("=" * 60)
        
    finally:
        client.close()


if __name__ == "__main__":
    main()

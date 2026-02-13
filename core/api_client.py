"""
API Client for Velow Cycling Club Backend
Handles all HTTP communication with the backend API

Usage:
    from api_client import VelowAPIClient
    import config
    
    # Initialize client with config credentials
    client = VelowAPIClient(
        config.API_BASE_URL,
        username=config.API_USERNAME,
        password=config.API_PASSWORD,
        bearer_token=config.API_TOKEN
    )
    
    # Use the client
    events = client.get_events()
    user = client.get_user("123")
    
    # Close when done
    client.close()
"""
import requests
import logging
from typing import Optional, List, Dict, Any


logger = logging.getLogger(__name__)


class VelowAPIClient:
    """Client for interacting with Velow Cycling Club API"""
    
    def __init__(self, base_url: str, username: Optional[str] = None, 
                 password: Optional[str] = None, bearer_token: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for the API (e.g., https://api.velowcyclingclub.ru/v3)
            username: Username for authentication
            password: Password for authentication
            bearer_token: Optional pre-existing bearer token (skips auth if provided)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.bearer_token = bearer_token
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Authenticate if credentials provided and no token
        if not bearer_token and username and password:
            self.authenticate()
        elif bearer_token:
            self._set_bearer_token(bearer_token)
    
    def _set_bearer_token(self, token: str):
        """Set bearer token in session headers"""
        self.bearer_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        logger.info("Bearer token set")
    
    def authenticate(self) -> bool:
        """
        Authenticate with username and password to get bearer token
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not self.username or not self.password:
            logger.error("Username or password not provided")
            return False
        
        url = f"{self.base_url}/api/users/auth"
        
        # Prepare authentication payload
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            logger.debug(f"POST {url}")
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                auth_data = response.json()
                
                # Extract token from response
                # Adjust this based on actual API response structure
                token = auth_data.get('token') or auth_data.get('access_token')
                
                if token:
                    self._set_bearer_token(token)
                    logger.info("Authentication successful")
                    return True
                else:
                    logger.error("No token in authentication response")
                    return False
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication request failed: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        url = f"{self.base_url}/api/users/{user_id}"
        
        try:
            logger.debug(f"GET {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"User retrieved successfully: {user_id}")
                return user_data
            elif response.status_code == 404:
                logger.warning(f"User not found: {user_id}")
                return None
            else:
                logger.error(f"Failed to get user: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_events(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of events
        
        Args:
            status: Optional status filter (e.g., 'IN_ACTIVE')
            
        Returns:
            List of event objects
        """
        url = f"{self.base_url}/api/events"
        params = {}
        
        if status:
            params['status'] = status
        
        try:
            logger.debug(f"GET {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                logger.info(f"Retrieved {len(events)} events")
                return events
            else:
                logger.error(f"Failed to get events: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return []
    
    def finish_event(self, event_id: int, user_id: str) -> bool:
        """
        Finish event registration for a user
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/events/finish/{event_id}"
        
        # Prepare request body
        payload = {
            "userId": user_id
        }
        
        try:
            logger.debug(f"POST {url} with payload: {payload}")
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Event finished successfully: event_id={event_id}, user_id={user_id}")
                return True
            else:
                logger.error(f"Failed to finish event: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False
    
    def close(self):
        """Close the session"""
        self.session.close()


# Example usage
if __name__ == "__main__":
    import config
    
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)
    
    # Create client with authentication from config
    client = VelowAPIClient(
        config.API_BASE_URL,
        username=config.API_USERNAME,
        password=config.API_PASSWORD,
        bearer_token=config.API_TOKEN
    )
    
    # Test get events
    print("\n=== Testing get_events ===")
    events = client.get_events()
    for event in events:
        print(f"Event: {event.get('id')} - {event.get('name')} - {event.get('status')}")
    
    # Test get active events
    print("\n=== Testing get_events with status filter ===")
    active_events = client.get_events(status='IN_ACTIVE')
    for event in active_events:
        print(f"Active Event: {event.get('id')} - {event.get('name')}")
    
    # Test get user (example ID)
    print("\n=== Testing get_user ===")
    user = client.get_user("123")
    if user:
        print(f"User: {user.get('name')}")
    else:
        print("User not found")
    
    # Close client
    client.close()
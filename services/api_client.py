import requests
import time
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ApiClient:
    """Generic API client for making HTTP requests with rate limiting"""
    
    def __init__(self, base_url: str, headers: Dict[str, str] = None, rate_limit_delay: float = 1.0):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_request_time = 0
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, endpoint: str = "", params: Dict[str, Any] = None, timeout: int = 30) -> Tuple[bool, Dict[str, Any], float, Optional[str]]:
        """
        Make a request to the API
        
        Returns:
            Tuple of (success, response_data, response_time, error_message)
        """
        self._enforce_rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        start_time = time.time()
        
        try:
            logger.debug(f"Making request to: {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.debug(f"Request successful: {response.status_code}")
                    return True, data, response_time, None
                except ValueError as e:
                    error_msg = f"Failed to parse JSON response: {str(e)}"
                    logger.error(error_msg)
                    return False, {"raw_response": response.text}, response_time, error_msg
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, {"status_code": response.status_code, "response": response.text}, response_time, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {timeout} seconds"
            logger.error(error_msg)
            return False, {}, time.time() - start_time, error_msg
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg)
            return False, {}, time.time() - start_time, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, {}, time.time() - start_time, error_msg

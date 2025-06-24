import logging
from typing import Dict, Any, Optional, Generator, Tuple
from services.api_client import ApiClient

logger = logging.getLogger(__name__)

class PaginationHandler:
    """Handle different pagination strategies for APIs"""
    
    def __init__(self, api_client: ApiClient, pagination_type: str, pagination_params: Dict[str, Any] = None):
        self.api_client = api_client
        self.pagination_type = pagination_type.lower()
        self.pagination_params = pagination_params or {}
        
    def paginate(self, endpoint: str = "", max_pages: int = 100) -> Generator[Tuple[int, bool, Dict[str, Any], float, Optional[str]], None, None]:
        """
        Generator that yields paginated API responses
        
        Yields:
            Tuple of (page_number, success, response_data, response_time, error_message)
        """
        if self.pagination_type == 'page':
            yield from self._paginate_by_page(endpoint, max_pages)
        elif self.pagination_type == 'offset':
            yield from self._paginate_by_offset(endpoint, max_pages)
        elif self.pagination_type == 'cursor':
            yield from self._paginate_by_cursor(endpoint, max_pages)
        else:
            logger.error(f"Unsupported pagination type: {self.pagination_type}")
            yield 1, False, {}, 0, f"Unsupported pagination type: {self.pagination_type}"
    
    def _paginate_by_page(self, endpoint: str, max_pages: int) -> Generator[Tuple[int, bool, Dict[str, Any], float, Optional[str]], None, None]:
        """Handle page number-based pagination"""
        page_param = self.pagination_params.get('page_param', 'page')
        page_size_param = self.pagination_params.get('page_size_param', 'per_page')
        page_size = self.pagination_params.get('page_size', 20)
        start_page = self.pagination_params.get('start_page', 1)
        
        for page in range(start_page, start_page + max_pages):
            params = {
                page_param: page,
                page_size_param: page_size
            }
            
            # Add any additional parameters
            additional_params = self.pagination_params.get('additional_params', {})
            params.update(additional_params)
            
            success, data, response_time, error = self.api_client.make_request(endpoint, params)
            yield page, success, data, response_time, error
            
            if not success:
                logger.warning(f"Failed to fetch page {page}, stopping pagination")
                break
                
            # Check if we've reached the end of data
            if self._is_last_page_by_page(data, page_size):
                logger.info(f"Reached end of data at page {page}")
                break
    
    def _paginate_by_offset(self, endpoint: str, max_pages: int) -> Generator[Tuple[int, bool, Dict[str, Any], float, Optional[str]], None, None]:
        """Handle offset-based pagination"""
        offset_param = self.pagination_params.get('offset_param', 'offset')
        limit_param = self.pagination_params.get('limit_param', 'limit')
        limit = self.pagination_params.get('limit', 20)
        start_offset = self.pagination_params.get('start_offset', 0)
        
        page = 1
        offset = start_offset
        
        while page <= max_pages:
            params = {
                offset_param: offset,
                limit_param: limit
            }
            
            # Add any additional parameters
            additional_params = self.pagination_params.get('additional_params', {})
            params.update(additional_params)
            
            success, data, response_time, error = self.api_client.make_request(endpoint, params)
            yield page, success, data, response_time, error
            
            if not success:
                logger.warning(f"Failed to fetch page {page} (offset {offset}), stopping pagination")
                break
                
            # Check if we've reached the end of data
            if self._is_last_page_by_offset(data, limit):
                logger.info(f"Reached end of data at page {page} (offset {offset})")
                break
            
            offset += limit
            page += 1
    
    def _paginate_by_cursor(self, endpoint: str, max_pages: int) -> Generator[Tuple[int, bool, Dict[str, Any], float, Optional[str]], None, None]:
        """Handle cursor-based pagination"""
        cursor_param = self.pagination_params.get('cursor_param', 'cursor')
        cursor_field = self.pagination_params.get('cursor_field', 'next_cursor')
        page_size_param = self.pagination_params.get('page_size_param', 'limit')
        page_size = self.pagination_params.get('page_size', 20)
        
        page = 1
        cursor = self.pagination_params.get('start_cursor')
        
        while page <= max_pages:
            params = {page_size_param: page_size}
            
            if cursor:
                params[cursor_param] = cursor
            
            # Add any additional parameters
            additional_params = self.pagination_params.get('additional_params', {})
            params.update(additional_params)
            
            success, data, response_time, error = self.api_client.make_request(endpoint, params)
            yield page, success, data, response_time, error
            
            if not success:
                logger.warning(f"Failed to fetch page {page}, stopping pagination")
                break
            
            # Get next cursor
            next_cursor = self._extract_cursor(data, cursor_field)
            if not next_cursor:
                logger.info(f"No more data available after page {page}")
                break
            
            cursor = next_cursor
            page += 1
    
    def _is_last_page_by_page(self, data: Dict[str, Any], expected_page_size: int) -> bool:
        """Determine if this is the last page for page-based pagination"""
        # Check common patterns for determining last page
        
        # Pattern 1: Check if returned items < expected page size
        items = self._extract_items(data)
        if items is not None and len(items) < expected_page_size:
            return True
        
        # Pattern 2: Check for explicit pagination metadata
        if isinstance(data, dict):
            # Check for common pagination metadata fields
            pagination_fields = ['pagination', 'meta', 'page_info', 'paging']
            for field in pagination_fields:
                if field in data:
                    pagination_info = data[field]
                    if isinstance(pagination_info, dict):
                        # Check for has_next, has_more, is_last, etc.
                        if pagination_info.get('has_next') is False or pagination_info.get('has_more') is False:
                            return True
                        if pagination_info.get('is_last') is True:
                            return True
        
        return False
    
    def _is_last_page_by_offset(self, data: Dict[str, Any], expected_limit: int) -> bool:
        """Determine if this is the last page for offset-based pagination"""
        return self._is_last_page_by_page(data, expected_limit)
    
    def _extract_cursor(self, data: Dict[str, Any], cursor_field: str) -> Optional[str]:
        """Extract cursor from response data"""
        if not isinstance(data, dict):
            return None
        
        # Try direct field access
        if cursor_field in data:
            return data[cursor_field]
        
        # Try nested access in common pagination fields
        pagination_fields = ['pagination', 'meta', 'page_info', 'paging']
        for field in pagination_fields:
            if field in data and isinstance(data[field], dict):
                if cursor_field in data[field]:
                    return data[field][cursor_field]
        
        return None
    
    def _extract_items(self, data: Dict[str, Any]) -> Optional[list]:
        """Extract items list from response data"""
        if not isinstance(data, dict):
            return None
        
        # Common field names for data arrays
        item_fields = ['data', 'items', 'results', 'records', 'entries']
        
        for field in item_fields:
            if field in data and isinstance(data[field], list):
                return data[field]
        
        # If data itself is a list
        if isinstance(data, list):
            return data
        
        return None

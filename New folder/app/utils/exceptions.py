class WebsiteNotFoundError(Exception):
    """Raised when a website cannot be found or accessed"""
    pass

class ShopifyDataError(Exception):
    """Raised when invalid or incomplete Shopify data is encountered"""
    pass

class InvalidURLFormatError(Exception):
    """Raised when an invalid URL format is provided"""
    pass

class RateLimitExceededError(Exception):
    """Raised when too many requests are made in a short time"""
    pass

class DataProcessingError(Exception):
    """Raised when data processing fails"""
    pass
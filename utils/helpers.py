# shopify_insights_app/utils/helpers.py

from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    """Ensures the URL has a scheme and ends with a slash."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url  # Default to https if no scheme
    if not url.endswith('/'):
        url += '/'
    return url

def is_valid_shopify_url(url: str) -> bool:
    """
    A very basic check to see if it *might* be a Shopify URL.
    This is not foolproof and would need more robust checks for production.
    Common Shopify indicators:
    - store.myshopify.com in the URL (subdomain)
    - presence of specific JS files (e.g., shopify.com/shopify.js) (requires fetching page)
    - common Shopify paths like /products.json
    For this assignment, we'll rely on the /products.json endpoint later.
    """
    parsed_url = urlparse(url)
    # Check for common Shopify-related domains (e.g., myshopify.com)
    if "myshopify.com" in parsed_url.netloc:
        return True
    # More advanced checks would require making a request and inspecting page source
    # For now, we rely on the /products.json check in the main scraping logic.
    return True # Assume valid for now, will fail gracefully later if not shopify
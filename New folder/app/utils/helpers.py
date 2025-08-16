from urllib.parse import urlparse, urlunparse
import re

def normalize_url(url: str) -> str:
    """Normalize URL to ensure consistent format"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    parsed = urlparse(url)
    # Remove www. if present
    netloc = parsed.netloc.replace('www.', '')
    # Reconstruct URL
    return urlunparse((
        parsed.scheme,
        netloc,
        parsed.path.rstrip('/'),
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

def extract_domain(url: str) -> str:
    """Extract domain name from URL"""
    parsed = urlparse(normalize_url(url))
    domain = parsed.netloc
    # Remove port number if present
    domain = domain.split(':')[0]
    return domain

def is_valid_shopify_url(url: str) -> bool:
    """Check if URL might be a Shopify store"""
    domain = extract_domain(url)
    # Simple check - Shopify stores often have myshopify.com or custom domains
    return bool(re.search(r'\.myshopify\.com$|\.com$|\.in$|\.io$', domain))
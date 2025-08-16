from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List, Dict, Optional
from app.models.schemas import Product, FAQItem, Policy, SocialHandle

def parse_shopify_data(html_content: str, base_url: str) -> Dict:
    """Parse Shopify store HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    return {
        'products': parse_products(soup, base_url),
        'faqs': parse_faqs(soup),
        'policies': parse_policies(soup),
        'social_handles': parse_social_handles(soup)
    }

def parse_products(soup: BeautifulSoup, base_url: str) -> List[Product]:
    """Parse product information from HTML"""
    products = []
    product_cards = soup.find_all('div', class_=re.compile(r'product-card|product-item', re.I))
    
    for card in product_cards:
        title_elem = card.find(['h2', 'h3'], class_=re.compile(r'title|name', re.I))
        price_elem = card.find('span', class_=re.compile(r'price', re.I))
        link_elem = card.find('a', href=True)
        image_elem = card.find('img')
        
        if title_elem and price_elem:
            products.append(Product(
                title=title_elem.get_text(strip=True),
                price=price_elem.get_text(strip=True),
                available=True,
                url=urljoin(base_url, link_elem['href']) if link_elem else None,
                image_url=image_elem['src'] if image_elem and 'src' in image_elem.attrs else None
            ))
    
    return products

def parse_faqs(soup: BeautifulSoup) -> List[FAQItem]:
    """Parse FAQ items from HTML"""
    faqs = []
    faq_items = soup.find_all('div', class_=re.compile(r'faq-item|accordion-item', re.I))
    
    for item in faq_items:
        question = item.find(['h3', 'h4'], class_=re.compile(r'question|title', re.I))
        answer = item.find(['div', 'p'], class_=re.compile(r'answer|content', re.I))
        
        if question and answer:
            faqs.append(FAQItem(
                question=question.get_text(strip=True),
                answer=answer.get_text('\n', strip=True)
            ))
    
    return faqs

def parse_policies(soup: BeautifulSoup) -> Dict[str, Policy]:
    """Parse policy documents from HTML"""
    policies = {}
    policy_links = soup.find_all('a', href=re.compile(r'policy|terms|privacy|refund', re.I))
    
    for link in policy_links:
        policy_type = 'privacy' if 'privacy' in link['href'].lower() else 'refund'
        policies[policy_type] = Policy(
            title=link.get_text(strip=True),
            content=f"See full policy at {link['href']}"
        )
    
    return policies

def parse_social_handles(soup: BeautifulSoup) -> List[SocialHandle]:
    """Parse social media links from HTML"""
    social_links = []
    social_elements = soup.find_all('a', href=re.compile(
        r'facebook|instagram|twitter|x\.com|tiktok|pinterest|youtube', re.I))
    
    for element in social_elements:
        url = element.get('href', '')
        platform = identify_social_platform(url)
        if platform:
            social_links.append(SocialHandle(
                platform=platform,
                url=url,
                handle=extract_social_handle(url)
            ))
    
    return social_links

def identify_social_platform(url: str) -> Optional[str]:
    """Identify social platform from URL"""
    platform_patterns = {
        'facebook': r'facebook\.com',
        'instagram': r'instagram\.com',
        'twitter': r'twitter\.com|x\.com',
        'tiktok': r'tiktok\.com',
        'pinterest': r'pinterest\.com',
        'youtube': r'youtube\.com|youtu\.be'
    }
    
    for platform, pattern in platform_patterns.items():
        if re.search(pattern, url, re.I):
            return platform
    return None

def extract_social_handle(url: str) -> str:
    """Extract handle from social URL"""
    handle = re.sub(r'^https?://(www\.)?', '', url, flags=re.I)
    handle = re.sub(r'\/.*$', '', handle)
    return handle
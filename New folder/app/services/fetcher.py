import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import asyncio
from typing import List, Dict, Optional
from app.utils.exceptions import WebsiteNotFoundError, ShopifyDataError
from app.utils.helpers import normalize_url, extract_domain
from app.models.schemas import Product, FAQItem, Policy, SocialHandle, ContactInfo
from pydantic import BaseModel
# or from your schemas import the specific models you need
class ShopifyFetcher:
    def __init__(self, website_url: str):
        self.base_url = normalize_url(website_url)
        self.domain = extract_domain(self.base_url)
        self.client = httpx.AsyncClient()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


    async def fetch_important_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract important links from the homepage"""
        important_links = {}
        link_texts = [
            'track order', 'order tracking', 'contact us', 
            'blog', 'help', 'support', 'size guide'
        ]
        
        for text in link_texts:
            link = soup.find('a', string=re.compile(text, re.I))
            if link and link.get('href'):
                important_links[text] = urljoin(self.base_url, link['href'])
        
        return important_links

   
    async def fetch_all_data(self) -> Dict:
        """Fetch all required data from Shopify store"""
        try:
            homepage = await self._fetch_homepage()
            
            products, hero_products, policies, faqs = await asyncio.gather(
                self.fetch_products(),
                self.fetch_hero_products(homepage),
                self.fetch_policies(),
                self.fetch_faqs()
            )
            
            return {
            "products": products,
            "hero_products": hero_products,
            "policies": policies,
            "faqs": faqs,
            "social_handles": await self.fetch_social_handles(homepage),
            "contact_info": await self.fetch_contact_info(homepage),
            "about_brand": await self.fetch_about_brand(),
            "important_links": await self.fetch_important_links(homepage)  # This was missing
        }
        except Exception as e:
            raise ShopifyDataError(f"Failed to fetch data: {str(e)}")
    


    async def _fetch_homepage(self) -> BeautifulSoup:
        """Fetch and parse homepage"""
        try:
            response = await self.client.get(self.base_url)
            if response.status_code != 200:
                raise WebsiteNotFoundError("Website not found or inaccessible")
            return BeautifulSoup(response.text, 'html.parser')
        except httpx.RequestError as e:
            raise WebsiteNotFoundError(f"Could not connect to website: {str(e)}")
    
    async def fetch_products(self) -> List[Product]:
        """Fetch product catalog from /products.json"""
        products_url = urljoin(self.base_url, "/products.json")
        try:
            response = await self.client.get(products_url)
            if response.status_code == 200:
                products_data = response.json().get('products', [])
                return [
                    Product(
                        id=str(product.get('id', '')),
                        title=product.get('title', ''),
                        description=product.get('body_html', ''),
                        price=self._extract_price(product),
                        available=product.get('available', False),
                        url=urljoin(self.base_url, f"/products/{product.get('handle', '')}"),
                        image_url=self._extract_image_url(product)
                    )
                    for product in products_data
                ]
            return []
        except (json.JSONDecodeError, httpx.RequestError):
            return []
    
    def _extract_price(self, product: Dict) -> str:
        variants = product.get('variants', [{}])
        if not variants:
            return "N/A"
        price = variants[0].get('price', 'N/A')
        compare_price = variants[0].get('compare_at_price')
        if compare_price and compare_price != price:
            return f"{price} (Was {compare_price})"
        return price
    
    def _extract_image_url(self, product: Dict) -> Optional[str]:
        images = product.get('images', [])
        if not images:
            return None
        return images[0].get('src')
    
    async def fetch_hero_products(self, soup: BeautifulSoup) -> List[Product]:
        """Parse hero products from homepage"""
        hero_products = []
        product_sections = soup.find_all('div', class_=re.compile(r'product-card|featured-product', re.I))
        
        for section in product_sections:
            title_elem = section.find(['h2', 'h3', 'h4'], class_=re.compile(r'title|name', re.I))
            price_elem = section.find('span', class_=re.compile(r'price', re.I))
            link_elem = section.find('a', href=True)
            
            if title_elem and price_elem:
                product = Product(
                    title=title_elem.get_text(strip=True),
                    price=price_elem.get_text(strip=True),
                    available=True,
                    url=urljoin(self.base_url, link_elem['href']) if link_elem else None,
                    description=''
                )
                hero_products.append(product)
                
        return hero_products
    
    async def fetch_policies(self) -> Dict[str, Policy]:
        """Fetch privacy and refund policies"""
        policies = {}
        policy_types = ['privacy', 'refund']
        
        for policy_type in policy_types:
            paths = [
                f"/policies/{policy_type}-policy",
                f"/pages/{policy_type}-policy",
                f"/{policy_type}-policy"
            ]
            
            for path in paths:
                try:
                    policy_url = urljoin(self.base_url, path)
                    response = await self.client.get(policy_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        content = soup.find('div', class_=re.compile(r'policy|content', re.I))
                        policies[policy_type] = Policy(
                            title=f"{policy_type.capitalize()} Policy",
                            content=content.get_text('\n', strip=True) if content else ''
                        )
                        break
                except httpx.RequestError:
                    continue
        
        return policies
    
    async def fetch_faqs(self) -> List[FAQItem]:
        """Fetch and parse FAQs"""
        faq_paths = ['/pages/faq', '/pages/frequently-asked-questions', '/faq']
        
        for path in faq_paths:
            try:
                faq_url = urljoin(self.base_url, path)
                response = await self.client.get(faq_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return self._parse_faqs(soup)
            except httpx.RequestError:
                continue
                
        return []
    
    def _parse_faqs(self, soup: BeautifulSoup) -> List[FAQItem]:
        """Parse FAQ items from HTML"""
        faqs = []
        
        # Try accordion-style FAQs
        accordions = soup.find_all(['div', 'section'], class_=re.compile(r'accordion|faq-item', re.I))
        for item in accordions:
            question = item.find(['h3', 'h4', 'div'], class_=re.compile(r'question|title', re.I))
            answer = item.find(['div', 'p'], class_=re.compile(r'answer|content', re.I))
            
            if question and answer:
                faqs.append(FAQItem(
                    question=question.get_text(strip=True),
                    answer=answer.get_text('\n', strip=True)
                ))
        
        # Try list-style FAQs if no accordions found
        if not faqs:
            faq_lists = soup.find_all(['dl', 'div'], class_=re.compile(r'faq-list', re.I))
            for faq_list in faq_lists:
                questions = faq_list.find_all(['dt', 'h3', 'div'], class_=re.compile(r'question', re.I))
                answers = faq_list.find_all(['dd', 'div', 'p'], class_=re.compile(r'answer', re.I))
                
                for q, a in zip(questions, answers):
                    faqs.append(FAQItem(
                        question=q.get_text(strip=True),
                        answer=a.get_text('\n', strip=True)
                    ))
        
        return faqs
    
    async def fetch_social_handles(self, soup: BeautifulSoup) -> List[SocialHandle]:
        """Parse social media links"""
        social_links = []
        social_elements = soup.find_all('a', href=re.compile(
            r'facebook|instagram|twitter|x\.com|tiktok|pinterest|youtube', re.I))
        
        for element in social_elements:
            url = element.get('href', '')
            platform = self._identify_social_platform(url)
            if platform:
                social_links.append(SocialHandle(
                    platform=platform,
                    url=url,
                    handle=self._extract_social_handle(url)
                ))  # Properly closed now
        
        return social_links
    
    def _identify_social_platform(self, url: str) -> Optional[str]:
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
    
    def _extract_social_handle(self, url: str) -> str:
        """Extract handle from social URL"""
        handle = re.sub(r'^https?://(www\.)?', '', url, flags=re.I)
        handle = re.sub(r'\/.*$', '', handle)
        return handle
    
    async def fetch_contact_info(self, soup: BeautifulSoup) -> ContactInfo:
        """Extract contact information"""
        contact_info = {
            'emails': [],
            'phone_numbers': [],
            'addresses': []
        }
        
        # Find contact page link
        contact_page_url = None
        contact_links = soup.find_all('a', string=re.compile(r'contact|reach us|get in touch', re.I))
        for link in contact_links:
            if link.get('href'):
                contact_page_url = urljoin(self.base_url, link['href'])
                break
        
        # Scrape contact page if found
        if contact_page_url:
            try:
                response = await self.client.get(contact_page_url)
                if response.status_code == 200:
                    contact_soup = BeautifulSoup(response.text, 'html.parser')
                    contact_info = self._extract_contact_info(contact_soup)
            except httpx.RequestError:
                pass
        
        # Also check footer
        footer = soup.find('footer')
        if footer:
            footer_contact_info = self._extract_contact_info(footer)
            contact_info['emails'] = list(set(contact_info['emails'] + footer_contact_info['emails']))
            contact_info['phone_numbers'] = list(set(contact_info['phone_numbers'] + footer_contact_info['phone_numbers']))
            contact_info['addresses'] = list(set(contact_info['addresses'] + footer_contact_info['addresses']))
        
        return ContactInfo(**contact_info)
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Helper to extract contact info from HTML"""
        contact_info = {
            'emails': [],
            'phone_numbers': [],
            'addresses': []
        }
        
        # Extract emails
        email_links = soup.find_all('a', href=re.compile(r'mailto:'))
        for link in email_links:
            email = link['href'].replace('mailto:', '').strip()
            if email and email not in contact_info['emails']:
                contact_info['emails'].append(email)
        
        # Extract phone numbers
        phone_links = soup.find_all('a', href=re.compile(r'tel:'))
        for link in phone_links:
            phone = link['href'].replace('tel:', '').strip()
            if phone and phone not in contact_info['phone_numbers']:
                contact_info['phone_numbers'].append(phone)
        
        # Extract addresses
        address_elements = soup.find_all(['address', 'div', 'p'], class_=re.compile(r'address', re.I))
        for element in address_elements:
            address = element.get_text('\n', strip=True)
            if address and address not in contact_info['addresses']:
                contact_info['addresses'].append(address)
        
        return contact_info
    
    async def fetch_social_handles(self, soup: BeautifulSoup) -> List[SocialHandle]:
        """Parse social media links"""
        social_links = []
        social_elements = soup.find_all('a', href=re.compile(
            r'facebook|instagram|twitter|x\.com|tiktok|pinterest|youtube', re.I))
        
        for element in social_elements:
            url = element.get('href', '')
            platform = self._identify_social_platform(url)
            if platform:
                social_links.append(SocialHandle(
                    platform=platform,
                    url=url,
                    handle=self._extract_social_handle(url)
                ))  # Properly closed now
        
        return social_links

    # ... (keep all other methods the same, except remove the duplicate fetch_social_handles)

    async def fetch_about_brand(self) -> str:
        """Fetch about brand section"""
        about_page_url = None
        homepage = await self._fetch_homepage()  # Get the homepage first
        about_links = homepage.find_all('a', string=re.compile(r'about us|our story|about', re.I))
        for link in about_links:
            if link.get('href'):
                about_page_url = urljoin(self.base_url, link['href'])
                break
        
        if about_page_url:
            try:
                response = await self.client.get(about_page_url)
                if response.status_code == 200:
                    about_soup = BeautifulSoup(response.text, 'html.parser')
                    content = about_soup.find('div', class_=re.compile(r'content|about-text', re.I))
                    if content:
                        return content.get_text('\n', strip=True)
            except httpx.RequestError:
                pass
        
        return ""
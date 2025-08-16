import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from models.brand_data import Product, Policy, FAQItem, ContactDetails, SocialHandle, ImportantLink, BrandContext

class ShopifyParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.scraped_urls = set() # To prevent infinite loops with internal links

    def _get_absolute_url(self, relative_url: str) -> Optional[str]:
        if relative_url and not relative_url.startswith('javascript:'):
            return urljoin(self.base_url, relative_url)
        return None

    def parse_product_catalog(self, products_json: Dict) -> List[Product]:
        products = []
        if products_json and 'products' in products_json:
            for item in products_json['products']:
                try:
                    price = None
                    currency = None
                    if item.get('variants'):
                        first_variant = item['variants'][0]
                        price = first_variant.get('price')
                        currency = "USD" # Placeholder, actual scraping needed

                    image_url = None
                    if item.get('images'):
                        image_url = item['images'][0].get('src')

                    handle = item.get('handle')
                    product_url = None
                    if handle:
                        product_url = self._get_absolute_url(f"/products/{handle}")

                    products.append(Product(
                        title=item.get('title', 'N/A'),
                        price=price,
                        currency=currency,
                        image_url=image_url,
                        product_url=product_url,
                        description=item.get('body_html')
                    ))
                except Exception as e:
                    print(f"Error parsing product: {e} - Data: {item}")
        return products

    def parse_hero_products(self, soup: BeautifulSoup) -> List[Product]:
        hero_products = []
        try:
            product_card_elements = soup.find_all(class_=re.compile(r'product-card|product-item|featured-product'))
            for card in product_card_elements:
                title_elem = card.find(class_=re.compile(r'product-card__title|product-item__title|product-title'))
                price_elem = card.find(class_=re.compile(r'price-item|product-card__price'))
                img_elem = card.find('img')
                link_elem = card.find('a', href=True)

                title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                price_text = price_elem.get_text(strip=True) if price_elem else None
                image_url = self._get_absolute_url(img_elem['src']) if img_elem and 'src' in img_elem else None
                product_url = self._get_absolute_url(link_elem['href']) if link_elem and 'href' in link_elem else None

                price = None
                currency = None
                if price_text:
                    match = re.search(r'([£$€₹])?\s*(\d[\d,.]*)', price_text)
                    if match:
                        currency_symbol = match.group(1)
                        numeric_price = match.group(2).replace(',', '')
                        price = numeric_price
                        if currency_symbol == '₹':
                            currency = "INR"
                        elif currency_symbol == '$':
                            currency = "USD"
                        elif currency_symbol == '€':
                            currency = "EUR"
                        elif currency_symbol == '£':
                            currency = "GBP"
                        else:
                            currency = "Unknown"

                if title != 'N/A':
                    hero_products.append(Product(
                        title=title,
                        price=price,
                        currency=currency,
                        image_url=image_url,
                        product_url=product_url
                    ))
        except Exception as e:
            print(f"Error parsing hero products: {e}")
        return hero_products

    # CORRECTED: Added page_url parameter to Policy model creation
    def parse_policy(self, soup: BeautifulSoup, policy_type: str, page_url: Optional[str] = None) -> Optional[Policy]:
        content_div = soup.find('div', class_=re.compile(r'rte|policy-content|page-content')) or \
                      soup.find('article') or \
                      soup.find('main')

        if content_div:
            for script_or_style in content_div(['script', 'style']):
                script_or_style.extract()
            content = content_div.get_text(separator="\n", strip=True)
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else policy_type.replace('_', ' ').title()

            # Pass the provided page_url directly
            return Policy(title=title, content=content, url=page_url)
        return None

    def parse_faqs(self, soup: BeautifulSoup) -> List[FAQItem]:
        faqs = []
        faq_sections = soup.find_all(class_=re.compile(r'faq-section|accordion|faq-list'))

        for section in faq_sections:
            questions = section.find_all(class_=re.compile(r'faq-question|accordion-header|question'))
            answers = section.find_all(class_=re.compile(r'faq-answer|accordion-content|answer'))

            for i in range(min(len(questions), len(answers))):
                q = questions[i].get_text(strip=True)
                a = answers[i].get_text(strip=True)
                if q and a:
                    faqs.append(FAQItem(question=q, answer=a))
            
            h_tags = section.find_all(re.compile(r'h[2-6]'))
            for h in h_tags:
                if '?' in h.get_text():
                    answer_elem = h.find_next_sibling(['p', 'div'])
                    if answer_elem:
                        faqs.append(FAQItem(question=h.get_text(strip=True), answer=answer_elem.get_text(strip=True)))
        return faqs

    def parse_social_handles(self, soup: BeautifulSoup) -> List[SocialHandle]:
        social_handles = []
        social_platforms = {
            'facebook': ['facebook.com', 'fb.me'],
            'instagram': ['instagram.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'youtube': ['youtube.com'], # Corrected YouTube domain
            'pinterest': ['pinterest.com'],
            'tiktok': ['tiktok.com']
        }

        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            for platform, keywords in social_platforms.items():
                if any(keyword in href for keyword in keywords):
                    if not any(s.url == href for s in social_handles):
                        # Ensure URL is absolute for Pydantic HttpUrl validation
                        absolute_href = self._get_absolute_url(href)
                        if absolute_href:
                            social_handles.append(SocialHandle(platform=platform, url=absolute_href))
                    break
        return social_handles

    def parse_contact_details(self, soup: BeautifulSoup) -> ContactDetails:
        emails = set()
        phone_numbers = set()

        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        for match in re.finditer(email_pattern, soup.get_text()):
            emails.add(match.group(0))

        phone_pattern = r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?'
        for match in re.finditer(phone_pattern, soup.get_text()):
            groups = [g for g in match.groups() if g is not None]
            phone_numbers.add("".join(groups))
            
        return ContactDetails(emails=list(emails), phone_numbers=list(phone_numbers))

    def parse_brand_text_context(self, soup: BeautifulSoup) -> Optional[str]:
        about_us_keywords = ['about us', 'our story', 'who we are', 'brand story']
        text_content = []

        main_content_areas = soup.find_all(['div', 'article', 'main'], class_=re.compile(r'main-content|content|section|about'))
        
        for area in main_content_areas:
            paragraphs = area.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text.split()) > 20:
                    text_content.append(text)
        
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and 'content' in meta_description.attrs:
            text_content.insert(0, meta_description['content'])

        return "\n\n".join(text_content) if text_content else None


    def parse_important_links(self, soup: BeautifulSoup) -> List[ImportantLink]:
        important_links = []
        
        link_keywords = {
            "Order tracking": ["track order", "order status", "my orders"],
            "Contact Us": ["contact", "support", "help center"],
            "Blogs": ["blog", "news"],
            "Shipping": ["shipping", "delivery"],
            "Careers": ["careers", "jobs"],
            "Terms of Service": ["terms of service", "terms & conditions"],
            "Privacy Policy": ["privacy policy"],
            "Refund Policy": ["refund policy", "return policy"]
        }

        all_links = soup.find_all('a', href=True)
        for link_element in all_links:
            href = link_element['href']
            text = link_element.get_text(strip=True)
            absolute_url = self._get_absolute_url(href)

            if absolute_url and urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                for category, keywords in link_keywords.items():
                    if any(kw.lower() in text.lower() for kw in keywords) or \
                       any(kw.lower().replace(' ', '-') in absolute_url.lower() for kw in keywords):
                        if not any(imp_link.url == absolute_url for imp_link in important_links):
                            important_links.append(ImportantLink(text=text if text else category, url=absolute_url))
                        break
        return important_links
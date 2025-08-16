from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl

class Product(BaseModel):
    id: Optional[str]
    title: str
    description: Optional[str]
    price: str
    available: bool
    url: Optional[HttpUrl]
    image_url: Optional[HttpUrl]

class FAQItem(BaseModel):
    question: str
    answer: str

class Policy(BaseModel):
    title: str
    content: str

class SocialHandle(BaseModel):
    platform: str
    url: HttpUrl
    handle: str

class ContactInfo(BaseModel):
    emails: List[str]
    phone_numbers: List[str]
    addresses: List[str]

class BrandInsightsResponse(BaseModel):
    store_url: HttpUrl
    product_catalog: List[Product]
    hero_products: List[Product]
    privacy_policy: Policy
    return_refund_policy: Policy
    faqs: List[FAQItem]
    social_handles: List[SocialHandle]
    contact_info: ContactInfo
    about_brand: str
    important_links: Dict[str, HttpUrl]
    fetched_at: str
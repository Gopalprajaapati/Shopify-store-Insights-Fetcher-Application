from pydantic import BaseModel, HttpUrl, AnyHttpUrl
from datetime import datetime
from typing import List, Optional, Dict, Union
import json

class Product(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: str
    available: bool
    url: Optional[Union[HttpUrl, str]] = None
    image_url: Optional[Union[HttpUrl, str]] = None

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if data.get('url'):
            data['url'] = str(data['url'])
        if data.get('image_url'):
            data['image_url'] = str(data['image_url'])
        return data

class FAQItem(BaseModel):
    question: str
    answer: str

class Policy(BaseModel):
    title: str
    content: str

class SocialHandle(BaseModel):
    platform: str
    url: Union[HttpUrl, str]
    handle: str

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['url'] = str(data['url'])
        return data

class ContactInfo(BaseModel):
    emails: List[str]
    phone_numbers: List[str]
    addresses: List[str]

class BrandInsightsResponse(BaseModel):
    store_url: Union[HttpUrl, str]
    product_catalog: List[Product]
    hero_products: List[Product]
    privacy_policy: Policy
    return_refund_policy: Policy
    faqs: List[FAQItem]
    social_handles: List[SocialHandle]
    contact_info: ContactInfo
    about_brand: str
    important_links: Dict[str, Union[HttpUrl, str]]
    fetched_at: datetime

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['store_url'] = str(data['store_url'])
        data['important_links'] = {k: str(v) for k, v in data['important_links'].items()}
        data['fetched_at'] = data['fetched_at'].isoformat()
        return data

class CompetitorAnalysisResponse(BrandInsightsResponse):
    original_store: Union[HttpUrl, str]
    competitors: List[BrandInsightsResponse]

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['original_store'] = str(data['original_store'])
        return data
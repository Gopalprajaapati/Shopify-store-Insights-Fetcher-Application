from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Dict, Optional, Any

class Product(BaseModel):
    title: str
    price: Optional[str] = None
    currency: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    product_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    # Add more fields as identified from /products.json or HTML scraping

class Policy(BaseModel):
    title: str
    content: str
    url: Optional[HttpUrl] = None

class FAQItem(BaseModel):
    question: str
    answer: str

class ContactDetails(BaseModel):
    emails: List[EmailStr] = []
    phone_numbers: List[str] = []

class SocialHandle(BaseModel):
    platform: str
    url: HttpUrl
    username: Optional[str] = None

class ImportantLink(BaseModel):
    text: str
    url: HttpUrl

class BrandContext(BaseModel):
    website_url: HttpUrl
    brand_name: Optional[str] = None
    product_catalog: List[Product] = Field(default_factory=list)
    hero_products: List[Product] = Field(default_factory=list)
    privacy_policy: Optional[Policy] = None
    return_refund_policy: Optional[Policy] = None
    faqs: List[FAQItem] = Field(default_factory=list)
    social_handles: List[SocialHandle] = Field(default_factory=list)
    contact_details: Optional[ContactDetails] = None
    brand_text_context: Optional[str] = None # About us, brand story, etc.
    important_links: List[ImportantLink] = Field(default_factory=list)
    other_insights: Dict[str, Any] = Field(default_factory=dict) # For any additional data
# shopify_insights_app/database/crud.py

from sqlalchemy.orm import Session
from database.models import (
    BrandDB, ProductDB, HeroProductDB, PolicyDB, FAQItemDB,
    ContactDetailsDB, SocialHandleDB, ImportantLinkDB
)
from models.brand_data import BrandContext, Product, Policy, FAQItem, ContactDetails, SocialHandle, ImportantLink
from typing import List, Optional
from datetime import datetime

def get_brand_by_url(db: Session, website_url: str) -> Optional[BrandDB]:
    return db.query(BrandDB).filter(BrandDB.website_url == website_url).first()

def create_brand_insights(db: Session, brand_data: BrandContext) -> BrandDB:
    # Check if brand already exists
    db_brand = get_brand_by_url(db, str(brand_data.website_url))
    if db_brand:
        # For simplicity, if exists, delete old related data and update.
        # In a real app, you might merge or version data.
        db.delete(db_brand)
        db.commit()
        db.refresh(db_brand) # Refresh the object for a clean slate

    db_brand = BrandDB(
        website_url=str(brand_data.website_url),
        brand_name=brand_data.brand_name,
        brand_text_context=brand_data.brand_text_context,
        last_fetched=datetime.utcnow()
    )
    db.add(db_brand)
    db.flush() # Flush to get db_brand.id before committing

    # Products
    for prod in brand_data.product_catalog:
        db_prod = ProductDB(
            brand_id=db_brand.id,
            title=prod.title,
            price=prod.price,
            currency=prod.currency,
            image_url=str(prod.image_url) if prod.image_url else None,
            product_url=str(prod.product_url) if prod.product_url else None,
            description=prod.description
        )
        db.add(db_prod)
    
    # Hero Products
    for hero_prod in brand_data.hero_products:
        db_hero_prod = HeroProductDB(
            brand_id=db_brand.id,
            title=hero_prod.title,
            price=hero_prod.price,
            currency=hero_prod.currency,
            image_url=str(hero_prod.image_url) if hero_prod.image_url else None,
            product_url=str(hero_prod.product_url) if hero_prod.product_url else None
        )
        db.add(db_hero_prod)

    # Policies
    if brand_data.privacy_policy:
        db_privacy = PolicyDB(
            brand_privacy_id=db_brand.id,
            title=brand_data.privacy_policy.title,
            content=brand_data.privacy_policy.content,
            url=str(brand_data.privacy_policy.url) if brand_data.privacy_policy.url else None,
            policy_type='privacy'
        )
        db.add(db_privacy)
    if brand_data.return_refund_policy:
        db_return_refund = PolicyDB(
            brand_return_refund_id=db_brand.id,
            title=brand_data.return_refund_policy.title,
            content=brand_data.return_refund_policy.content,
            url=str(brand_data.return_refund_policy.url) if brand_data.return_refund_policy.url else None,
            policy_type='return_refund'
        )
        db.add(db_return_refund)

    # FAQs
    for faq in brand_data.faqs:
        db_faq = FAQItemDB(
            brand_id=db_brand.id,
            question=faq.question,
            answer=faq.answer
        )
        db.add(db_faq)

    # Contact Details
    if brand_data.contact_details:
        db_contact = ContactDetailsDB(
            brand_id=db_brand.id,
            emails=",".join(brand_data.contact_details.emails) if brand_data.contact_details.emails else None,
            phone_numbers=",".join(brand_data.contact_details.phone_numbers) if brand_data.contact_details.phone_numbers else None
        )
        db.add(db_contact)

    # Social Handles
    for social in brand_data.social_handles:
        db_social = SocialHandleDB(
            brand_id=db_brand.id,
            platform=social.platform,
            url=str(social.url),
            username=social.username
        )
        db.add(db_social)

    # Important Links
    for link in brand_data.important_links:
        db_link = ImportantLinkDB(
            brand_id=db_brand.id,
            text=link.text,
            url=str(link.url)
        )
        db.add(db_link)

    db.commit()
    db.refresh(db_brand)
    return db_brand

def get_brand_insights_from_db(db: Session, website_url: str) -> Optional[BrandContext]:
    db_brand = db.query(BrandDB).filter(BrandDB.website_url == website_url).first()

    if not db_brand:
        return None

    # Reconstruct Pydantic BrandContext from DB models
    brand_context = BrandContext(
        website_url=db_brand.website_url,
        brand_name=db_brand.brand_name,
        brand_text_context=db_brand.brand_text_context
    )

    brand_context.product_catalog = [
        Product(
            title=p.title,
            price=p.price,
            currency=p.currency,
            image_url=p.image_url,
            product_url=p.product_url,
            description=p.description
        ) for p in db_brand.products
    ]

    brand_context.hero_products = [
        Product( # Using Product Pydantic model for Hero Products
            title=hp.title,
            price=hp.price,
            currency=hp.currency,
            image_url=hp.image_url,
            product_url=hp.product_url
        ) for hp in db_brand.hero_products_rel
    ]

    if db_brand.privacy_policy:
        brand_context.privacy_policy = Policy(
            title=db_brand.privacy_policy.title,
            content=db_brand.privacy_policy.content,
            url=db_brand.privacy_policy.url
        )

    if db_brand.return_refund_policy:
        brand_context.return_refund_policy = Policy(
            title=db_brand.return_refund_policy.title,
            content=db_brand.return_refund_policy.content,
            url=db_brand.return_refund_policy.url
        )

    brand_context.faqs = [
        FAQItem(question=f.question, answer=f.answer) for f in db_brand.faqs
    ]

    if db_brand.contact_details:
        emails = db_brand.contact_details.emails.split(',') if db_brand.contact_details.emails else []
        phone_numbers = db_brand.contact_details.phone_numbers.split(',') if db_brand.contact_details.phone_numbers else []
        brand_context.contact_details = ContactDetails(emails=emails, phone_numbers=phone_numbers)

    brand_context.social_handles = [
        SocialHandle(platform=s.platform, url=s.url, username=s.username) for s in db_brand.social_handles
    ]

    brand_context.important_links = [
        ImportantLink(text=l.text, url=l.url) for l in db_brand.important_links
    ]

    return brand_context
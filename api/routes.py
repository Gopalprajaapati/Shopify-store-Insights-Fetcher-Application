from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import HttpUrl, ValidationError
from sqlalchemy.orm import Session
import re
import requests # Ensure this is imported

from services.scraper import WebScraper
from services.parser import ShopifyParser
from models.brand_data import BrandContext
from utils.helpers import normalize_url, is_valid_shopify_url
from database.dependencies import get_db
from database import crud
from database.models import create_db_tables

router = APIRouter()

create_db_tables()


@router.get("/fetch-insights", response_model=BrandContext, summary="Fetch insights from a Shopify store")
async def fetch_shopify_insights(website_url: HttpUrl, db: Session = Depends(get_db)):
    """
    Fetches comprehensive insights from a given Shopify store URL.
    Attempts to fetch from DB first, if not found, scrapes and saves.

    Args:
        website_url (HttpUrl): The URL of the Shopify store (e.g., https://memy.co.in).
        db (Session): Database session dependency.

    Returns:
        BrandContext: A JSON object containing structured brand data.
    """
    normalized_url = normalize_url(str(website_url))

    existing_brand_data = crud.get_brand_insights_from_db(db, normalized_url)
    if existing_brand_data:
        print(f"Insights for {normalized_url} found in DB. Returning cached data.")
        return existing_brand_data

    try:
        if not is_valid_shopify_url(normalized_url):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided URL does not appear to be a Shopify store.")

        scraper = WebScraper(normalized_url)
        parser = ShopifyParser(normalized_url)
        
        brand_context = BrandContext(website_url=website_url)

        products_json = scraper.fetch_json("/products.json")
        if products_json:
            brand_context.product_catalog = parser.parse_product_catalog(products_json)
        else:
            print(f"Warning: Could not fetch products.json for {normalized_url}. It might not be a standard Shopify store or products are hidden.")

        homepage_soup = scraper.fetch_html("/")
        if homepage_soup:
            brand_context.hero_products = parser.parse_hero_products(homepage_soup)

            # --- Privacy Policy ---
            privacy_policy_url_found = None
            # Try common paths first
            for path in ["/policies/privacy-policy", "/pages/privacy-policy"]:
                url_to_fetch = normalized_url + path
                temp_soup = scraper.fetch_html(url_to_fetch)
                if temp_soup:
                    # Pass the exact URL fetched
                    brand_context.privacy_policy = parser.parse_policy(temp_soup, "privacy_policy", page_url=url_to_fetch)
                    privacy_policy_url_found = url_to_fetch
                    break
            
            # Fallback: search for a privacy policy link on the homepage
            if not brand_context.privacy_policy and homepage_soup:
                privacy_link = homepage_soup.find('a', href=re.compile(r'privacy-policy|privacy', re.IGNORECASE))
                if privacy_link and privacy_link.get('href'):
                    abs_url_from_link = parser._get_absolute_url(privacy_link['href'])
                    if abs_url_from_link:
                        temp_soup = scraper.fetch_html(abs_url_from_link)
                        if temp_soup:
                            # Pass the exact URL fetched from the link
                            brand_context.privacy_policy = parser.parse_policy(temp_soup, "privacy_policy", page_url=abs_url_from_link)
                            privacy_policy_url_found = abs_url_from_link

            # Ensure the policy object has the URL if successfully parsed
            if brand_context.privacy_policy and not brand_context.privacy_policy.url and privacy_policy_url_found:
                brand_context.privacy_policy.url = privacy_policy_url_found


            # --- Return, Refund Policies ---
            return_refund_policy_url_found = None
            for path in ["/policies/refund-policy", "/policies/returns-policy", "/pages/return-policy"]:
                url_to_fetch = normalized_url + path
                temp_soup = scraper.fetch_html(url_to_fetch)
                if temp_soup:
                    brand_context.return_refund_policy = parser.parse_policy(temp_soup, "return_refund_policy", page_url=url_to_fetch)
                    return_refund_policy_url_found = url_to_fetch
                    break
            
            if not brand_context.return_refund_policy and homepage_soup:
                refund_link = homepage_soup.find('a', href=re.compile(r'refund-policy|return-policy|returns', re.IGNORECASE))
                if refund_link and refund_link.get('href'):
                    abs_url_from_link = parser._get_absolute_url(refund_link['href'])
                    if abs_url_from_link:
                        temp_soup = scraper.fetch_html(abs_url_from_link)
                        if temp_soup:
                            brand_context.return_refund_policy = parser.parse_policy(temp_soup, "return_refund_policy", page_url=abs_url_from_link)
                            return_refund_policy_url_found = abs_url_from_link
            
            if brand_context.return_refund_policy and not brand_context.return_refund_policy.url and return_refund_policy_url_found:
                brand_context.return_refund_policy.url = return_refund_policy_url_found


            # --- Brand FAQs ---
            faq_url_found = None
            for path in ["/pages/faqs", "/community/faq", "/apps/help-center/faq"]: 
                url_to_fetch = normalized_url + path
                temp_soup = scraper.fetch_html(url_to_fetch)
                if temp_soup:
                    brand_context.faqs = parser.parse_faqs(temp_soup)
                    faq_url_found = url_to_fetch
                    break
            
            if not brand_context.faqs and homepage_soup: 
                faq_link = homepage_soup.find('a', href=re.compile(r'faq|frequently-asked-questions|help', re.IGNORECASE))
                if faq_link and faq_link.get('href'):
                    abs_url_from_link = parser._get_absolute_url(faq_link['href'])
                    if abs_url_from_link:
                        temp_soup = scraper.fetch_html(abs_url_from_link)
                        if temp_soup:
                            brand_context.faqs = parser.parse_faqs(temp_soup)
                            faq_url_found = abs_url_from_link
            # Note: FAQs don't have a direct 'url' attribute in your model, so no need to assign it here.

            brand_context.social_handles = parser.parse_social_handles(homepage_soup)
            brand_context.contact_details = parser.parse_contact_details(homepage_soup)
            brand_context.brand_text_context = parser.parse_brand_text_context(homepage_soup)
            brand_context.important_links = parser.parse_important_links(homepage_soup)
            
            title_tag = homepage_soup.find('title')
            if title_tag:
                brand_name = title_tag.get_text(strip=True)
                brand_name = re.sub(r'\s*\|\s*Shopify.*$', '', brand_name, flags=re.IGNORECASE)
                brand_name = re.sub(r'\s*-\s*Powered by Shopify.*$', '', brand_name, flags=re.IGNORECASE)
                brand_context.brand_name = brand_name.strip()

        if not brand_context.product_catalog and not brand_context.hero_products and not homepage_soup:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not access the website or retrieve any meaningful data. It might not be a standard Shopify store or is unreachable.")

        crud.create_brand_insights(db, brand_context)
        print(f"Insights for {normalized_url} scraped and saved to DB.")
        
        return brand_context

    except requests.exceptions.MissingSchema:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format. Please ensure it includes http:// or https://")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found or unreachable. Please check the URL.")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Data validation error: {e.errors()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal server error occurred: {e}")
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import BrandInsightsResponse
from app.services.fetcher import ShopifyFetcher
from app.utils.exceptions import WebsiteNotFoundError, ShopifyDataError

router = APIRouter(prefix="/api/v1", tags=["shopify-insights"])

@router.get("/insights", response_model=BrandInsightsResponse)
async def get_shopify_insights(website_url: str):
    try:
        async with ShopifyFetcher(website_url) as fetcher:
            products = await fetcher.fetch_products()
            hero_products = await fetcher.fetch_hero_products()
            privacy_policy = await fetcher.fetch_policy('privacy')
            refund_policy = await fetcher.fetch_policy('refund')
            faqs = await fetcher.fetch_faqs()
            social_handles = await fetcher.fetch_social_handles()
            contact_info = await fetcher.fetch_contact_info()
            about_brand = await fetcher.fetch_about_brand()
            important_links = await fetcher.fetch_important_links()
            
            if not products:
                raise ShopifyDataError("No products found - may not be a Shopify store")
                
            return {
                "store_url": website_url,
                "product_catalog": products,
                "hero_products": hero_products,
                "privacy_policy": privacy_policy or {"title": "Privacy Policy", "content": "Not found"},
                "return_refund_policy": refund_policy or {"title": "Refund Policy", "content": "Not found"},
                "faqs": faqs,
                "social_handles": social_handles,
                "contact_info": contact_info,
                "about_brand": about_brand,
                "important_links": important_links,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
    except WebsiteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ShopifyDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
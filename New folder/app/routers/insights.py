from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.services.fetcher import ShopifyFetcher
from app.models.schemas import (
    BrandInsightsResponse,
    Policy,
    Product,
    FAQItem,
    SocialHandle,
    ContactInfo
)
from app.models.database import get_db, ShopifyStoreInsights
from sqlalchemy.orm import Session
import uuid
from sqlalchemy import inspect
from app.models.database import Base

router = APIRouter(prefix="/api/v1", tags=["shopify-insights"])

@router.get("/insights", response_model=BrandInsightsResponse)
async def get_shopify_insights(
    website_url: str,
    db: Session = Depends(get_db)
):
    try:
        async with ShopifyFetcher(website_url) as fetcher:
            data = await fetcher.fetch_all_data()
            
            # Convert all objects to JSON-serializable format
            def prepare_for_db(obj):
                if isinstance(obj, BaseModel):
                    return obj.dict()
                elif isinstance(obj, dict):
                    return {k: prepare_for_db(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [prepare_for_db(item) for item in obj]
                return obj
            
            # Prepare database entry
            db_insight = ShopifyStoreInsights(
                id=str(uuid.uuid4()),
                store_url=str(website_url),
                product_catalog=[p.dict() for p in data["products"]],
                hero_products=[p.dict() for p in data["hero_products"]],
                privacy_policy=data["policies"].get("privacy", {}).dict(),
                return_refund_policy=data["policies"].get("refund", {}).dict(),
                faqs=[f.dict() for f in data["faqs"]],
                social_handles=[s.dict() for s in data["social_handles"]],
                contact_info=data["contact_info"].dict(),
                about_brand=data["about_brand"],
                important_links={k: str(v) for k, v in data["important_links"].items()},
                competitors=[],
                fetched_at=datetime.utcnow()
            )
            
            db.add(db_insight)
            db.commit()
            
            return BrandInsightsResponse(
                store_url=website_url,
                product_catalog=data["products"],
                hero_products=data["hero_products"],
                privacy_policy=data["policies"].get("privacy", 
                    Policy(title="Privacy Policy", content="Not found")),
                return_refund_policy=data["policies"].get("refund", 
                    Policy(title="Refund Policy", content="Not found")),
                faqs=data["faqs"],
                social_handles=data["social_handles"],
                contact_info=data["contact_info"],
                about_brand=data["about_brand"],
                important_links=data["important_links"],
                fetched_at=datetime.utcnow()
            )
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
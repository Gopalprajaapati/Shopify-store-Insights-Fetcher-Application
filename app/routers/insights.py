from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.services.fetcher import ShopifyFetcher
from app.services.competitor_analysis import CompetitorAnalyzer
from app.models.schemas import BrandInsightsResponse, CompetitorAnalysisResponse
from app.utils.exceptions import WebsiteNotFoundError, ShopifyDataError
from app.models.database import get_db, ShopifyStoreInsights
from sqlalchemy.orm import Session
import uuid

router = APIRouter(prefix="/api/v1", tags=["shopify-insights"])


router = APIRouter(prefix="/api/v1", tags=["shopify-insights"])



@router.get("/insights", response_model=BrandInsightsResponse)
async def get_shopify_insights(
    website_url: str,
    db: Session = Depends(get_db)
):
    try:
        async with ShopifyFetcher(website_url) as fetcher:
            data = await fetcher.fetch_all_data()
            
            # Save to database
            db_insight = ShopifyStoreInsights(
                id=str(uuid.uuid4()),
                store_url=website_url,
                product_catalog=[p.dict() for p in data["products"]],
                hero_products=[p.dict() for p in data["hero_products"]],
                privacy_policy=data["policies"].get("privacy", {}),
                return_refund_policy=data["policies"].get("refund", {}),
                faqs=[f.dict() for f in data["faqs"]],
                social_handles=[s.dict() for s in data["social_handles"]],
                contact_info=data["contact_info"].dict(),
                about_brand=data["about_brand"],
                important_links=data["important_links"]
            )
            db.add(db_insight)
            db.commit()
            
            return {
                "store_url": website_url,
                "product_catalog": data["products"],
                "hero_products": data["hero_products"],
                "privacy_policy": data["policies"].get("privacy", Policy(title="Privacy Policy", content="Not found")),
                "return_refund_policy": data["policies"].get("refund", Policy(title="Refund Policy", content="Not found")),
                "faqs": data["faqs"],
                "social_handles": data["social_handles"],
                "contact_info": data["contact_info"],
                "about_brand": data["about_brand"],
                "important_links": data["important_links"],
                "fetched_at": datetime.utcnow().isoformat()
            }
            
    except WebsiteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ShopifyDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/insights-with-competitors", response_model=CompetitorAnalysisResponse)
async def get_insights_with_competitors(
    website_url: str,
    db: Session = Depends(get_db)
):
    try:
        # Get main store insights
        main_insights = await get_shopify_insights(website_url, db)
        
        # Get competitors
        async with ShopifyFetcher(website_url) as fetcher:
            analyzer = CompetitorAnalyzer(fetcher)
            competitors = await analyzer.find_competitors()
        
        # Get insights for each competitor
        competitor_insights = []
        for competitor_url in competitors:
            try:
                competitor_data = await get_shopify_insights(competitor_url, db)
                competitor_insights.append(competitor_data)
            except Exception:
                continue
                
        # Update main insights with competitors
        db_insight = db.query(ShopifyStoreInsights).filter(
            ShopifyStoreInsights.store_url == website_url
        ).first()
        if db_insight:
            db_insight.competitors = [c.dict() for c in competitor_insights]
            db.commit()
                
        return {
            **main_insights.dict(),
            "original_store": website_url,
            "competitors": competitor_insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
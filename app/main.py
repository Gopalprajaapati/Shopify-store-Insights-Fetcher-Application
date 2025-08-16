from fastapi import FastAPI
from app.routers import insights
from app.config import settings

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="API to fetch insights from Shopify stores without using the official API",
    version="1.0.0"
)

app.include_router(insights.router)

@app.get("/")
async def root():
    return {"message": "Shopify Store Insights Fetcher API"}
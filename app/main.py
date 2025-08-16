from fastapi import FastAPI
from app.routers import insights
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="API to fetch insights from Shopify stores without using official API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insights.router)

@app.get("/")
async def root():
    return {"message": "Shopify Store Insights Fetcher API"}
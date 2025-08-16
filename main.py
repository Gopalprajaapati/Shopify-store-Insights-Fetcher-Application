from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl, ValidationError
from api.routes import router
from typing import Optional

app = FastAPI(
    title="Shopify Insights Fetcher",
    description="API to fetch structured data from Shopify stores without official API.",
    version="1.0.0"
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Shopify Insights Fetcher API. Go to /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
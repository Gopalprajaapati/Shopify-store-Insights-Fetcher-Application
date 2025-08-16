# shopify_insights_app/config.py

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Shopify Insights Fetcher"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "shopify")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "shopifypassword")
    DB_NAME: str = os.getenv("DB_NAME", "shopify_insights_db")
    
    # URL-encode the password to handle special characters
    ENCODED_PASSWORD: str = quote_plus(DB_PASSWORD)
    
    # Construct DATABASE_URL
    DATABASE_URL: str = f"mysql+mysqlconnector://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    DEFAULT_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT: int = 10  # seconds

settings = Settings()
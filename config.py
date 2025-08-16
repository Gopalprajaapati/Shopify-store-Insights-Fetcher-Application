# shopify_insights_app/config.py

import os
from dotenv import load_dotenv


load_dotenv()  # ⬅️ Load variables from .env into the environment


class Settings:
    PROJECT_NAME: str = "Shopify Insights Fetcher"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database settings
    # Example for MySQL: "mysql+mysqlconnector://user:password@host:port/database_name"
    # Make sure to replace user, password, host, port, and database_name with your actual MySQL credentials
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+mysqlconnector://shopify:shopifypassword@localhost:3306/shopify_insights_db") 
    
    DEFAULT_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT: int = 10 # seconds

settings = Settings()



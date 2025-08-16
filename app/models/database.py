from sqlalchemy import create_engine, Column, String, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

Base = declarative_base()

class ShopifyStoreInsights(Base):
    __tablename__ = "shopify_store_insights"
    
    id = Column(String(36), primary_key=True)
    store_url = Column(String(512), unique=True, nullable=False)
    product_catalog = Column(JSON)
    hero_products = Column(JSON)
    privacy_policy = Column(JSON)
    return_refund_policy = Column(JSON)
    faqs = Column(JSON)
    social_handles = Column(JSON)
    contact_info = Column(JSON)
    about_brand = Column(Text)
    important_links = Column(JSON)
    competitors = Column(JSON)
    fetched_at = Column(DateTime, default=datetime.utcnow)

# Database connection
DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
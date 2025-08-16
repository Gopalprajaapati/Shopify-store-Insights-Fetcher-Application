# shopify_insights_app/database/models.py

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import TEXT, LONGTEXT
from datetime import datetime
from config import settings

# Create a base class for declarative models
Base = declarative_base()

# Define the database connection
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BrandDB(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), unique=True, index=True, nullable=False)
    brand_name = Column(String(255), nullable=True)
    brand_text_context = Column(LONGTEXT, nullable=True)
    last_fetched = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("ProductDB", back_populates="brand", cascade="all, delete-orphan")
    hero_products_rel = relationship("HeroProductDB", back_populates="brand", cascade="all, delete-orphan")
    #privacy_policy = relationship("PolicyDB", back_populates="brand_privacy", uselist=False, cascade="all, delete-orphan")
    privacy_policy = relationship(
        "PolicyDB",
        back_populates="brand_privacy",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="[PolicyDB.brand_privacy_id]" # <--- ADD THIS
    )
    #return_refund_policy = relationship("PolicyDB", back_populates="brand_return_refund", uselist=False, cascade="all, delete-orphan")
    return_refund_policy = relationship(
        "PolicyDB",
        back_populates="brand_return_refund",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="[PolicyDB.brand_return_refund_id]" # <--- ADD THIS
    )
    faqs = relationship("FAQItemDB", back_populates="brand", cascade="all, delete-orphan")
    social_handles = relationship("SocialHandleDB", back_populates="brand", cascade="all, delete-orphan")
    contact_details = relationship("ContactDetailsDB", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    important_links = relationship("ImportantLinkDB", back_populates="brand", cascade="all, delete-orphan")

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    title = Column(String(255), nullable=False)
    price = Column(String(50), nullable=True) # Storing as string as original Pydantic model
    currency = Column(String(10), nullable=True)
    image_url = Column(TEXT, nullable=True)
    product_url = Column(TEXT, nullable=True)
    description = Column(LONGTEXT, nullable=True)

    brand = relationship("BrandDB", back_populates="products")

class HeroProductDB(Base):
    __tablename__ = "hero_products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    title = Column(String(255), nullable=False)
    price = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=True)
    image_url = Column(TEXT, nullable=True)
    product_url = Column(TEXT, nullable=True)

    brand = relationship("BrandDB", back_populates="hero_products_rel")

class PolicyDB(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    brand_privacy_id = Column(Integer, ForeignKey("brands.id"), nullable=True) # For privacy policy
    brand_return_refund_id = Column(Integer, ForeignKey("brands.id"), nullable=True) # For return/refund policy
    
    title = Column(String(255), nullable=False)
    content = Column(LONGTEXT, nullable=False)
    url = Column(TEXT, nullable=True)
    policy_type = Column(String(50), nullable=False) # 'privacy' or 'return_refund'

    brand_privacy = relationship("BrandDB", foreign_keys=[brand_privacy_id], back_populates="privacy_policy")
    brand_return_refund = relationship("BrandDB", foreign_keys=[brand_return_refund_id], back_populates="return_refund_policy")

class FAQItemDB(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    question = Column(TEXT, nullable=False)
    answer = Column(LONGTEXT, nullable=False)

    brand = relationship("BrandDB", back_populates="faqs")

class ContactDetailsDB(Base):
    __tablename__ = "contact_details"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), unique=True, nullable=False)
    emails = Column(TEXT, nullable=True)  # Store as comma-separated string or JSON string
    phone_numbers = Column(TEXT, nullable=True) # Store as comma-separated string or JSON string

    brand = relationship("BrandDB", back_populates="contact_details")

class SocialHandleDB(Base):
    __tablename__ = "social_handles"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    url = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)

    brand = relationship("BrandDB", back_populates="social_handles")

class ImportantLinkDB(Base):
    __tablename__ = "important_links"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    text = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)

    brand = relationship("BrandDB", back_populates="important_links")

# Function to create tables (call this once to set up your database)
def create_db_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created or already exist.")

# Optional: Call this function on application startup or manually
if __name__ == "__main__":
    create_db_tables()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Gopal@143"
    DB_NAME: str = "shopify_insights"
    
    class Config:
        env_file = ".env"

settings = Settings()
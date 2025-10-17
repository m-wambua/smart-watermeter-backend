import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application configuration and environment variables."""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mpesa_transactions.db")

    # M-Pesa credentials
    CONSUMER_KEY: str = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET: str = os.getenv("CONSUMER_SECRET")
    SHORTCODE: str = os.getenv("SHORTCODE")
    NGROK_URL: str = os.getenv("NGROK_URL")

settings = Settings()

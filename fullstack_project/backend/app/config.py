# Configuration for email and app settings.

from pydantic_settings import BaseSettings
from typing import Optional

# Email and App Configuration
class Settings(BaseSettings):    
    # Email settings (SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = ""  # Set in .env (e.g., noreply@myapp.com) -> test?
    SENDER_PASSWORD: str = ""  # Set in .env (app-specific password for Gmail) -> 123?
    
    # Email display name
    SENDER_NAME: str = "TheDebuggers Library Notifications"
    
    # App settings
    APP_NAME: str = "TheDebuggers Library"
    APP_EMAIL: str = "noreply@TheDebuggersLibrary.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

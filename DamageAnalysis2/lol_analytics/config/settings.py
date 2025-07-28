"""Configuration management using Pydantic settings."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    riot_api_key: str = Field(..., env="RIOT_API_KEY")
    riot_region: str = Field("americas", env="RIOT_REGION")
    api_rate_limit: int = Field(50, env="API_RATE_LIMIT")
    api_timeout: int = Field(30, env="API_TIMEOUT")
    
    # Database Configuration
    database_url: str = Field("sqlite:///lol_analytics.db", env="DATABASE_URL")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field("logs/analytics.log", env="LOG_FILE")
    
    # Application Configuration
    debug: bool = Field(False, env="DEBUG")
    data_dir: Path = Field(Path("data"), env="DATA_DIR")
    cache_ttl: int = Field(3600, env="CACHE_TTL")  # seconds
    
    @validator("riot_api_key")
    def validate_api_key(cls, v):
        """Validate API key format."""
        if not v or v == "your_riot_api_key_here":
            raise ValueError("Valid Riot API key is required")
        if not v.startswith("RGAPI-"):
            raise ValueError("API key must start with 'RGAPI-'")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator("data_dir")
    def validate_data_dir(cls, v):
        """Ensure data directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
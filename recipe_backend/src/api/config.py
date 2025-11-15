import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    app_name: str = Field(default="Recipe & Meal Planner API", description="Application name")
    debug: bool = Field(default=os.getenv("DEBUG", "false").lower() == "true", description="Debug mode")
    # Make API key optional so the app can start and expose health/basic endpoints without it
    spoonacular_api_key: Optional[str] = Field(default=os.getenv("SPOONACULAR_API_KEY"), description="Spoonacular API key from environment")
    api_base_url: str = Field(default="https://api.spoonacular.com", description="Spoonacular API base URL")
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
        description="CORS allowed origins (comma separated)"
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_allow_methods: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_METHODS", "*").split(","),
        description="CORS allowed methods (comma separated)"
    )
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_HEADERS", "*").split(","),
        description="CORS allowed headers (comma separated)"
    )
    request_timeout_seconds: float = Field(
        default=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")),
        description="HTTP client request timeout in seconds"
    )
    # Frontend envs referenced by orchestrator; not required for backend functionality
    frontend_url: Optional[str] = Field(default=os.getenv("REACT_APP_FRONTEND_URL"), description="Frontend base URL")
    backend_url: Optional[str] = Field(default=os.getenv("REACT_APP_BACKEND_URL"), description="Backend public URL")


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings loaded from the environment."""
    # Do not raise if the API key is missing; endpoints that require it will handle errors gracefully.
    return Settings()

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers_recipes import router as recipes_router
from .routers_mealplan import router as mealplan_router
from .spoonacular_client import SpoonacularClient
from .state import set_spoonacular_client, get_spoonacular_client

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Recipe search and Meal Planning using Spoonacular.",
    version="0.1.0",
    contact={"name": "Recipe Planner", "url": "https://example.com"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "Health", "description": "Service health and diagnostics"},
        {"name": "Recipes", "description": "Search and retrieve recipes"},
        {"name": "Meal Plan", "description": "Generate meal plans"},
    ],
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins] if settings.cors_allow_origins else ["*"],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=[m.strip() for m in settings.cors_allow_methods] if settings.cors_allow_methods else ["*"],
    allow_headers=[h.strip() for h in settings.cors_allow_headers] if settings.cors_allow_headers else ["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize resources on startup (Spoonacular client)."""
    client = SpoonacularClient()
    await client.startup()
    set_spoonacular_client(app, client)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Cleanup resources on shutdown."""
    client = get_spoonacular_client(app)
    await client.shutdown()


# Routers
app.include_router(recipes_router)
app.include_router(mealplan_router)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check() -> Dict[str, str]:
    """Health check endpoint to verify service is running."""
    return {"message": "Healthy"}

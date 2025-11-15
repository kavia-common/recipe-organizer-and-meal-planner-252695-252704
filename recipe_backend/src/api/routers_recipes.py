from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from .spoonacular_client import SpoonacularClient, SpoonacularError
from .state import get_spoonacular_client

router = APIRouter(prefix="/recipes", tags=["Recipes"])


# PUBLIC_INTERFACE
@router.get(
    "/search",
    summary="Search recipes",
    description="Search for recipes using Spoonacular's complexSearch endpoint.",
    responses={
        200: {"description": "Recipes returned"},
        400: {"description": "Invalid parameters"},
        502: {"description": "Upstream API error"},
    },
)
async def search_recipes(
    q: str = Query(..., description="Search query"),
    number: int = Query(10, ge=1, le=50, description="Number of results to return"),
    diet: Optional[str] = Query(None, description="Dietary filter, e.g., vegetarian, vegan, keto"),
    client: SpoonacularClient = Depends(get_spoonacular_client),
):
    """Perform a recipe search with optional diet filter.

    Returns a plain JSON-serializable dictionary passthrough from Spoonacular.
    """
    try:
        data = await client.search_recipes(query=q, number=number, diet=diet)
        return data
    except SpoonacularError as e:
        raise HTTPException(status_code=502, detail={"message": str(e), "upstream_status": e.status_code})


# PUBLIC_INTERFACE
@router.get(
    "/{recipe_id}",
    summary="Get recipe details",
    description="Fetch detailed information of a recipe by ID.",
    responses={
        200: {"description": "Recipe information"},
        404: {"description": "Recipe not found"},
        502: {"description": "Upstream API error"},
    },
)
async def get_recipe_details(
    recipe_id: int,
    include_nutrition: bool = Query(False, description="Include nutrition data in the response"),
    client: SpoonacularClient = Depends(get_spoonacular_client),
):
    """Get recipe information from Spoonacular and return JSON payload."""
    try:
        return await client.get_recipe_information(recipe_id, include_nutrition=include_nutrition)
    except SpoonacularError as e:
        status = 404 if e.status_code == 404 else 502
        raise HTTPException(status_code=status, detail={"message": str(e), "upstream_status": e.status_code})


# PUBLIC_INTERFACE
@router.get(
    "/{recipe_id}/nutrition",
    summary="Get recipe nutrition",
    description="Fetch nutrition widget data for a recipe.",
    responses={
        200: {"description": "Nutrition widget JSON"},
        404: {"description": "Recipe not found"},
        502: {"description": "Upstream API error"},
    },
)
async def get_recipe_nutrition(
    recipe_id: int,
    client: SpoonacularClient = Depends(get_spoonacular_client),
):
    """Get nutrition widget JSON from Spoonacular for a recipe and return JSON payload."""
    try:
        return await client.get_recipe_nutrition(recipe_id)
    except SpoonacularError as e:
        status = 404 if e.status_code == 404 else 502
        raise HTTPException(status_code=status, detail={"message": str(e), "upstream_status": e.status_code})

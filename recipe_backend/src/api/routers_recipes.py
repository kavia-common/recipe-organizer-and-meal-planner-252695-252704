from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .spoonacular_client import SpoonacularClient, SpoonacularError
from .state import get_spoonacular_client

router = APIRouter(prefix="/recipes", tags=["Recipes"])


class RecipeSummary(BaseModel):
    """Minimal recipe summary for search results."""
    id: int = Field(..., description="Recipe ID")
    title: str = Field(..., description="Recipe title")
    image: Optional[str] = Field(default=None, description="Image URL")
    imageType: Optional[str] = Field(default=None, description="Image type/extension")


class SearchResponse(BaseModel):
    """Response shape for Spoonacular complexSearch proxy."""
    results: List[RecipeSummary] = Field(default_factory=list, description="Recipe summaries")
    offset: Optional[int] = Field(default=None, description="Pagination offset")
    number: Optional[int] = Field(default=None, description="Number of results returned")
    totalResults: Optional[int] = Field(default=None, description="Total matching results")


# PUBLIC_INTERFACE
@router.get(
    "/search",
    summary="Search recipes",
    description="Search for recipes using Spoonacular's complexSearch endpoint.",
    response_model=SearchResponse,
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
    """
    Perform a recipe search with optional diet filter.
    Returns Spoonacular complexSearch payload coerced into SearchResponse.
    """
    try:
        data = await client.search_recipes(query=q, number=number, diet=diet)
        # Coerce incoming JSON into typed response. Unknown fields in results are ignored.
        return SearchResponse(**data)
    except SpoonacularError as e:
        raise HTTPException(status_code=502, detail={"message": str(e), "upstream_status": e.status_code})


# PUBLIC_INTERFACE
@router.get(
    "/{recipe_id}",
    summary="Get recipe details",
    description="Fetch detailed information of a recipe by ID.",
    response_model=None,
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
    """Get recipe information from Spoonacular."""
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
    response_model=None,
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
    """Get nutrition widget JSON from Spoonacular for a recipe."""
    try:
        return await client.get_recipe_nutrition(recipe_id)
    except SpoonacularError as e:
        status = 404 if e.status_code == 404 else 502
        raise HTTPException(status_code=status, detail={"message": str(e), "upstream_status": e.status_code})

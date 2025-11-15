from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from .spoonacular_client import SpoonacularClient, SpoonacularError
from .state import get_spoonacular_client

router = APIRouter(prefix="/mealplan", tags=["Meal Plan"])


# PUBLIC_INTERFACE
@router.get(
    "/generate",
    summary="Generate meal plan",
    description="Generate a day or week meal plan using Spoonacular.",
    responses={
        200: {"description": "Meal plan generated"},
        400: {"description": "Invalid parameters"},
        502: {"description": "Upstream API error"},
    },
)
async def generate_meal_plan(
    time_frame: str = Query("day", pattern="^(day|week)$", description="Timeframe to generate meal plan for: day or week"),
    target_calories: Optional[int] = Query(None, ge=800, le=5000, description="Target daily calories"),
    diet: Optional[str] = Query(None, description="Dietary preference (e.g., vegetarian, keto)"),
    exclude: Optional[str] = Query(None, description="Comma-separated ingredients to exclude"),
    client: SpoonacularClient = Depends(get_spoonacular_client),
) -> Dict[str, Any]:
    """Generate a meal plan using Spoonacular's mealplanner/generate endpoint.

    Returns:
        Dict[str, Any]: JSON object of the generated meal plan as returned by Spoonacular.
    """
    try:
        return await client.generate_meal_plan(
            time_frame=time_frame, target_calories=target_calories, diet=diet, exclude=exclude
        )
    except SpoonacularError as e:
        raise HTTPException(status_code=502, detail={"message": str(e), "upstream_status": e.status_code})

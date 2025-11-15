from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel, Field

from .config import get_settings


class SpoonacularError(Exception):
    """Raised when Spoonacular API returns an error response."""

    def __init__(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class _Timeouts(BaseModel):
    connect: float = Field(default=5.0)
    read: float = Field(default=10.0)
    write: float = Field(default=10.0)
    pool: float = Field(default=5.0)


class SpoonacularClient:
    """Async client for interacting with Spoonacular API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.api_base_url.rstrip("/")
        self._api_key = settings.spoonacular_api_key
        t = settings.request_timeout_seconds
        self._timeouts = _Timeouts(connect=t, read=t, write=t, pool=t)
        self._client: Optional[httpx.AsyncClient] = None

    # PUBLIC_INTERFACE
    async def startup(self) -> None:
        """Initialize the underlying HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Accept": "application/json"},
            timeout=httpx.Timeout(
                connect=self._timeouts.connect,
                read=self._timeouts.read,
                write=self._timeouts.write,
                pool=self._timeouts.pool,
            ),
        )

    # PUBLIC_INTERFACE
    async def shutdown(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("SpoonacularClient not initialized. Call startup() before making requests.")
        merged_params = {"apiKey": self._api_key}
        if params:
            merged_params.update(params)

        resp = await self._client.get(path, params=merged_params)
        if resp.status_code >= 400:
            try:
                data = resp.json()
            except Exception:
                data = {"message": resp.text}
            msg = data.get("message") or data.get("status") or "Spoonacular API error"
            raise SpoonacularError(resp.status_code, msg, details=data)
        return resp.json()

    # PUBLIC_INTERFACE
    async def search_recipes(self, query: str, number: int = 10, diet: Optional[str] = None) -> Dict[str, Any]:
        """Search recipes by query text with optional diet filter."""
        params: Dict[str, Any] = {"query": query, "number": number}
        if diet:
            params["diet"] = diet
        return await self._get("/recipes/complexSearch", params=params)

    # PUBLIC_INTERFACE
    async def get_recipe_information(self, recipe_id: int, include_nutrition: bool = False) -> Dict[str, Any]:
        """Fetch detailed information for a recipe."""
        path = f"/recipes/{recipe_id}/information"
        params = {"includeNutrition": str(include_nutrition).lower()}
        return await self._get(path, params=params)

    # PUBLIC_INTERFACE
    async def get_recipe_nutrition(self, recipe_id: int) -> Dict[str, Any]:
        """Fetch nutrition widget data for a recipe."""
        path = f"/recipes/{recipe_id}/nutritionWidget.json"
        return await self._get(path)

    # PUBLIC_INTERFACE
    async def generate_meal_plan(self, time_frame: str = "day", target_calories: Optional[int] = None,
                                 diet: Optional[str] = None, exclude: Optional[str] = None) -> Dict[str, Any]:
        """Generate a meal plan for a day or week."""
        params: Dict[str, Any] = {"timeFrame": time_frame}
        if target_calories is not None:
            params["targetCalories"] = target_calories
        if diet:
            params["diet"] = diet
        if exclude:
            params["exclude"] = exclude
        return await self._get("/mealplanner/generate", params=params)

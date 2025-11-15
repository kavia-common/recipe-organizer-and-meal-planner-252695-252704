from typing import cast, Optional

from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from .spoonacular_client import SpoonacularClient


SPOONACULAR_CLIENT_KEY = "spoonacular_client"


def set_spoonacular_client(app: FastAPI, client: SpoonacularClient) -> None:
    """Attach the Spoonacular client to app state."""
    app.state.__setattr__(SPOONACULAR_CLIENT_KEY, client)


# PUBLIC_INTERFACE
def get_spoonacular_client(request: Request) -> SpoonacularClient:
    """FastAPI dependency to retrieve the Spoonacular client from app state.

    This dependency is request-based so it can access the current application's state.
    If the client is not initialized (e.g., missing API key), raise a 503 to indicate
    the service is not ready for Spoonacular-backed operations.
    """
    app: FastAPI = request.app  # type: ignore[assignment]
    client: Optional[SpoonacularClient] = getattr(app.state, SPOONACULAR_CLIENT_KEY, None)
    if client is None:
        raise HTTPException(status_code=503, detail={"message": "Spoonacular client is not initialized"})
    return cast(SpoonacularClient, client)

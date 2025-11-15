from typing import cast

from fastapi import FastAPI

from .spoonacular_client import SpoonacularClient


SPOONACULAR_CLIENT_KEY = "spoonacular_client"


def set_spoonacular_client(app: FastAPI, client: SpoonacularClient) -> None:
    """Attach the Spoonacular client to app state."""
    app.state.__setattr__(SPOONACULAR_CLIENT_KEY, client)


# PUBLIC_INTERFACE
def get_spoonacular_client(app: FastAPI) -> SpoonacularClient:  # type: ignore[override]
    """FastAPI dependency to retrieve the Spoonacular client from app state."""
    client = getattr(app.state, SPOONACULAR_CLIENT_KEY, None)
    if client is None:
        raise RuntimeError("Spoonacular client is not initialized")
    return cast(SpoonacularClient, client)

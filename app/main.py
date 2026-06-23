from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import List
from app.service import AutocompleteService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppState:
    """État partagé de l'application, injectable dans les routes."""
    def __init__(self):
        self.service: AutocompleteService | None = None


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.service = AutocompleteService()
    logger.info("Service d'auto-complétion initialisé")
    yield
    state.service = None
    logger.info("Service d'auto-complétion arrêté")


app = FastAPI(lifespan=lifespan)


@app.get("/autocomplete", response_model=List[str])
def autocomplete(query: str):
    logger.info(f"query: {query}")
    if state.service is None:
        raise RuntimeError("Service non initialisé")
    return state.service.autocomplete(query)
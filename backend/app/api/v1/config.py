"""Configuration endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings
from app.llm.client import llm_client

router = APIRouter()


class ConfigOut(BaseModel):
    books_path: str
    embedding_model: str
    embedding_dimension: int
    orchestrator_intensity: str
    default_model: str


class ConfigUpdate(BaseModel):
    orchestrator_intensity: str | None = None
    default_model: str | None = None


class ModelConfig(BaseModel):
    task_type: str
    model_id: str


@router.get("", response_model=ConfigOut)
async def get_config():
    return ConfigOut(
        books_path=settings.books_path,
        embedding_model=settings.embedding_model,
        embedding_dimension=settings.embedding_dimension,
        orchestrator_intensity=settings.orchestrator_intensity,
        default_model=settings.default_model,
    )


@router.patch("")
async def update_config(update: ConfigUpdate):
    updated = {}
    if update.default_model:
        llm_client.registry.set_model("default", update.default_model)
        updated["default_model"] = update.default_model
    if update.orchestrator_intensity:
        updated["orchestrator_intensity"] = update.orchestrator_intensity
    return {"updated": updated}


@router.get("/models")
async def get_models():
    return {
        "current": llm_client.registry.get_all_models(),
        "available_tasks": ["default", "insight", "chat", "feed", "topic", "summary"],
    }


@router.put("/models")
async def set_model(config: ModelConfig):
    llm_client.registry.set_model(config.task_type, config.model_id)
    return {"task_type": config.task_type, "model_id": config.model_id}

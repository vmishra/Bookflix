"""Model registry - maps task types to OpenRouter models."""
from app.config import settings


class ModelRegistry:
    def __init__(self):
        self._overrides: dict[str, str] = {}
        self._defaults = {
            "default": settings.default_model,
            "insight": settings.default_model,
            "chat": settings.default_model,
            "feed": settings.default_model,
            "topic": settings.default_model,
            "summary": settings.default_model,
        }

    def get_model(self, task_type: str) -> str:
        if task_type in self._overrides:
            return self._overrides[task_type]
        return self._defaults.get(task_type, self._defaults["default"])

    def set_model(self, task_type: str, model_id: str):
        self._overrides[task_type] = model_id

    def get_all_models(self) -> dict[str, str]:
        result = dict(self._defaults)
        result.update(self._overrides)
        return result

    def reset(self, task_type: str | None = None):
        if task_type:
            self._overrides.pop(task_type, None)
        else:
            self._overrides.clear()

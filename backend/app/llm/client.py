"""Model-agnostic LLM client via OpenRouter."""
import logging
from openai import AsyncOpenAI
from app.config import settings
from app.llm.models import ModelRegistry

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self.registry = ModelRegistry()

    async def complete(
        self,
        messages: list[dict],
        task_type: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> str:
        model = self.registry.get_model(task_type)
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM call failed (model={model}, task={task_type}): {e}")
            raise

    async def complete_stream(
        self,
        messages: list[dict],
        task_type: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ):
        model = self.registry.get_model(task_type)
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"LLM stream failed (model={model}, task={task_type}): {e}")
            raise


llm_client = LLMClient()

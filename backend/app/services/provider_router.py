"""Provider Router: Manages primary execution and approved fallback chains."""

from typing import Any, AsyncGenerator
from app.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import logger
from app.services.llm_service import LLMService

settings = get_settings()


class ProviderRouter:
    def __init__(self, llm_service: LLMService | None = None):
        self.llm = llm_service or LLMService()
        self.primary_model = settings.CHAT_PRIMARY_MODEL
        self.fallback_models = settings.fallback_models_list

    async def execute_with_fallback(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """Tries primary model first; if transient provider error occurs, falls back sequentially."""
        models_to_try = [self.primary_model] + self.fallback_models
        last_error = None

        for model in models_to_try:
            try:
                logger.info("Routing chat query to model: %s", model)
                result = await self.llm.generate_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return result
            except Exception as exc:
                last_error = exc
                logger.warning("Model %s failed: %s. Trying next configured fallback...", model, str(exc)[:100])
                continue

        logger.error("All configured AI providers failed: %s", last_error)
        raise AIProviderError(
            "Our AI services are temporarily unavailable due to high demand. Please try again in a few moments."
        )

    async def execute_stream_with_fallback(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> tuple[AsyncGenerator[str, None], str, str]:
        """Tries models sequentially, verifying connection on the first token before returning the generator."""
        models_to_try = [self.primary_model] + self.fallback_models
        last_error = None

        for model in models_to_try:
            try:
                provider_name = model.split("/")[0] if "/" in model else "unknown"
                logger.info("Attempting streaming completion with model: %s", model)
                raw_gen = self.llm.stream_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Pre-flight the stream by fetching the first token to verify provider connection
                first_token = await anext(raw_gen, None)

                # Chain the first token with remaining stream
                async def chained_gen(first: str | None, gen: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
                    if first is not None:
                        yield first
                    async for token in gen:
                        yield token

                logger.info("Streaming stream established successfully with model: %s", model)
                return chained_gen(first_token, raw_gen), model, provider_name

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Stream initiation failed for model %s: %s. Trying next configured fallback...",
                    model,
                    str(exc)[:120],
                )
                continue

        logger.error("All configured streaming providers failed: %s", last_error)
        raise AIProviderError(f"Stream generation failed: {last_error}")


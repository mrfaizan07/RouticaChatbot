"""AI Provider service powered by LiteLLM supporting Gemini, Groq, and OpenRouter."""

import asyncio
import os
import random
import time
from typing import Any, AsyncGenerator

# Prevent LiteLLM from making outbound HTTP requests to github for cost maps
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

import litellm

from app.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import logger

settings = get_settings()

# Tone down third-party LiteLLM logging
litellm.suppress_debug_info = True


class LLMService:
    def __init__(self):
        self.groq_keys = [k for k in [settings.GROQ_API_KEY, settings.GROQ_API_KEY1] if k]
        self._groq_index = 0
        self._configure_api_keys()

    def _configure_api_keys(self) -> None:
        """Injects API keys into litellm configuration and os.environ."""
        if settings.GEMINI_API_KEY:
            litellm.gemini_key = settings.GEMINI_API_KEY
            os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
        if self.groq_keys:
            active_groq = self.groq_keys[0]
            litellm.groq_key = active_groq
            os.environ["GROQ_API_KEY"] = active_groq
        if settings.OPENROUTER_API_KEY:
            litellm.openrouter_key = settings.OPENROUTER_API_KEY
            os.environ["OPENROUTER_API_KEY"] = settings.OPENROUTER_API_KEY

    def rotate_groq_key(self) -> str | None:
        """Rotates to the next available Groq API key."""
        if len(self.groq_keys) > 1:
            self._groq_index = (self._groq_index + 1) % len(self.groq_keys)
            new_key = self.groq_keys[self._groq_index]
            litellm.groq_key = new_key
            os.environ["GROQ_API_KEY"] = new_key
            logger.info("Rotated to alternate Groq API key index: %d", self._groq_index)
            return new_key
        return self.groq_keys[0] if self.groq_keys else None

    def _get_api_key_for_model(self, model: str) -> str | None:
        model_lower = model.lower()
        if "gemini" in model_lower:
            return settings.GEMINI_API_KEY or None
        if "groq" in model_lower:
            if self.groq_keys:
                return self.groq_keys[self._groq_index % len(self.groq_keys)]
            return settings.GROQ_API_KEY or None
        if "openrouter" in model_lower:
            return settings.OPENROUTER_API_KEY or None
        return None

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> dict[str, Any]:
        """Executes LLM completion with controlled exponential backoff with jitter."""
        if settings.APP_ENV == "testing":
            # Mock LLM completion in testing mode
            return {
                "content": "This is a verified test response regarding Routica products and solutions.",
                "model": model,
                "provider": model.split("/")[0] if "/" in model else "mock",
                "usage": {"total_tokens": 150},
            }

        api_key = self._get_api_key_for_model(model)
        custom_provider = None
        if model.startswith("gemini/"):
            custom_provider = "gemini"
        elif model.startswith("groq/"):
            custom_provider = "groq"
        elif model.startswith("openrouter/"):
            custom_provider = "openrouter"

        for attempt in range(max_retries + 1):
            try:
                start_t = time.perf_counter()
                completion_kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "timeout": timeout,
                    "api_key": api_key,
                }
                if custom_provider:
                    completion_kwargs["custom_llm_provider"] = custom_provider

                response = await litellm.acompletion(**completion_kwargs)
                duration_ms = round((time.perf_counter() - start_t) * 1000, 2)
                content = response.choices[0].message.content or ""
                provider_name = model.split("/")[0] if "/" in model else "unknown"

                logger.info(
                    "LLM completion succeeded",
                    extra={"model": model, "provider": provider_name, "duration_ms": duration_ms},
                )

                return {
                    "content": content,
                    "model": model,
                    "provider": provider_name,
                    "usage": dict(response.get("usage", {})),
                }
            except Exception as exc:
                error_msg = str(exc)
                logger.warning(
                    "LLM attempt %d failed for model %s: %s",
                    attempt + 1,
                    model,
                    error_msg[:120],
                )
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    backoff = (2**attempt) * 0.5 + random.uniform(0.1, 0.4)
                    await asyncio.sleep(backoff)
                else:
                    raise AIProviderError(f"Provider request failed for {model}: {error_msg[:100]}")

    async def stream_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """Streams LLM tokens using LiteLLM asynchronous streaming."""
        if settings.APP_ENV == "testing":
            # Mock streaming in testing
            for word in ["Routica ", "Explorer ", "II ", "supports ", "high-speed ", "5G ", "connectivity."]:
                yield word
                await asyncio.sleep(0.01)
            return

        api_key = self._get_api_key_for_model(model)
        custom_provider = None
        if model.startswith("gemini/"):
            custom_provider = "gemini"
        elif model.startswith("groq/"):
            custom_provider = "groq"
        elif model.startswith("openrouter/"):
            custom_provider = "openrouter"

        try:
            stream_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                "api_key": api_key,
            }
            if custom_provider:
                stream_kwargs["custom_llm_provider"] = custom_provider

            response = await litellm.acompletion(**stream_kwargs)
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as exc:
            if "groq" in model.lower():
                self.rotate_groq_key()
            logger.error("Streaming error for model %s: %s", model, exc)
            raise AIProviderError(f"Stream generation failed: {exc}")
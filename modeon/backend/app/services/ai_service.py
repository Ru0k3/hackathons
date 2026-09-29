"""
Modeon — AI Service

Wraps Azure OpenAI chat completions with:
  - Dual clients: GPT-4o-mini (primary) and GPT-4o (retry/fallback)
  - Retry-up strategy: mini → large on any failure
  - JSON response parsing with markdown fence stripping
  - Token usage and error tracking via PostHog
"""

import json
import logging
from typing import Any

from fastapi import HTTPException
from openai import AzureOpenAI

from app.config import settings
from app.services.analytics import track

logger = logging.getLogger("modeon.ai_service")

# PROMPTS is loaded at startup in main.py and shared globally.
# We import the module so we always access the live dict.
import app.main as _main_module


def _get_prompts() -> dict[str, Any]:
    return _main_module.PROMPTS


def _strip_markdown_fences(text: str) -> str:
    """Remove leading/trailing ```json or ``` fences from model output."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence line
        newline = text.find("\n")
        if newline != -1:
            text = text[newline + 1:]
        # Remove closing fence
        if text.endswith("```"):
            text = text[: text.rfind("```")].rstrip()
    return text.strip()


class AIService:
    def __init__(self) -> None:
        self.client_mini = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-01",
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_MINI,
        )
        self.client_large = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-01",
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_LARGE,
        )
        logger.info(
            "AIService initialised (mini=%s, large=%s)",
            settings.AZURE_OPENAI_DEPLOYMENT_MINI,
            settings.AZURE_OPENAI_DEPLOYMENT_LARGE,
        )

    def _call(
        self,
        client: AzureOpenAI,
        deployment: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
        temperature: float,
        timeout: float,
    ) -> tuple[dict[str, Any], str, int, int]:
        """
        Make a synchronous chat completion call.
        Returns (parsed_dict, model_name, prompt_tokens, completion_tokens).
        Raises on any error.
        """
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )
        raw_text: str = response.choices[0].message.content or ""
        cleaned = _strip_markdown_fences(raw_text)
        parsed = json.loads(cleaned)

        prompt_tokens: int = response.usage.prompt_tokens if response.usage else 0
        completion_tokens: int = response.usage.completion_tokens if response.usage else 0

        return parsed, deployment, prompt_tokens, completion_tokens

    async def complete(
        self,
        prompt_key: str,
        user_message: str,
        timeout: float = 5.0,
        use_large_model: bool = False,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a chat completion for the given prompt key.

        Strategy:
          1. Attempt with client_mini (unless use_large_model=True).
          2. On any failure: log, track error, retry once with client_large.
          3. If retry also fails: log, track, raise HTTP 503.
          4. On success: track token usage to PostHog.
        """
        prompts = _get_prompts()
        if prompt_key not in prompts:
            logger.error("Prompt key '%s' not found in PROMPTS dict.", prompt_key)
            raise HTTPException(
                status_code=500,
                detail=f"AI prompt configuration missing for '{prompt_key}'.",
            )

        config: dict[str, Any] = prompts[prompt_key]
        system_prompt: str = config["system"]
        max_tokens: int = int(config.get("max_tokens", 1000))
        temperature: float = float(config.get("temperature", 0.7))

        primary_client = self.client_large if use_large_model else self.client_mini
        primary_deployment = (
            settings.AZURE_OPENAI_DEPLOYMENT_LARGE
            if use_large_model
            else settings.AZURE_OPENAI_DEPLOYMENT_MINI
        )

        # ── First attempt ──────────────────────────────────────────────────────
        try:
            parsed, model_used, prompt_tokens, completion_tokens = self._call(
                client=primary_client,
                deployment=primary_deployment,
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )
            track(
                user_id or "anonymous",
                "ai_token_usage",
                {
                    "endpoint": prompt_key,
                    "model": model_used,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                },
            )
            return parsed

        except Exception as first_exc:
            model_label = "large" if use_large_model else "mini"
            logger.warning(
                "AI first attempt failed for prompt='%s', model='%s': %s: %s",
                prompt_key,
                model_label,
                type(first_exc).__name__,
                first_exc,
            )
            track(
                user_id or "anonymous",
                "ai_inference_error",
                {
                    "endpoint": prompt_key,
                    "error_type": type(first_exc).__name__,
                    "model": model_label,
                },
            )

        # ── Retry with large model ─────────────────────────────────────────────
        try:
            parsed, model_used, prompt_tokens, completion_tokens = self._call(
                client=self.client_large,
                deployment=settings.AZURE_OPENAI_DEPLOYMENT_LARGE,
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )
            track(
                user_id or "anonymous",
                "ai_token_usage",
                {
                    "endpoint": prompt_key,
                    "model": model_used,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                },
            )
            return parsed

        except Exception as retry_exc:
            logger.error(
                "AI retry also failed for prompt='%s', model='large': %s: %s",
                prompt_key,
                type(retry_exc).__name__,
                retry_exc,
            )
            track(
                user_id or "anonymous",
                "ai_inference_error",
                {
                    "endpoint": prompt_key,
                    "error_type": type(retry_exc).__name__,
                    "model": "large",
                },
            )
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable",
            )


# ── Module-level singleton ─────────────────────────────────────────────────────
ai_service: AIService = AIService()

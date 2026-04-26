"""
Backward-compatible Azure OpenAI wrapper exports.

The primary implementation lives in `app.services.ai_service`.
"""

from __future__ import annotations

import json

from openai import AsyncAzureOpenAI

from app.config import settings
from app.services.ai_service import AIService, ai_service


def _client(deployment: str) -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
        azure_deployment=deployment,
        api_version="2024-02-01",
    )


async def chat_complete(
    messages: list,
    model: str = "mini",
    max_tokens: int = 1024,
) -> str:
    """
    Compatibility helper for older call sites.
    """
    chat_json = getattr(ai_service, "chat_json", None)
    if callable(chat_json):
        payload = await chat_json(messages, model=model, max_tokens=max_tokens)
        return payload if isinstance(payload, str) else json.dumps(payload)

    deployment = (
        settings.AZURE_OPENAI_DEPLOYMENT_MINI
        if model == "mini"
        else settings.AZURE_OPENAI_DEPLOYMENT_LARGE
    )
    resp = await _client(deployment).chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content or ""


async def vision_complete(image_url: str, prompt: str) -> dict:
    """
    Compatibility helper for older call sites.
    """
    vision_json = getattr(ai_service, "vision_json", None)
    if callable(vision_json):
        return await vision_json(image_url, prompt)

    deployment = settings.AZURE_OPENAI_DEPLOYMENT_LARGE
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]
    resp = await _client(deployment).chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=1024,
        temperature=0.5,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw": content}


__all__ = ["AIService", "ai_service", "chat_complete", "vision_complete"]

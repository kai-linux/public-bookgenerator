"""GPT-5.6 Terra routing contracts extracted from the production generator.

This module deliberately contains no credentials or network client. It makes
the provider order and request-shaping rules executable and reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


OFFICIAL_TERRA_MODEL = "gpt-5.6-terra"
OPENROUTER_TERRA_MODEL = "openai/gpt-5.6-terra"


@dataclass(frozen=True)
class ProviderRoute:
    provider: str
    model: str


def pro_provider_chain() -> tuple[ProviderRoute, ...]:
    """Prefer OpenAI and fail over only to the same model family."""
    return (
        ProviderRoute("openai", OFFICIAL_TERRA_MODEL),
        ProviderRoute("openrouter", OPENROUTER_TERRA_MODEL),
    )


def model_family(model: str) -> str:
    """Normalize provider-specific prefixes without weakening model identity."""
    return str(model or "").strip().lower().removeprefix("openai/")


def failover_preserves_model_family(routes: Iterable[ProviderRoute]) -> bool:
    families = {model_family(route.model) for route in routes}
    return families == {OFFICIAL_TERRA_MODEL}


def openai_supports_custom_sampling(model: str) -> bool:
    """Terra rejects legacy non-default sampling controls on Chat Completions."""
    return OFFICIAL_TERRA_MODEL not in model_family(model)


def build_openai_request(
    *,
    model: str,
    messages: Iterable[Mapping[str, str]],
    temperature: float = 0.75,
    top_p: float | None = None,
    response_format: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply only controls supported by the selected official OpenAI model.

    Production discovered that sending Terra legacy sampling fields caused a
    deterministic HTTP 400 before provider failover. For Terra, the stable
    structural fields remain while custom sampling controls are omitted.
    """
    body: dict[str, Any] = {
        "model": model,
        "messages": [dict(message) for message in messages],
    }
    if response_format is not None:
        body["response_format"] = dict(response_format)

    if openai_supports_custom_sampling(model):
        body.update(
            {
                "temperature": temperature,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.1,
            }
        )
        if top_p is not None:
            body["top_p"] = top_p
    return body

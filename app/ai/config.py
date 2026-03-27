from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    label: str
    env_key_name: str
    env_model_name: str
    default_model: str
    supported_models: List[str]


PROVIDERS: Dict[str, ProviderConfig] = {
    "openai": ProviderConfig(
        provider_id="openai",
        label="OpenAI",
        env_key_name="OPENAI_API_KEY",
        env_model_name="OPENAI_MODEL",
        default_model="gpt-5",
        supported_models=["gpt-5", "gpt-5-mini", "gpt-4.1"],
    ),
    "anthropic": ProviderConfig(
        provider_id="anthropic",
        label="Claude",
        env_key_name="ANTHROPIC_API_KEY",
        env_model_name="ANTHROPIC_MODEL",
        default_model="claude-sonnet-4-20250514",
        supported_models=[
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest",
        ],
    ),
}


DEFAULT_PROVIDER = "openai"


def get_provider_config(provider_id: str | None) -> ProviderConfig:
    key = (provider_id or os.getenv("COPILOT_PROVIDER") or DEFAULT_PROVIDER).strip().lower()
    return PROVIDERS.get(key, PROVIDERS[DEFAULT_PROVIDER])


def get_provider_api_key(provider_id: str | None) -> str | None:
    config = get_provider_config(provider_id)
    return os.getenv(config.env_key_name)


def get_provider_model(provider_id: str | None, requested_model: str | None = None) -> str:
    config = get_provider_config(provider_id)
    if requested_model and requested_model.strip():
        return requested_model.strip()
    return os.getenv(config.env_model_name, config.default_model)


def serialize_provider_catalog() -> List[dict]:
    items = []
    for provider in PROVIDERS.values():
        items.append(
            {
                "id": provider.provider_id,
                "label": provider.label,
                "default_model": provider.default_model,
                "models": provider.supported_models,
                "configured": bool(os.getenv(provider.env_key_name)),
                "env_key_name": provider.env_key_name,
                "env_model_name": provider.env_model_name,
            }
        )
    return items

from __future__ import annotations

import json
from typing import Any, Callable, Dict

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.ai.config import get_provider_config, serialize_provider_catalog
from app.ai.providers import run_anthropic, run_openai
from app.ai.tools_registry import build_tool_specs, default_filters, resolve_tool


class CopilotRequest(BaseModel):
    message: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    current_tab: str = "Summary"
    current_view: str = "Summary"
    mode: str = "Diagnose"
    context: Dict[str, Any] = Field(default_factory=dict)
    conversation: list[dict[str, str]] = Field(default_factory=list)
    provider: str | None = None
    model: str | None = None


class CopilotService:
    def __init__(self, handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]):
        self.handlers = handlers
        self.tool_specs = build_tool_specs()

    def provider_catalog(self) -> list[dict]:
        return serialize_provider_catalog()

    def _make_prompt(self, request: CopilotRequest, filters: Dict[str, Any]) -> str:
        history_lines = []
        for msg in request.conversation[-6:]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_lines.append(f'{role}: {content}')

        return f"""
Mode: {request.mode}
Current tab: {request.current_tab}
Current view: {request.current_view}
Current filters: {json.dumps(filters, ensure_ascii=False)}
Context snapshot: {json.dumps(request.context or {}, ensure_ascii=False)}
Conversation history:
{chr(10).join(history_lines) if history_lines else 'No prior conversation.'}

User question:
{request.message}
""".strip()

    def _execute_tool(self, filters: Dict[str, Any], name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.handlers:
            raise HTTPException(status_code=400, detail=f'Unknown copilot tool: {name}')
        return resolve_tool(name, filters, args, self.handlers)

    def chat(self, request: CopilotRequest) -> dict[str, Any]:
        filters = default_filters(request.filters)
        provider = get_provider_config(request.provider)
        prompt = self._make_prompt(request, filters)

        def executor(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
            return self._execute_tool(filters, name, args)

        if provider.provider_id == 'openai':
            return run_openai(
                prompt=prompt,
                tool_specs=self.tool_specs,
                tool_executor=executor,
                requested_model=request.model,
            )
        if provider.provider_id == 'anthropic':
            return run_anthropic(
                prompt=prompt,
                conversation=request.conversation,
                tool_specs=self.tool_specs,
                tool_executor=executor,
                requested_model=request.model,
            )

        raise HTTPException(status_code=400, detail='Unsupported provider.')

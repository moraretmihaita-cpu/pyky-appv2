from __future__ import annotations

import json
from typing import Any, Callable

from fastapi import HTTPException

from app.ai.config import get_provider_api_key, get_provider_model


SYSTEM_PROMPT = (
    'You are an internal analytics copilot for AI Ads Analyst. '
    'You MUST answer only using the provided internal tools, current filters, context snapshot, and their outputs. '
    'Do not claim to browse the web or use any external source. '
    'Adapt the answer to the requested mode: Explain, Diagnose, Recommend, or Compare. '
    'When needed, call one or more tools, then answer using these exact sections: '
    'Summary, Evidence, Probable cause, Recommended actions, Estimated impact, Confidence. '
    'Confidence must be one of: ridicată, medie, scăzută. '
    'Be explicit when data is missing, when the context is partial, or when you are making an inference. '
    'Keep the answer concise, analytical, and action-oriented.'
)


def _extract_openai_output_text(response: Any) -> str:
    text = getattr(response, 'output_text', None)
    if text:
        return text
    parts = []
    for item in getattr(response, 'output', []) or []:
        if getattr(item, 'type', '') == 'message':
            for content in getattr(item, 'content', []) or []:
                if getattr(content, 'type', '') == 'output_text':
                    parts.append(getattr(content, 'text', ''))
    return '\n'.join([p for p in parts if p]).strip()


def _extract_anthropic_text(message: Any) -> str:
    parts = []
    for block in getattr(message, 'content', []) or []:
        if getattr(block, 'type', '') == 'text':
            parts.append(getattr(block, 'text', ''))
    return '\n'.join([p for p in parts if p]).strip()


def _anthropic_tools(tool_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            'name': tool['name'],
            'description': tool['description'],
            'input_schema': tool['parameters'],
        }
        for tool in tool_specs
    ]


def run_openai(
    *,
    prompt: str,
    tool_specs: list[dict[str, Any]],
    tool_executor: Callable[[str, dict[str, Any]], dict[str, Any]],
    requested_model: str | None,
) -> dict[str, Any]:
    api_key = get_provider_api_key('openai')
    if not api_key:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY is not configured.')
    try:
        from openai import OpenAI
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'OpenAI SDK missing: {exc}')

    client = OpenAI(api_key=api_key)
    model = get_provider_model('openai', requested_model)
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=prompt,
        tools=tool_specs,
        max_output_tokens=1200,
    )

    used_tools: list[str] = []
    for _ in range(6):
        tool_calls = [item for item in (response.output or []) if getattr(item, 'type', '') == 'function_call']
        if not tool_calls:
            break
        outputs = []
        for call in tool_calls:
            args = json.loads(call.arguments or '{}')
            result = tool_executor(call.name, args)
            used_tools.append(call.name)
            outputs.append({'type': 'function_call_output', 'call_id': call.call_id, 'output': json.dumps(result, ensure_ascii=False)[:120000]})
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            previous_response_id=response.id,
            input=outputs,
            tools=tool_specs,
            max_output_tokens=1200,
        )

    return {'answer': _extract_openai_output_text(response), 'tools_used': list(dict.fromkeys(used_tools)), 'model': model, 'provider': 'openai'}


def run_anthropic(
    *,
    prompt: str,
    conversation: list[dict[str, str]],
    tool_specs: list[dict[str, Any]],
    tool_executor: Callable[[str, dict[str, Any]], dict[str, Any]],
    requested_model: str | None,
) -> dict[str, Any]:
    api_key = get_provider_api_key('anthropic')
    if not api_key:
        raise HTTPException(status_code=500, detail='ANTHROPIC_API_KEY is not configured.')
    try:
        from anthropic import Anthropic
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Anthropic SDK missing: {exc}')

    client = Anthropic(api_key=api_key)
    model = get_provider_model('anthropic', requested_model)

    messages = []
    for msg in conversation[-6:]:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if role in ['user', 'assistant'] and content:
            messages.append({'role': role, 'content': content})
    messages.append({'role': 'user', 'content': prompt})

    used_tools: list[str] = []
    final_message = None
    for _ in range(6):
        response = client.messages.create(
            model=model,
            system=SYSTEM_PROMPT,
            max_tokens=1200,
            messages=messages,
            tools=_anthropic_tools(tool_specs),
        )
        final_message = response
        tool_uses = [block for block in response.content if getattr(block, 'type', '') == 'tool_use']
        if not tool_uses:
            break

        messages.append({'role': 'assistant', 'content': response.content})
        tool_results = []
        for block in tool_uses:
            args = getattr(block, 'input', {}) or {}
            result = tool_executor(block.name, args)
            used_tools.append(block.name)
            tool_results.append({'type': 'tool_result', 'tool_use_id': block.id, 'content': json.dumps(result, ensure_ascii=False)[:120000]})
        messages.append({'role': 'user', 'content': tool_results})

    return {'answer': _extract_anthropic_text(final_message) if final_message else '', 'tools_used': list(dict.fromkeys(used_tools)), 'model': model, 'provider': 'anthropic'}

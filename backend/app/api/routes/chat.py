"""Chat routes using the Vercel AI stream protocol."""

from __future__ import annotations

from json import JSONDecodeError, loads
from typing import Any, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_entity_service, get_graph_service, get_investigation_service
from app.core.chat.agent import (
    EntityReadService,
    GraphReadService,
    InvestigationChatDeps,
    get_investigation_chat_agent,
)

try:
    from pydantic_ai.ui.vercel_ai import VercelAIAdapter
except ImportError:  # pragma: no cover - optional dependency until installed
    VercelAIAdapter = None

router = APIRouter()
investigation_service_dep = Depends(get_investigation_service)
entity_service_dep = Depends(get_entity_service)
graph_service_dep = Depends(get_graph_service)


class InvestigationLookup(Protocol):
    """Minimal interface required for investigation lookup."""

    def get(self, investigation_id: str) -> object | None: ...


def _investigation_id_from_payload(payload: dict[str, Any]) -> str | None:
    raw_id = payload.get("investigationId")
    if not isinstance(raw_id, str):
        return None
    value = raw_id.strip()
    return value or None


@router.post("/")
async def chat(
    request: Request,
    investigation_service: InvestigationLookup = investigation_service_dep,
    entity_service: EntityReadService = entity_service_dep,
    graph_service: GraphReadService = graph_service_dep,
) -> object:
    """Stream investigation chat responses via Vercel AI Data Stream protocol."""
    if VercelAIAdapter is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat support is unavailable: install pydantic-ai",
        )

    raw_body = await request.body()
    try:
        payload = loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat payload")

    investigation_id = _investigation_id_from_payload(payload)
    if investigation_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: investigationId",
        )

    investigation = investigation_service.get(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    deps = InvestigationChatDeps(
        investigation_id=investigation_id,
        entity_service=entity_service,
        graph_service=graph_service,
    )

    try:
        agent = get_investigation_chat_agent()
    except Exception as exc:  # pragma: no cover - depends on environment config
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Chat agent initialization failed: {exc}",
        ) from exc

    return await VercelAIAdapter.dispatch_request(
        request,
        agent=agent,
        deps=deps,
    )

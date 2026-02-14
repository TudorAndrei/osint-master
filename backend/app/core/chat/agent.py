"""Investigation chat agent built with Pydantic AI."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from pydantic_ai import Agent, RunContext

from app.config import settings
from app.models.entity import DuplicateCandidate, Entity, EntityExpand  # noqa: TC001
from app.models.graph import GraphPage  # noqa: TC001

SYSTEM_INSTRUCTIONS = """
You are an OSINT investigation assistant.

Rules:
- You are read-only. Never propose that you executed writes.
- Never create, update, merge, delete, or ingest data.
- Use tools to answer factual questions about the active investigation.
- If a user asks for write operations, explain that the assistant is read-only
  and provide safe manual steps.
- Keep answers concise and grounded in returned tool results.
- When users ask for summaries, use available tools and provide a useful summary.
""".strip()


@dataclass(frozen=True)
class InvestigationChatDeps:
    """Dependencies used by the investigation chat agent."""

    investigation_id: str
    entity_service: EntityReadService
    graph_service: GraphReadService


class EntityReadService(Protocol):
    """Entity read operations required by the chat agent."""

    def list(self, investigation_id: str, search: str | None = None) -> list[Entity]: ...

    def get(self, investigation_id: str, entity_id: str) -> Entity | None: ...

    def expand(self, investigation_id: str, entity_id: str) -> EntityExpand | None: ...

    def find_duplicates(
        self,
        investigation_id: str,
        schema: str | None = None,
        threshold: float = 0.7,
        limit: int = 100,
    ) -> list[DuplicateCandidate]: ...


class GraphReadService(Protocol):
    """Graph read operations required by the chat agent."""

    def get_graph_page(
        self, investigation_id: str, skip: int = 0, limit: int = 500
    ) -> GraphPage: ...


@lru_cache
def get_investigation_chat_agent() -> Agent[InvestigationChatDeps]:
    """Create and cache the investigation chat agent instance."""
    model_id = settings.chat_model_id.strip() or f"google-gla:{settings.extract_model_id}"
    if settings.gemini_api_key and not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    agent = Agent[InvestigationChatDeps](
        model_id,
        deps_type=InvestigationChatDeps,
        instructions=SYSTEM_INSTRUCTIONS,
    )

    @agent.tool
    def list_entities(
        ctx: RunContext[InvestigationChatDeps],
        search: str | None = None,
        limit: int = 50,
    ) -> list[Entity]:
        """List entities from the current investigation, optionally filtered by text."""
        safe_limit = max(1, min(limit, 200))
        entities = ctx.deps.entity_service.list(ctx.deps.investigation_id, search=search)
        return entities[:safe_limit]

    @agent.tool
    def get_entity(
        ctx: RunContext[InvestigationChatDeps],
        entity_id: str,
    ) -> Entity | None:
        """Get one entity by ID from the current investigation."""
        return ctx.deps.entity_service.get(ctx.deps.investigation_id, entity_id)

    @agent.tool
    def expand_entity(
        ctx: RunContext[InvestigationChatDeps],
        entity_id: str,
    ) -> EntityExpand | None:
        """Get an entity, its neighbors, and connecting edges."""
        return ctx.deps.entity_service.expand(ctx.deps.investigation_id, entity_id)

    @agent.tool
    def get_graph_page(
        ctx: RunContext[InvestigationChatDeps],
        skip: int = 0,
        limit: int = 200,
    ) -> GraphPage:
        """Get paginated graph nodes and edges for the current investigation."""
        safe_skip = max(0, skip)
        safe_limit = max(1, min(limit, 500))
        return ctx.deps.graph_service.get_graph_page(
            ctx.deps.investigation_id,
            skip=safe_skip,
            limit=safe_limit,
        )

    @agent.tool
    def find_duplicate_candidates(
        ctx: RunContext[InvestigationChatDeps],
        schema: str | None = None,
        threshold: float = 0.7,
        limit: int = 50,
    ) -> list[DuplicateCandidate]:
        """Find potential duplicate entity pairs for manual review."""
        safe_threshold = max(0.0, min(threshold, 1.0))
        safe_limit = max(1, min(limit, 200))
        return ctx.deps.entity_service.find_duplicates(
            ctx.deps.investigation_id,
            schema=schema,
            threshold=safe_threshold,
            limit=safe_limit,
        )

    @agent.tool
    def summarize_investigation(
        ctx: RunContext[InvestigationChatDeps],
        sample_limit: int = 200,
    ) -> dict[str, object]:
        """Return a compact investigation summary for assistant responses."""
        safe_limit = max(20, min(sample_limit, 500))
        page = ctx.deps.graph_service.get_graph_page(
            ctx.deps.investigation_id,
            skip=0,
            limit=safe_limit,
        )
        schema_counts = Counter(node.schema_ for node in page.nodes)
        top_nodes = [
            {
                "id": node.id,
                "label": node.label,
                "schema": node.schema_,
            }
            for node in page.nodes[:10]
        ]
        top_edges = [
            {
                "source": edge.source,
                "target": edge.target,
                "schema": edge.schema_,
            }
            for edge in page.edges[:10]
        ]
        return {
            "investigation_id": ctx.deps.investigation_id,
            "total_nodes": page.total_nodes,
            "total_edges": page.total_edges,
            "sampled_nodes": len(page.nodes),
            "sampled_edges": len(page.edges),
            "schema_counts": dict(schema_counts.most_common(10)),
            "sample_nodes": top_nodes,
            "sample_edges": top_edges,
        }

    return agent

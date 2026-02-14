# Investigation Graph as Memory (Single-DB Approach)

## Goal

- Treat investigative memory and case relations as one graph in FalkorDB, not separate memory storage.

## Core Approach

- Use FalkorDB as the single source of truth for both case facts and agent memory.
- Represent memory as first-class graph objects: Entity, Observation, Claim, Event, ConversationTurn, Source, Hypothesis.
- Add metadata to every relation: provenance, confidence, created_by, case_id, created_at, updated_at.
- Keep strict facts and exploratory intel in the same graph with different labels/status values.

## Suggested Graph Pattern

- (:Observation)-[:ABOUT]->(:Entity)
- (:Observation)-[:DERIVED_FROM]->(:Source)
- (:Claim)-[:SUPPORTED_BY]->(:Observation)
- (:Entity)-[:RELATED_TO {type, confidence, status}]->(:Entity)
- status values: proposed | corroborated | disputed

## Agent/Chatbot Benefits

- Retrieval is case-aware graph traversal instead of external memory lookup.
- "Show me why" is possible through provenance chains.
- Analysts can promote/demote inferred links without losing history.

## Risk Controls

- Attach source/provenance to every node and edge written by agents.
- Keep confidence scores and evidence counts for relation quality.
- Enforce tenant/case isolation in all writes and reads.
- Add retention/TTL rules for low-confidence transient memory.

## Recommendation

- Quarantine agent-extracted relations as status=proposed by default.
- Include proposed links only when explicitly requested or in analyst review views.
- Promote to corroborated after validation (human or rule-based).

## Pilot Plan

1. Ingest a bounded set of closed investigations and chat transcripts.
2. Write all extracted relations with provenance/confidence metadata.
3. Evaluate on real queries: link precision, contextual recall, false-association rate, analyst trust.

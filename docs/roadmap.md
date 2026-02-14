# Roadmap

This page captures the current direction for OSINT Master documentation and platform evolution.

## Current focus (MVP foundation)

- Stable multi-investigation graph workflows
- FTM-first ingestion and schema alignment
- Entity exploration, expansion, and merge tooling
- Notebook-based analyst context

## Near-term platform work

- Stronger graph workflow tooling (filters, search depth, expansion controls)
- More import/connect pipelines beyond baseline FTM JSON ingestion
- Improved enrichment and source-linking workflows
- Better operational visibility around ingestion and extraction jobs

## Documentation workstream

- Add endpoint examples and request/response payload samples
- Add contributor onboarding (project conventions, lint/test flow)
- Add architecture decision records for major subsystem choices
- Add deployment guide for persistent infrastructure environments

## Existing planning references

- `AUTH_PLAN.md`
- `COPILOT_PLAN.md`

## Ideas backlog (`docs/ideas/`)

- [`chatbot-tooling-recommendations.md`](ideas/chatbot-tooling-recommendations.md): phased tool rollout for grounded, citation-first investigation chat
- [`ftm-stack-integration-candidates.md`](ideas/ftm-stack-integration-candidates.md): prioritized FollowTheMoney ecosystem integrations and longer-horizon storage/search options
- [`investigation-graph-memory.md`](ideas/investigation-graph-memory.md): single-DB graph memory model with provenance, confidence, and proposed-to-corroborated workflow

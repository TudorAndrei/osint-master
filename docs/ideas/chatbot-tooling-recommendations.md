# Chatbot Tooling Recommendations (LangChain Community Tools)

## Goal

- Add high-value LangChain tools to OSINT Master chat in a way that improves grounded answers, provenance, and analyst trust.

## Product Context

- OSINT Master chat is case-scoped and currently read-only.
- The assistant should prioritize evidence-backed retrieval and avoid unsafe side effects.
- Tool outputs should map cleanly into investigation graph memory concepts (source, confidence, provenance).

## Recommended Tools (Priority Order)

### Tier 1: Immediate high ROI

#### 1) Tavily Search

- Why: Strong default web retrieval for grounded answers.
- Use for: Broad web search with useful snippets and links.
- Expected value: Better factual recall with source URLs for citations.

#### 2) Tavily Extract

- Why: Pulls page content for deeper evidence extraction after search.
- Use for: Expanding top search hits into analyzable text.
- Expected value: Better quote-level support and explainability.

#### 3) Requests Toolkit

- Why: Simple deterministic fetch path for static/public pages.
- Use for: Lightweight URL retrieval when browser automation is unnecessary.
- Expected value: Lower complexity and cost than full browser agents.

#### 4) Wikipedia + Wikidata

- Why: High-signal entity disambiguation and normalization.
- Use for: Resolving ambiguous people/org/place names and IDs.
- Expected value: Improved merge/dedup quality and analyst confidence.

### Tier 2: Add based on case mix

#### 5) Exa Search

- Why: High-quality research-oriented results with metadata.
- Use for: Investigations that need stronger source quality and publication context.

#### 6) Jina Search

- Why: Good low-cost secondary retrieval path with page content.
- Use for: Backstop when primary search misses or rate limits apply.

#### 7) Semantic Scholar / ArXiv / PubMed

- Why: Domain-specific evidence for technical, scientific, and biomedical claims.
- Use for: Cases requiring source authority beyond general web pages.

### Tier 3: Conditional

#### 8) Playwright Browser Toolkit

- Why: Handles JS-heavy pages and interactive content.
- Use for: Targets that fail with simple HTTP fetch.
- Note: Higher operational complexity; add only when needed.

#### 9) OpenAPI Toolkit

- Why: Controlled path to expose planned connectors (OpenCorporates, GLEIF, SEC EDGAR, etc.).
- Use for: Wrapping selected external APIs behind explicit schemas.

## Not Recommended for MVP Chat

- SQLDatabase Toolkit / MCP Toolbox without strict read-only gating.
  - Reason: Broad SQL capability increases accidental write risk.
- Transaction-focused tools (GOAT, Privy, Ampersend).
  - Reason: Out of product scope for investigation chat.
- Broad productivity suites as first additions.
  - Reason: Lower impact than retrieval/provenance for core OSINT workflows.

## Guardrails for Tool Integration

- Enforce investigation isolation on every tool call and response attachment.
- Persist provenance for each claim:
  - source URL
  - retrieval timestamp
  - tool name
  - confidence score
- Default new agent-inferred links to proposed status until analyst validation.
- Redact or avoid storing sensitive key material in entities, logs, or chat transcripts.
- Keep chat toolset read-only by default.

## Suggested Rollout Plan

### Phase 1

- Tavily Search + Tavily Extract
- Requests Toolkit
- Wikipedia + Wikidata

### Phase 2

- Exa Search (or Jina Search as cost-sensitive alternative)
- One domain source pack: Semantic Scholar or ArXiv/PubMed

### Phase 3

- Playwright for JS-heavy targets
- OpenAPI Toolkit wrappers for planned OSINT connectors

## Success Criteria

- Higher answer grounding rate (responses with verifiable citations).
- Improved analyst trust in "show me why" evidence chains.
- Reduced unsupported claims in chat responses.
- No cross-investigation leakage and no write-side effects.

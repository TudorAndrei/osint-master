# Data Sources

This page tracks source integrations and planned connectors for the platform.

## Current integrations

| Source | Type | Status | Notes |
| --- | --- | --- | --- |
| User-provided FTM files (`.ftm`, `.ijson`, `.json`, `.ndjson`) | Structured ingest | Implemented | Primary ingestion path via `/api/investigations/{id}/ingest`. |
| Yente (OpenSanctions-backed index) | Enrichment/search | Implemented | Exposed through `/api/enrich/yente` and `/api/enrich/yente/link/{investigation_id}/{entity_id}`. |
| Uploaded documents (including SEC filing text) | Document extraction | Implemented | Extracted into FTM entities through the extraction workflow. |

## Planned free/public connectors (deduplicated)

| Source | Type | Status | Notes |
| --- | --- | --- | --- |
| OpenCorporates | Company registry | Planned | Entity profile and officer enrichment. |
| GLEIF API | LEI/entity resolution | Planned | Normalize legal entities and cross-border matching. |
| OpenOwnership | Beneficial ownership | Planned | UBO and control graph enrichment. |
| SEC EDGAR | Filings/disclosures | Planned | Direct connector for US public-company filings. |
| UK Companies House API | Company registry | Planned | Directors, PSC, and filing history. |
| GDELT 2.0 | Adverse media/events | Planned | Event stream and risk signal enrichment. |
| SAM.gov Exclusions | Exclusions/debarment | Planned | US procurement risk checks. |
| OSM Overpass API + Nominatim | GEOINT/geocoding | Planned | Geospatial enrichment and location validation. |
| crt.sh | Certificate transparency | Planned | Domain/infrastructure pivoting. |

## Planned optional key-based connectors

| Source | Type | Status | Notes |
| --- | --- | --- | --- |
| Shodan | Infrastructure intelligence | Planned | API-key based connector. Supports platform-wide key and user BYOK mode. |

## Connector policy

- Web-Check is self-hosted and used as a domain/web enrichment source.
- Web-Check ingestion stores only a subsample of results (selected high-signal fields), not the full raw output.
- Shodan integration is optional and API-key gated:
  - platform-wide key for shared deployments,
  - BYOK for user-scoped enrichment.
- BYOK keys must not be persisted in investigation entities or logs.

## Deduplication policy

- OpenSanctions (through Yente) is the canonical sanctions/watchlist feed for MVP.
- Do not add separate default ingestors for lists already covered by OpenSanctions (for example UN and UK OFSI) unless there is a compliance or latency requirement.
- Evaluate direct-source fallbacks only when we need stricter provenance, faster refresh cadence, or a proven coverage gap.

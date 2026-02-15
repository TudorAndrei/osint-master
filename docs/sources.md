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
| OpenCorporates (`occli`) | Company registry | Planned | Entity profile and officer enrichment. |
| GLEIF API | LEI/entity resolution | Planned | Normalize legal entities and cross-border matching. |
| OpenOwnership | Beneficial ownership | Planned | UBO and control graph enrichment. |
| SEC EDGAR | Filings/disclosures | Planned | Direct connector for US public-company filings. |
| UK Companies House API | Company registry | Planned | Directors, PSC, and filing history. |
| GDELT 2.0 | Adverse media/events | Planned | Event stream and risk signal enrichment. |
| SAM.gov Exclusions | Exclusions/debarment | Planned | US procurement risk checks. |
| OSM Overpass API + Nominatim | GEOINT/geocoding | Planned | Geospatial enrichment and location validation. |
| crt.sh | Certificate transparency | Planned | Domain/infrastructure pivoting. |
| Internet Archive (Wayback Machine) + Common Crawl (`waybackpy`/`gau`) | Web archives/historical web | Planned | Historical URL and snapshot enrichment for timeline and infrastructure investigations. |
| DocumentCloud | Document repository | Planned | Ingest public documents into extraction workflows and map entities/relationships to investigations. |
| ICIJ Offshore Leaks | Corporate/leaks datasets | Planned | Offshore entity/officer/shareholder relationship enrichment for cross-border investigations. |
| OCCRP Aleph | Investigative records/documents | Planned | Entity, document, and case enrichment for cross-source investigative graph analysis. |
| CourtListener RECAP Archive | Court records/documents | Planned | Docket and filing ingestion for legal timeline and case-entity relationship enrichment. |
| URLhaus | Threat indicators (URLs) | Planned | Malicious URL feed ingestion for campaign clustering and IOC pivoting. |
| BGPView | ASN/BGP metadata | Planned | ASN, prefix, and routing context enrichment for infrastructure attribution workflows. |
| GeoNames | Geospatial gazetteer | Planned | Normalize location entities and improve place resolution across investigations. |
| passivedns.mnemonic.no | Passive DNS history | Planned | Domain/IP historical pivots for temporal infrastructure relationship analysis. |
| PeeringDB | Network/ASN registry | Planned | Network operator, ASN, and peering context enrichment for attribution workflows. |
| RansomLook | Ransomware events/tracking | Planned | Group/victim event enrichment for campaign and timeline analysis. |
| ACLED | Conflict/event dataset | Planned | Structured geotagged events for adverse-event and actor relationship enrichment. |
| OONI Explorer | Network measurement/censorship | Planned | Country/time/network event evidence for internet-disruption investigations. |
| OpenCellID | Cell tower geodata | Planned | Telecom geospatial enrichment for location and infrastructure pivots. |
| FDIC BankFind | Financial institution registry | Planned | US bank institution profile enrichment for compliance/financial investigations. |
| 990 Finder | Nonprofit filings | Planned | IRS nonprofit filing and officer/organization enrichment. |
| WIPO Global Brand Database | Trademark/IP registry | Planned | Trademark owner and jurisdiction enrichment for ownership/control investigations. |
| MalwareBazaar (abuse.ch) | Malware sample intelligence | Planned | Malware hash/family enrichment for IOC-to-infrastructure and campaign relationship analysis. |
| PhishStats | Phishing feed | Planned | Phishing URL/domain event enrichment for campaign clustering and timeline analysis. |
| Validin | Historical DNS intelligence | Planned | Domain/IP historical resolution enrichment for temporal infrastructure pivots. |
| Cloudflare Radar | Internet telemetry/events | Planned | Macro network and attack trend enrichment for contextual investigation signals. |
| ExoneraTor (Tor Project) | Tor relay history | Planned | Historical Tor exit-node checks for IP attribution and timeline context. |
| Pushshift API | Social archive (Reddit) | Planned | Historical Reddit post/comment enrichment for event and entity timeline analysis. |
| Arctic Shift | Social archive (Reddit) | Planned | Complementary Reddit archival API for backfill and coverage gaps. |

## Planned optional key-based connectors

| Source | Type | Status | Notes |
| --- | --- | --- | --- |
| Shodan | Infrastructure intelligence | Planned | API-key based connector. Supports platform-wide key and user BYOK mode. |
| Netlas | Infrastructure intelligence | Planned | API-key based connector for host/domain/certificate enrichment with optional BYOK mode. |
| urlscan.io | Web/domain telemetry | Planned | API-key based connector for scan artifacts (domains, requests, IPs, certs) and evidence pivots. |
| SecurityTrails | DNS/WHOIS history | Planned | API-key based connector for historical DNS, WHOIS, and domain infrastructure relationships. |
| AbuseIPDB | IP reputation | Planned | API-key based connector for IP abuse reports and risk signal enrichment. |
| Censys | Infrastructure intelligence | Planned | API-key based connector for host/service/certificate discovery and infrastructure pivots. |
| OTX AlienVault | Threat intelligence | Planned | API-key based connector for IOC pulse enrichment (indicators, tags, campaigns). |
| WhoisFreaks | WHOIS history | Planned | API-key based connector for historical WHOIS ownership and domain timeline enrichment. |
| WhoisXML API WHOIS History | WHOIS history | Planned | API-key based connector for long-range registrant and domain history analysis. |
| Pulsedive | Threat intelligence | Planned | API-key based connector for IOC enrichment (domains, IPs, URLs, tags). |
| VirusTotal | Threat intelligence | Planned | API-key based connector for domain/IP/URL/file relationship enrichment and IOC pivoting. |
| GreyNoise | Infrastructure intelligence | Planned | API-key based connector for internet background-noise filtering and IP context enrichment. |
| WiGLE | Wireless geospatial intelligence | Planned | API-key based connector for BSSID/SSID geolocation enrichment and location pivots. |
| FOFA | Infrastructure intelligence | Planned | API-key based connector for host/service exposure discovery and infrastructure pivoting. |
| ZoomEye | Infrastructure intelligence | Planned | API-key based connector for internet asset discovery and exposure correlation. |

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

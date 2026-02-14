# FollowTheMoney Stack Integration Candidates

## Source

- https://followthemoney.tech/community/stack/

## Context

- OSINT Master is FtM-first, with FastAPI backend, FalkorDB graph storage, and planned expansion into extraction pipelines and additional connectors.

## Candidate Tools to Evaluate Later

### High-priority candidates

- rigour (plus normality/prefixdate): data cleaning and normalization during ingestion.
- yente: search and bulk matching API for FtM datasets.
- nomenklatura: statement-level storage and entity resolution workflows.
- ftmq: advanced querying layer over nomenklatura stores.
- ingest-file: build document graphs from source files for investigative workflows.

### Analysis and enrichment candidates

- ftm-analyze: analysis pipeline components (NER/language/processing workflows).
- ftm-transcribe: extract text from audio/video into FtM-compatible entities.
- ftm-geocode: parse and geocode addresses from FtM entities.
- followthemoney-compare: model-assisted cross-reference and entity comparison.
- juditha: reconcile NER output to known FtM entities.

### Interoperability and ingestion candidates

- openaleph-client / alephclient: import/export interoperability with OpenAleph/Aleph APIs.
- memorious (and investigraph fork): lightweight scraping path for FtM-producing collectors.
- zavod / investigraph: structured FtM data production frameworks.
- followthemoney-ocds: OCDS importer.
- followthemoney-cellebrite: Cellebrite forensics importer.

### Storage/search candidates (longer-horizon)

- followthemoney-store: SQL-backed entity fragment store.
- ftm-columnstore: ClickHouse-backed statement store.
- ftmq-api: read-only FastAPI exposure for statement stores.
- ftmq-search: search backend experiments for FtM data.
- ftm-assets: media/image asset storage and resolution.

### Watchlist / not immediate

- bahamut: WIP statement data server with resolution support.
- FollowTheMoney Data Lake (RFC): upcoming architecture, monitor maturity.

### Do not prioritize

- Discontinued/legacy section tools listed on the FtM page.

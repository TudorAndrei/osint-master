#!/usr/bin/env bash
set -euo pipefail

HOST="${DOCS_HOST:-127.0.0.1}"
PORT="${DOCS_PORT:-8002}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

WATCH_DIRS=("${ROOT_DIR}/docs" "${ROOT_DIR}/backend")
if [[ -n "${DOCS_WATCH_DIRS:-}" ]]; then
	IFS=':' read -r -a WATCH_DIRS <<<"${DOCS_WATCH_DIRS}"
fi

WATCH_ARGS=()
for watch_dir in "${WATCH_DIRS[@]}"; do
	if [[ -d "${watch_dir}" ]]; then
		WATCH_ARGS+=(--watch "${watch_dir}")
	fi
done

exec uvx \
	--with mkdocs-material \
	--with "mkdocstrings[python]" \
	--with mkdocs-swagger-ui-tag \
	--with mkdocs-mermaid2-plugin \
	--with mkdocs-include-markdown-plugin \
	--with mkdocs-macros-plugin \
	--with mkdocs-git-revision-date-localized-plugin \
	--from mkdocs \
	mkdocs serve -f "${ROOT_DIR}/mkdocs.yml" -a "${HOST}:${PORT}" --dirtyreload "${WATCH_ARGS[@]}" "$@"

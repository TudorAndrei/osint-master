"""Yente integration service for entity lookup."""

from __future__ import annotations

import json
from typing import Any
from urllib import parse

import httpx
import logfire

from app.config import settings
from app.models.enrich import YenteSearchResponse, YenteSearchResult


class YenteServiceError(Exception):
    """Raised when Yente request fails."""


class YenteService:
    """Search OpenSanctions entities through Yente."""

    @logfire.instrument("request yente json", extract_args=False)
    def _request_json(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        url = f"{settings.yente_url.rstrip('/')}/{path.lstrip('/')}"

        try:
            response = httpx.get(url, params=params, timeout=settings.yente_timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            msg = f"Yente request failed ({exc.response.status_code}): {detail}"
            raise YenteServiceError(msg) from exc
        except (httpx.RequestError, json.JSONDecodeError, ValueError) as exc:
            msg = f"Yente request failed: {exc}"
            raise YenteServiceError(msg) from exc

        if not isinstance(payload, dict):
            msg = "Yente returned an unexpected payload"
            raise YenteServiceError(msg)
        return payload

    @staticmethod
    def _normalize_properties(raw: object) -> dict[str, list[str]]:
        if not isinstance(raw, dict):
            return {}

        properties: dict[str, list[str]] = {}
        for key, value in raw.items():
            if isinstance(value, list):
                properties[str(key)] = [str(item) for item in value if item is not None]
            elif value is None:
                properties[str(key)] = []
            else:
                properties[str(key)] = [str(value)]
        return properties

    @staticmethod
    def _normalize_result(item: dict[str, Any]) -> YenteSearchResult | None:
        entity = item.get("entity") if isinstance(item.get("entity"), dict) else item
        if not isinstance(entity, dict):
            return None

        entity_id = entity.get("id")
        schema_name = entity.get("schema")
        if not entity_id or not schema_name:
            return None

        caption = str(
            entity.get("caption")
            or entity.get("name")
            or (entity.get("properties") or {}).get("name", [entity_id])[0],
        )

        score_value = item.get("score")
        score = float(score_value) if isinstance(score_value, (int, float)) else None

        datasets = entity.get("datasets")
        if isinstance(datasets, list):
            normalized_datasets = [str(dataset) for dataset in datasets]
        else:
            normalized_datasets = []

        properties = YenteService._normalize_properties(entity.get("properties"))

        return YenteSearchResult(
            id=str(entity_id),
            schema=str(schema_name),
            caption=caption,
            score=score,
            datasets=normalized_datasets,
            properties=properties,
        )

    @staticmethod
    def _extract_entity_ids(value: object) -> set[str]:
        ids: set[str] = set()
        if isinstance(value, dict):
            entity_id = value.get("id")
            if isinstance(entity_id, (str, int)):
                ids.add(str(entity_id))
            for nested in value.values():
                ids.update(YenteService._extract_entity_ids(nested))
            return ids

        if isinstance(value, list):
            for nested in value:
                ids.update(YenteService._extract_entity_ids(nested))
        return ids

    def search(self, query: str, limit: int = 20) -> YenteSearchResponse:
        q = query.strip()
        if not q:
            return YenteSearchResponse(query=query, total=0, results=[])

        payload = self._request_json(
            f"search/{parse.quote(settings.yente_dataset, safe='')}",
            params={"q": q, "limit": str(limit)},
        )

        raw_results = payload.get("results", []) if isinstance(payload, dict) else []
        results: list[YenteSearchResult] = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            normalized = self._normalize_result(item)
            if normalized is not None:
                results.append(normalized)

        total = payload.get("total") if isinstance(payload, dict) else None
        if not isinstance(total, int):
            total = len(results)

        return YenteSearchResponse(query=q, total=total, results=results)

    def adjacent_entity_ids(self, entity_id: str) -> list[str]:
        payload = self._request_json(f"entities/{parse.quote(entity_id, safe='')}/adjacent")
        adjacent = payload.get("adjacent")
        if not isinstance(adjacent, dict):
            return []

        linked_ids: set[str] = set()
        for bucket in adjacent.values():
            if not isinstance(bucket, dict):
                continue
            results = bucket.get("results")
            if not isinstance(results, list):
                continue
            for result in results:
                if not isinstance(result, dict):
                    continue
                linked_ids.update(self._extract_entity_ids(result.get("properties", {})))

        linked_ids.discard(entity_id)
        return sorted(linked_ids)

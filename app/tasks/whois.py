from datetime import date, datetime
from typing import Any
from urllib.parse import urlparse

import whois

from app.db import create_entity, get_db, get_entities_by_label, update_entity
from app.models import Domain


def extract_domain_from_url(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path
        hostname = hostname.split(":")[0]
        if hostname:
            return hostname.lower()
    except Exception:  # noqa: BLE001
        pass
    return None


def normalize_date(value: datetime | date | list[Any] | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def fetch_whois_for_url(url: str) -> None:
    domain_name = extract_domain_from_url(url)
    if not domain_name:
        return

    try:
        w: dict[str, Any] = whois.whois(domain_name)
    except Exception:  # noqa: BLE001
        return

    whois_domain_raw = w.get("domain_name")
    if not whois_domain_raw:
        return

    if isinstance(whois_domain_raw, list):
        whois_domain_raw = whois_domain_raw[0]
    whois_domain = str(whois_domain_raw).lower()

    registration_date = normalize_date(w.get("creation_date"))
    expiration_date = normalize_date(w.get("expiration_date"))
    registrar: str | None = w.get("registrar")

    db = get_db()

    existing_domains = get_entities_by_label(db, "Domain")
    existing_domain = next(
        (
            d
            for d in existing_domains
            if str(d.get("domain_name", "")).lower() == whois_domain
        ),
        None,
    )

    if existing_domain:
        updates: dict[str, date | str] = {}
        if registration_date and not existing_domain.get("registration_date"):
            updates["registration_date"] = registration_date
        if expiration_date and not existing_domain.get("expiration_date"):
            updates["expiration_date"] = expiration_date
        if registrar and not existing_domain.get("registrar"):
            updates["registrar"] = registrar
        if updates:
            _ = update_entity(db, "Domain", str(existing_domain["id"]), updates)
    else:
        domain = Domain(
            domain_name=whois_domain,
            registration_date=registration_date,
            expiration_date=expiration_date,
            registrar=registrar,
            description=None,
        )
        _ = create_entity(db, "Domain", domain)

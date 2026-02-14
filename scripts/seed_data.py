#!/usr/bin/env python3
"""
Seed script to populate FalkorDB with sample FTM entities for testing.

Usage:
    uv run python scripts/seed_data.py
"""

import json
from pathlib import Path

# Extraction-supported non-relation schemata.
ENTITY_SCHEMAS = {
    "Person",
    "Company",
    "Organization",
    "Security",
    "Email",
}

# Ingestion-supported relation schemata.
RELATION_SCHEMAS = {
    "Ownership",
    "Directorship",
    "Employment",
    "Associate",
    "Family",
    "Membership",
    "Representation",
    "Payment",
    "UnknownLink",
}

# Sample FTM records covering all supported entity and relation types.
SAMPLE_ENTITIES = [
    {
        "id": "person-john-doe",
        "schema": "Person",
        "properties": {
            "name": ["John Doe"],
            "nationality": ["us"],
            "birthDate": ["1982-03-15"],
        },
    },
    {
        "id": "person-jane-smith",
        "schema": "Person",
        "properties": {
            "name": ["Jane Smith"],
            "nationality": ["gb"],
            "birthDate": ["1985-07-22"],
        },
    },
    {
        "id": "company-acme-corp",
        "schema": "Company",
        "properties": {
            "name": ["ACME Corporation"],
            "jurisdiction": ["us"],
            "incorporationDate": ["2010-01-15"],
        },
    },
    {
        "id": "company-globex",
        "schema": "Company",
        "properties": {
            "name": ["Globex Inc"],
            "jurisdiction": ["de"],
            "incorporationDate": ["2015-06-01"],
        },
    },
    {
        "id": "organization-bezos-trust",
        "schema": "Organization",
        "properties": {
            "name": ["Bezos Family Trust"],
            "classification": ["trust"],
        },
    },
    {
        "id": "security-acme-stock",
        "schema": "Security",
        "properties": {
            "name": ["ACME Common Stock"],
            "ticker": ["ACME"],
            "isin": ["US0000000001"],
        },
    },
    {
        "id": "email-jane-contoso",
        "schema": "Email",
        "properties": {
            "email": ["jane@contoso.com"],
        },
    },
    {
        "id": "site-acme-nyc-hq",
        "schema": "RealEstate",
        "properties": {
            "name": ["ACME HQ"],
            "address": ["123 Main Street, New York, NY 10001"],
            "city": ["New York"],
            "country": ["us"],
            "latitude": ["40.7128"],
            "longitude": ["-74.0060"],
        },
    },
    {
        "id": "site-globex-berlin-office",
        "schema": "RealEstate",
        "properties": {
            "name": ["Globex Berlin Office"],
            "address": ["Alexanderplatz 1, 10178 Berlin"],
            "city": ["Berlin"],
            "country": ["de"],
            "latitude": ["52.5200"],
            "longitude": ["13.4050"],
        },
    },
    {
        "id": "site-acme-singapore-dc",
        "schema": "RealEstate",
        "properties": {
            "name": ["ACME Singapore Data Center"],
            "address": ["10 Marina Boulevard, Singapore"],
            "city": ["Singapore"],
            "country": ["sg"],
            "latitude": ["1.2903"],
            "longitude": ["103.8519"],
        },
    },
    {
        "id": "ownership-john-acme",
        "schema": "Ownership",
        "properties": {
            "owner": ["person-john-doe"],
            "asset": ["company-acme-corp"],
            "percentage": ["51%"],
            "startDate": ["2010-01-15"],
        },
    },
    {
        "id": "directorship-john-globex",
        "schema": "Directorship",
        "properties": {
            "director": ["person-john-doe"],
            "organization": ["company-globex"],
            "role": ["CEO"],
            "startDate": ["2018-01-01"],
        },
    },
    {
        "id": "employment-jane-globex",
        "schema": "Employment",
        "properties": {
            "employee": ["person-jane-smith"],
            "employer": ["company-globex"],
            "role": ["CFO"],
            "startDate": ["2020-05-01"],
        },
    },
    {
        "id": "associate-john-jane",
        "schema": "Associate",
        "properties": {
            "person": ["person-john-doe"],
            "associate": ["person-jane-smith"],
            "summary": ["Frequent business collaborators"],
        },
    },
    {
        "id": "family-john-jane",
        "schema": "Family",
        "properties": {
            "person": ["person-john-doe"],
            "relative": ["person-jane-smith"],
            "relationship": ["sibling"],
        },
    },
    {
        "id": "membership-jane-trust",
        "schema": "Membership",
        "properties": {
            "member": ["person-jane-smith"],
            "organization": ["organization-bezos-trust"],
            "role": ["board member"],
        },
    },
    {
        "id": "representation-john-trust",
        "schema": "Representation",
        "properties": {
            "agent": ["person-john-doe"],
            "client": ["organization-bezos-trust"],
            "role": ["trustee"],
        },
    },
    {
        "id": "payment-globex-acme",
        "schema": "Payment",
        "properties": {
            "payer": ["company-globex"],
            "beneficiary": ["company-acme-corp"],
            "amount": ["1250000"],
            "currency": ["USD"],
            "date": ["2024-11-10"],
        },
    },
    {
        "id": "unknownlink-security-email",
        "schema": "UnknownLink",
        "properties": {
            "subject": ["security-acme-stock"],
            "object": ["email-jane-contoso"],
            "summary": ["Suspicious mention in leaked correspondence"],
        },
    },
    {
        "id": "unknownlink-acme-hq",
        "schema": "UnknownLink",
        "properties": {
            "subject": ["company-acme-corp"],
            "object": ["site-acme-nyc-hq"],
            "summary": ["Company linked to headquarters location"],
        },
    },
    {
        "id": "unknownlink-globex-berlin",
        "schema": "UnknownLink",
        "properties": {
            "subject": ["company-globex"],
            "object": ["site-globex-berlin-office"],
            "summary": ["Company linked to branch office location"],
        },
    },
]


def validate_sample_coverage() -> None:
    """Fail fast if sample records do not cover all target schemata."""
    present = {record["schema"] for record in SAMPLE_ENTITIES}
    missing_entities = sorted(ENTITY_SCHEMAS - present)
    missing_relations = sorted(RELATION_SCHEMAS - present)

    if missing_entities or missing_relations:
        missing_parts: list[str] = []
        if missing_entities:
            missing_parts.append(f"entity schemata: {', '.join(missing_entities)}")
        if missing_relations:
            missing_parts.append(f"relation schemata: {', '.join(missing_relations)}")
        raise RuntimeError(f"Missing schema coverage: {'; '.join(missing_parts)}")


def write_sample_ftm_file():
    """Write sample entities to an FTM JSON file."""
    validate_sample_coverage()
    output_path = Path(__file__).parent / "sample_data.ftm"

    # Write as newline-delimited JSON (FTM format)
    with open(output_path, "w") as f:
        for entity in SAMPLE_ENTITIES:
            f.write(json.dumps(entity) + "\n")

    print(f"Sample FTM data written to: {output_path}")
    print(f"Total entities: {len(SAMPLE_ENTITIES)}")


if __name__ == "__main__":
    write_sample_ftm_file()

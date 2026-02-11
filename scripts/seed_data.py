#!/usr/bin/env python3
"""
Seed script to populate FalkorDB with sample FTM entities for testing.

Usage:
    uv run python scripts/seed_data.py
"""

import json
from pathlib import Path

# Sample FTM entities for testing
SAMPLE_ENTITIES = [
    {
        "id": "person-john-doe",
        "schema": "Person",
        "properties": {
            "name": ["John Doe", "J. Doe"],
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
            "name": ["ACME Corporation", "ACME Corp"],
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
        "id": "ownership-jane-acme",
        "schema": "Ownership",
        "properties": {
            "owner": ["person-jane-smith"],
            "asset": ["company-acme-corp"],
            "percentage": ["49%"],
            "startDate": ["2012-03-01"],
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
        "id": "address-hq",
        "schema": "RealEstate",
        "properties": {
            "name": ["HQ"],
            "address": ["123 Main Street, New York, NY 10001"],
            "city": ["New York"],
            "country": ["us"],
            "latitude": ["40.7128"],
            "longitude": ["-74.0060"],
        },
    },
    {
        "id": "address-berlin",
        "schema": "RealEstate",
        "properties": {
            "name": ["Berlin Office"],
            "address": ["Alexanderplatz 1, 10178 Berlin"],
            "city": ["Berlin"],
            "country": ["de"],
            "latitude": ["52.5200"],
            "longitude": ["13.4050"],
        },
    },
    {
        "id": "occupancy-acme-hq",
        "schema": "Occupancy",
        "properties": {
            "occupant": ["company-acme-corp"],
            "asset": ["address-hq"],
            "status": ["current"],
        },
    },
    {
        "id": "occupancy-globex-berlin",
        "schema": "Occupancy",
        "properties": {
            "occupant": ["company-globex"],
            "asset": ["address-berlin"],
            "status": ["current"],
        },
    },
]


def write_sample_ftm_file():
    """Write sample entities to an FTM JSON file."""
    output_path = Path(__file__).parent / "sample_data.ftm"

    # Write as newline-delimited JSON (FTM format)
    with open(output_path, "w") as f:
        for entity in SAMPLE_ENTITIES:
            f.write(json.dumps(entity) + "\n")

    print(f"Sample FTM data written to: {output_path}")
    print(f"Total entities: {len(SAMPLE_ENTITIES)}")


if __name__ == "__main__":
    write_sample_ftm_file()

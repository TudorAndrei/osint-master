"""Logfire setup and instrumentation helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logfire

from app.config import settings

if TYPE_CHECKING:
    from fastapi import FastAPI


def configure_logfire() -> None:
    """Configure Logfire and global library instrumentation."""
    environment = settings.logfire_environment.strip() or (
        "development" if settings.debug else "production"
    )

    if settings.logfire_token:
        logfire.configure(
            service_name=settings.logfire_service_name,
            service_version="0.1.0",
            environment=environment,
            send_to_logfire=True,
            token=settings.logfire_token,
        )
    else:
        logfire.configure(
            service_name=settings.logfire_service_name,
            service_version="0.1.0",
            environment=environment,
            send_to_logfire=False,
        )

    logfire.instrument_httpx()
    logfire.instrument_pydantic()
    logfire.instrument_pydantic_ai()


def instrument_fastapi(app: FastAPI) -> None:
    """Instrument FastAPI app."""
    logfire.instrument_fastapi(app)

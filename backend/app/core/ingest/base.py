"""Base ingestor interface."""

from abc import ABC, abstractmethod
from collections.abc import Iterator


class BaseIngestor(ABC):
    """Abstract base class for data ingestors."""

    @abstractmethod
    def ingest(self, content: bytes) -> Iterator[dict]:
        """Ingest content and yield FTM entities.

        Args:
            content: Raw file content as bytes.

        Yields:
            FTM entity dictionaries.

        """

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """List of supported file extensions (e.g., ['.ftm', '.ijson'])."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the ingestor."""

"""Source connector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from ..models import Company


class Source(ABC):
    """A public source of newly formed company records.

    Implementations should be polite (respect rate limits / set a User-Agent)
    and resilient: a single bad record must not abort the whole crawl.
    """

    name: str = "base"

    @abstractmethod
    def fetch(self, limit: int = 100) -> Iterator[Company]:
        """Yield up to `limit` newly discovered companies."""
        raise NotImplementedError

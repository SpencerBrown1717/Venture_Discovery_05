"""Pluggable data-source connectors.

Each connector yields `Company` records from a public source. Connectors are
registered by name so the pipeline / CLI can select sources at runtime.
"""

from __future__ import annotations

from .base import Source
from .sample import SampleSource
from .sec_edgar import SecEdgarSource

REGISTRY: dict[str, type[Source]] = {
    SampleSource.name: SampleSource,
    SecEdgarSource.name: SecEdgarSource,
}


def get_source(name: str, **kwargs) -> Source:
    if name not in REGISTRY:
        raise KeyError(
            f"Unknown source '{name}'. Available: {', '.join(sorted(REGISTRY))}"
        )
    return REGISTRY[name](**kwargs)


__all__ = ["Source", "SampleSource", "SecEdgarSource", "REGISTRY", "get_source"]

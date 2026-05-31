"""Pipeline orchestration: collect -> classify -> (research) -> store.

This is the heart of the autonomous scout. Each stage is independent and
fail-soft: a bad record or a flaky network source degrades that one item
rather than aborting the run, which is essential for an unattended agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .classify import get_classifier
from .db import Database
from .models import Company
from .sources import get_source


@dataclass
class RunReport:
    source: str
    fetched: int = 0
    classified_ai: int = 0
    researched: int = 0
    inserted: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"[{self.source}] fetched={self.fetched} ai={self.classified_ai} "
            f"researched={self.researched} inserted={self.inserted} "
            f"updated={self.updated} errors={len(self.errors)}"
        )


@dataclass
class Pipeline:
    db: Database
    use_llm: bool = False
    research: bool = False
    research_min_score: float = 0.5
    fetch_site: bool = True
    classifier_kwargs: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._classifier = get_classifier(use_llm=self.use_llm, **self.classifier_kwargs)
        self._memo_agent = None
        if self.research:
            from .research import MemoAgent

            self._memo_agent = MemoAgent(use_llm=self.use_llm, fetch_site=self.fetch_site)

    def run(self, source_name: str, limit: int = 100, **source_kwargs) -> RunReport:
        report = RunReport(source=source_name)
        source = get_source(source_name, **source_kwargs)

        batch: list[Company] = []
        for company in source.fetch(limit=limit):
            report.fetched += 1
            try:
                self._classifier.classify(company)
                if company.is_ai:
                    report.classified_ai += 1
                if (
                    self._memo_agent is not None
                    and company.ai_score >= self.research_min_score
                ):
                    self._memo_agent.research(company)
                    report.researched += 1
            except Exception as exc:  # one bad record shouldn't kill the run
                report.errors.append(f"{company.name}: {exc}")
            batch.append(company)

        inserted, updated = self.db.upsert_many(batch)
        report.inserted, report.updated = inserted, updated
        return report

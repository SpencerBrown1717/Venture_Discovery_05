"""AI-relatedness classification."""

from __future__ import annotations

from ..models import Company
from .heuristic import HeuristicClassifier


def get_classifier(use_llm: bool = False, **kwargs):
    """Return a classifier. Falls back to heuristics if the LLM is unavailable."""
    if use_llm:
        try:
            from .llm import LlmClassifier

            return LlmClassifier(**kwargs)
        except Exception as exc:  # missing key / package -> degrade gracefully
            print(f"[classify] LLM unavailable ({exc}); using heuristic classifier.")
    return HeuristicClassifier(**kwargs)


__all__ = ["HeuristicClassifier", "get_classifier", "Company"]

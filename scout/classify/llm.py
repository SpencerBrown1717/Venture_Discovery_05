"""Optional LLM classifier (stretch enhancement).

Uses an OpenAI-compatible chat model to judge AI-relatedness when richer
reasoning is desired. Requires `openai` + `OPENAI_API_KEY`. The pipeline always
falls back to the heuristic classifier if either is missing, so this never
becomes a hard dependency.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from ..models import Company
from .heuristic import HeuristicClassifier

SYSTEM_PROMPT = """You are a venture-capital analyst screening newly formed companies.
Decide how likely the company is an AI/ML company (builds, sells, or is fundamentally
powered by artificial intelligence) versus merely using buzzwords.
Return STRICT JSON: {"ai_score": <0..1 float>, "is_ai": <bool>, "category": <string>,
"reasoning": <one sentence>}. Categories: AI Infrastructure, Developer Tools, AI Agents,
Computer Vision, NLP / Language, Robotics, Healthcare AI, Fintech AI, Generative Media,
Data / Analytics, General AI, or "Not AI"."""


@dataclass
class LlmClassifier:
    model: str = "gpt-4o-mini"
    threshold: float = 0.5

    def __post_init__(self) -> None:
        from openai import OpenAI  # raises if package missing

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set")
        self._client = OpenAI()
        self._fallback = HeuristicClassifier(threshold=self.threshold)

    def classify(self, company: Company) -> Company:
        prompt = (
            f"Company name: {company.name}\n"
            f"Website: {company.website or 'n/a'}\n"
            f"Description: {company.description or 'n/a'}\n"
            f"Jurisdiction: {company.jurisdiction or 'n/a'}"
        )
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            data = json.loads(resp.choices[0].message.content)
            company.ai_score = round(float(data.get("ai_score", 0.0)), 4)
            company.is_ai = bool(data.get("is_ai", company.ai_score >= self.threshold))
            category = data.get("category", "")
            company.ai_category = "" if category == "Not AI" else category
            reasoning = data.get("reasoning", "")
            company.ai_signals = [f"llm: {reasoning}"] if reasoning else ["llm classification"]
            return company
        except Exception as exc:
            print(f"[classify:llm] {company.name}: {exc}; falling back to heuristic.")
            return self._fallback.classify(company)

"""Deterministic sample-dataset generator.

Loads a curated set of **real, public AI companies** with **verified working
websites** so the demo dashboard never links to dead domains. Non-AI noise
records intentionally omit websites (typical for very early local formations).

Run `python -m scout verify-links` after editing to re-check every URL.
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sample_companies.json"

JURISDICTIONS = [
    "Delaware, USA", "California, USA", "New York, USA", "Texas, USA",
    "Massachusetts, USA", "Washington, USA", "London, UK", "Toronto, CA",
    "Berlin, DE", "Paris, FR", "Singapore, SG", "Tel Aviv, IL",
]

# Real AI companies — every domain verified reachable (2026-05-31).
# Format: (legal-style display name, bare domain, description)
AI_SEED = [
    ("Together AI Inc.", "together.ai",
     "High-throughput open-source LLM inference and fine-tuning platform."),
    ("Modal Labs Inc.", "modal.com",
     "Serverless GPU compute platform for AI model training and inference."),
    ("Fireworks AI Inc.", "fireworks.ai",
     "Fast inference engine for open-source and custom language models."),
    ("Groq Inc.", "groq.com",
     "LPU inference hardware and cloud for low-latency LLM serving."),
    ("Cursor (Anysphere Inc.)", "cursor.com",
     "AI-native code editor with agentic pair programming."),
    ("Replit Inc.", "replit.com",
     "Cloud IDE with AI agent for building and deploying apps."),
    ("Sourcegraph Inc.", "sourcegraph.com",
     "AI coding assistant and codebase intelligence platform."),
    ("CrewAI Inc.", "crewai.com",
     "Framework for orchestrating role-playing autonomous AI agents."),
    ("LangChain Inc.", "langchain.com",
     "Developer platform for building LLM-powered applications and agents."),
    ("Sierra Technologies Inc.", "sierra.ai",
     "Conversational AI agents for enterprise customer experience."),
    ("Roboflow Inc.", "roboflow.com",
     "Computer vision platform for training and deploying models."),
    ("Landing AI Inc.", "landing.ai",
     "Visual inspection and computer vision for manufacturing."),
    ("Scale AI Inc.", "scale.com",
     "Data engine and RLHF infrastructure for AI model development."),
    ("Cohere Inc.", "cohere.com",
     "Enterprise NLP platform for search, generation, and embeddings."),
    ("Mistral AI SAS", "mistral.ai",
     "Open-weight foundation models and enterprise AI platform."),
    ("Abridge Inc.", "abridge.com",
     "AI clinical documentation from ambient conversation."),
    ("Ambience Healthcare Inc.", "ambiencehealthcare.com",
     "AI operating system for clinical documentation."),
    ("Hippocratic AI Inc.", "hippocraticai.com",
     "Safety-focused LLMs for healthcare workflows."),
    ("Ramp Business Corporation", "ramp.com",
     "Corporate card and spend platform with AI-powered finance automation."),
    ("Sardine AI Inc.", "sardine.ai",
     "AI fraud prevention and compliance for fintech."),
    ("Runway AI Inc.", "runwayml.com",
     "Generative video and creative AI tools for creators."),
    ("ElevenLabs Inc.", "elevenlabs.io",
     "AI voice synthesis and speech generation platform."),
    ("Pika Labs Inc.", "pika.art",
     "Generative video model for text-to-video creation."),
    ("Figure AI Inc.", "figure.ai",
     "Humanoid robots powered by AI for labor automation."),
    ("Covariant Inc.", "covariant.ai",
     "AI robotics for warehouse picking and manipulation."),
    ("Skild AI Inc.", "skild.ai",
     "General-purpose AI brain for diverse robot embodiments."),
    ("Hex Technologies Inc.", "hex.tech",
     "Collaborative data workspace with AI analytics copilot."),
    ("Pinecone Systems Inc.", "pinecone.io",
     "Managed vector database for production RAG applications."),
    ("Weaviate B.V.", "weaviate.io",
     "Open-source vector database and hybrid search engine."),
    ("Weights & Biases Inc.", "wandb.ai",
     "MLOps platform for experiment tracking and model monitoring."),
    ("Harvey AI Inc.", "harvey.ai",
     "AI assistant for legal research and contract workflows."),
    ("Glean Technologies Inc.", "glean.com",
     "Enterprise AI search and knowledge discovery across apps."),
    ("Perplexity AI Inc.", "perplexity.ai",
     "AI-native answer engine with real-time web retrieval."),
    ("Snorkel AI Inc.", "snorkel.ai",
     "Data-centric AI platform for programmatic labeling."),
    ("Baseten Inc.", "baseten.co",
     "Model serving infrastructure for production ML deployments."),
    ("Anyscale Inc.", "anyscale.com",
     "Ray-based platform for scaling AI and Python workloads."),
    ("Voyage AI Inc.", "voyageai.com",
     "Embedding models optimized for retrieval and search."),
]

# Non-AI noise — no website (typical for newly registered local businesses).
NOISE_SEED = [
    ("Granite Peak Construction LLC", "",
     "Commercial construction and general contracting services."),
    ("Mountain Air HVAC LLC", "",
     "Residential heating, ventilation, and air conditioning installation."),
    ("Riverside Family Dental PLLC", "",
     "General and cosmetic dentistry practice serving the metro area."),
    ("Coastal Catering Co.", "",
     "Full-service event catering and private chef services."),
    ("Sterling Property Group LLC", "",
     "Commercial real estate brokerage and property management."),
    ("Harborview Logistics Inc.", "",
     "Freight forwarding and last-mile delivery across the eastern seaboard."),
    ("Brightline Marketing LLC", "",
     "Boutique brand and performance marketing agency."),
    ("Smart Home Comfort Inc.", "",
     "Installs smart thermostats and connected home automation hardware."),
    ("Intelligent Cleaning Services LLC", "",
     "Commercial janitorial and facilities cleaning services."),
    ("Cognitive Coffee Roasters LLC", "",
     "Specialty coffee roastery and neighborhood cafe."),
    ("Apex Auto Repair Inc.", "",
     "Independent auto repair shop and tire service center."),
    ("Willow & Sage Interiors LLC", "",
     "Residential interior design and home staging studio."),
    ("Summit Fitness Collective LLC", "",
     "Boutique fitness studio offering strength and conditioning classes."),
    ("Evergreen Landscaping Inc.", "",
     "Landscape design, installation, and seasonal maintenance."),
    ("Model Citizen Apparel LLC", "",
     "Direct-to-consumer sustainable clothing brand."),
]


def _spread_dates(n: int, rng: random.Random, months_back: int = 9) -> list[str]:
    today = date.today()
    start = today - timedelta(days=months_back * 30)
    span = (today - start).days
    out = []
    for _ in range(n):
        frac = rng.random() ** 0.6
        out.append((start + timedelta(days=int(frac * span))).isoformat())
    return out


def generate(seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    records: list[dict] = []

    ai_dates = _spread_dates(len(AI_SEED), rng)
    for (name, site, desc), fdate in zip(AI_SEED, ai_dates):
        rec = {
            "name": name,
            "source_id": f"sample-{abs(hash(name)) % 10_000_000}",
            "jurisdiction": rng.choice(JURISDICTIONS),
            "formation_date": fdate,
            "description": desc,
        }
        if site:
            rec["website"] = f"https://{site}"
        records.append(rec)

    noise_dates = _spread_dates(len(NOISE_SEED), rng)
    for (name, _site, desc), fdate in zip(NOISE_SEED, noise_dates):
        records.append({
            "name": name,
            "source_id": f"sample-{abs(hash(name)) % 10_000_000}",
            "jurisdiction": rng.choice(JURISDICTIONS),
            "formation_date": fdate,
            "description": desc,
        })

    records.sort(key=lambda r: r["formation_date"], reverse=True)
    return records


def write(path: Path | str | None = None, seed: int = 7) -> Path:
    out = Path(path) if path else DATA_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(generate(seed), indent=2))
    return out


if __name__ == "__main__":
    p = write()
    print(f"Wrote sample dataset -> {p}")

"""Deterministic sample-dataset generator.

Produces a realistic mix of newly formed companies -- genuine AI startups plus
non-AI "noise" -- spread across recent months and jurisdictions. Used to power
the committed demo dashboard and to let the whole pipeline run offline.

The data is synthetic but modeled on the shape of real public registry records
(name, jurisdiction, formation date, optional website, short description).
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

# (name, website, description) -- genuine AI companies across subsectors.
AI_SEED = [
    ("Lattice Inference Labs", "latticeinfer.ai",
     "High-throughput LLM inference engine with speculative decoding for cheaper serving."),
    ("Verdant Agents", "verdantagents.com",
     "Autonomous AI agents that operate enterprise back-office workflows end to end."),
    ("Cortex Vision Systems", "cortexvision.io",
     "Computer vision platform for real-time defect detection on manufacturing lines."),
    ("Solace Health AI", "solacehealth.ai",
     "Clinical documentation copilot that drafts notes from ambient visit audio."),
    ("Ledger Sentinel", "ledgersentinel.com",
     "Machine learning fraud detection for real-time payments and card networks."),
    ("Mistwave Robotics", "mistwave.io",
     "Autonomous mobile robots for warehouse picking using reinforcement learning."),
    ("Prism Foundation Models", "prismfm.ai",
     "Builds small, efficient foundation models fine-tuned for regulated industries."),
    ("Echo Synthesis", "echosynth.ai",
     "Generative voice and avatar platform for localized marketing content."),
    ("Quill Copilot", "quillcopilot.dev",
     "AI pair programmer that reviews pull requests and writes tests automatically."),
    ("Helio Forecast", "helioforecast.com",
     "Predictive analytics for energy grids using deep learning demand models."),
    ("Nexus Vector", "nexusvector.io",
     "Managed vector database and retrieval layer for production RAG applications."),
    ("Aperture Diffusion", "aperturediffusion.ai",
     "Diffusion-model image generation API tuned for product photography."),
    ("Sentient Underwriting", "sentientuw.com",
     "AI underwriting engine for specialty insurance and credit risk."),
    ("Talos Perception", "talosperception.ai",
     "Perception stack and sensor fusion for autonomous industrial vehicles."),
    ("Beacon NLP", "beaconnlp.com",
     "Natural language processing for legal contract review and obligation extraction."),
    ("Quanta MLOps", "quantamlops.io",
     "MLOps platform for model serving, monitoring, and drift detection at scale."),
    ("Forge Agentic", "forgeagentic.ai",
     "Agentic workflow automation framework with tool use and long-horizon planning."),
    ("Meridian Drug Discovery", "meridianbio.ai",
     "Deep learning models that predict protein-ligand binding for drug discovery."),
    ("Pulse Trading Intelligence", "pulsetrading.ai",
     "Reinforcement learning trading signals for systematic crypto strategies."),
    ("Cascade Speech", "cascadespeech.com",
     "Real-time speech-to-speech translation powered by transformer models."),
    ("Atlas Data Science", "atlasds.io",
     "Predictive analytics and forecasting copilots for retail supply chains."),
    ("Glia Neural", "glianeural.ai",
     "Neural network accelerators and an inference runtime for edge devices."),
    ("Orchard Computer Vision", "orchardcv.com",
     "Computer vision for precision agriculture: crop health and yield detection."),
    ("Synthro Media", "synthro.ai",
     "Generative video synthesis platform for short-form social content."),
    ("Kindred Care Copilot", "kindredcare.ai",
     "AI patient-triage copilot for primary care clinics and telehealth."),
    ("Vantage Risk Models", "vantagerisk.ai",
     "Machine learning credit risk and fraud models for fintech lenders."),
]

# Non-AI noise (plus a few buzzword false positives to stress the classifier).
NOISE_SEED = [
    ("Granite Peak Construction", "granitepeakbuild.com",
     "Commercial construction and general contracting services."),
    ("Mountain Air HVAC", "mountainairhvac.com",
     "Residential heating, ventilation, and air conditioning installation."),
    ("Riverside Family Dental", "riversidedental.com",
     "General and cosmetic dentistry practice serving the metro area."),
    ("Coastal Catering Co", "coastalcatering.com",
     "Full-service event catering and private chef services."),
    ("Sterling Property Group", "sterlingpropertygroup.com",
     "Commercial real estate brokerage and property management."),
    ("Harborview Logistics", "harborviewlogistics.com",
     "Freight forwarding and last-mile delivery across the eastern seaboard."),
    ("Brightline Marketing", "brightlinemktg.com",
     "Boutique brand and performance marketing agency."),
    ("Smart Home Comfort", "smarthomecomfort.com",
     "Installs smart thermostats and connected home automation hardware."),
    ("Intelligent Cleaning Services", "intellicleanpro.com",
     "Commercial janitorial and facilities cleaning services."),
    ("Cognitive Coffee Roasters", "cognitivecoffee.com",
     "Specialty coffee roastery and neighborhood cafe."),
    ("Apex Auto Repair", "apexautorepair.com",
     "Independent auto repair shop and tire service center."),
    ("Willow & Sage Interiors", "willowsageinteriors.com",
     "Residential interior design and home staging studio."),
    ("Summit Fitness Collective", "summitfitness.com",
     "Boutique fitness studio offering strength and conditioning classes."),
    ("Evergreen Landscaping", "evergreenscape.com",
     "Landscape design, installation, and seasonal maintenance."),
    ("Model Citizen Apparel", "modelcitizen.com",
     "Direct-to-consumer sustainable clothing brand."),
]


def _spread_dates(n: int, rng: random.Random, months_back: int = 9) -> list[str]:
    """Generate formation dates over the last `months_back` months, weighted
    toward more recent months to mimic accelerating AI formation."""
    today = date.today()
    start = today - timedelta(days=months_back * 30)
    span = (today - start).days
    out = []
    for _ in range(n):
        # bias toward recent: square of uniform pushes mass toward 1.0
        frac = rng.random() ** 0.6
        out.append((start + timedelta(days=int(frac * span))).isoformat())
    return out


def generate(seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    records: list[dict] = []

    ai_dates = _spread_dates(len(AI_SEED), rng)
    for (name, site, desc), fdate in zip(AI_SEED, ai_dates):
        records.append({
            "name": name,
            "source_id": f"sample-{abs(hash(name)) % 10_000_000}",
            "jurisdiction": rng.choice(JURISDICTIONS),
            "formation_date": fdate,
            "website": f"https://{site}",
            "description": desc,
        })

    noise_dates = _spread_dates(len(NOISE_SEED), rng)
    for (name, site, desc), fdate in zip(NOISE_SEED, noise_dates):
        records.append({
            "name": name,
            "source_id": f"sample-{abs(hash(name)) % 10_000_000}",
            "jurisdiction": rng.choice(JURISDICTIONS),
            "formation_date": fdate,
            "website": f"https://{site}",
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

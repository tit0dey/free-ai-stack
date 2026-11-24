#!/usr/bin/env python3
"""Regenerate README tables from data/providers.json.

Updates content between:
- <!-- PICKS:START --> / <!-- PICKS:END -->
- <!-- TABLE:START --> / <!-- TABLE:END -->
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "providers.json"
PACKAGE_DATA_PATH = ROOT / "free_ai_stack" / "data" / "providers.json"
README_PATH = ROOT / "README.md"

TASK_PICKS = [
    ("Coding", ["Groq", "Mistral AI (La Plateforme)", "Cloudflare Workers AI", "OpenRouter", "Google AI Studio (Gemini API)"]),
    ("Chat", ["Google AI Studio (Gemini API)", "Groq", "OpenRouter", "Cloudflare Workers AI", "Mistral AI (La Plateforme)"]),
    ("Vision", ["Google AI Studio (Gemini API)", "Z.ai (GLM API)", "OVHcloud AI Endpoints", "Cloudflare Workers AI", "Mistral AI (La Plateforme)"]),
    ("Long context", ["Google AI Studio (Gemini API)", "OVHcloud AI Endpoints", "Z.ai (GLM API)", "OpenRouter", "Mistral AI (La Plateforme)"]),
    ("Embeddings", ["Cohere", "Cloudflare Workers AI", "Scaleway Generative APIs", "Mistral AI (La Plateforme)", "OVHcloud AI Endpoints"]),
]


def load_providers() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        providers = json.load(f)
    if not isinstance(providers, list):
        raise ValueError("providers.json must be a JSON array")
    return providers


def fmt_models(models: list[str], max_items: int = 4) -> str:
    if not models:
        return "-"
    shown = models[:max_items]
    text = ", ".join(m.replace("|", "\\|") for m in shown)
    if len(models) > max_items:
        text += f", +{len(models) - max_items} more"
    return text


def fmt_limits(limits: str, max_len: int = 140) -> str:
    text = " ".join(limits.split())
    text = text.replace("|", "\\|")
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def fmt_status(status: str) -> str:
    s = (status or "unverified").lower()
    if s == "verified":
        return "✅ Verified"
    if s == "unverified":
        return "⚠️ Unverified"
    return f"⚠️ {status}"


def pick_provider(providers: list[dict], preferred_names: list[str]) -> dict | None:
    by_name = {p.get("name"): p for p in providers}
    for name in preferred_names:
        p = by_name.get(name)
        if p and p.get("status") == "verified":
            return p
    for name in preferred_names:
        p = by_name.get(name)
        if p:
            return p
    for p in providers:
        if p.get("status") == "verified":
            return p
    return providers[0] if providers else None


def best_for(task: str, provider: dict) -> str:
    name = provider.get("name", "")
    hints = {
        "Coding": {
            "Groq": "Fast inference for code/chat models with generous daily token caps.",
            "Mistral AI (La Plateforme)": "Free mode access for prototyping coding assistants.",
            "Cloudflare Workers AI": "Easy serverless inference with a daily free neuron allocation.",
            "OpenRouter": "Try multiple free coding models behind one API.",
            "Google AI Studio (Gemini API)": "Strong free-tier models for coding and reasoning.",
        },
        "Chat": {
            "Google AI Studio (Gemini API)": "Broad free model selection for general chat and assistants.",
            "Groq": "Low-latency chat responses on free hosted models.",
            "OpenRouter": "One endpoint for rotating free chat models.",
            "Cloudflare Workers AI": "Simple chat inference with daily free allocation.",
            "Mistral AI (La Plateforme)": "Good general chat models in free mode.",
        },
        "Vision": {
            "Google AI Studio (Gemini API)": "Free multimodal models with image/audio support.",
            "Z.ai (GLM API)": "Free GLM vision flash model available.",
            "OVHcloud AI Endpoints": "Anonymous access to vision-capable open models.",
            "Cloudflare Workers AI": "Vision-capable models in the Workers AI catalog.",
            "Mistral AI (La Plateforme)": "Multimodal models available in free mode (limits vary).",
        },
        "Long context": {
            "Google AI Studio (Gemini API)": "Large-context Gemini models available on free tier.",
            "OVHcloud AI Endpoints": "Large-context open models with anonymous access.",
            "Z.ai (GLM API)": "Free GLM flash models for long-context experimentation.",
            "OpenRouter": "Route to free models with large context windows.",
            "Mistral AI (La Plateforme)": "Large-context models available; check console limits.",
        },
        "Embeddings": {
            "Cohere": "Trial key includes embed and rerank endpoints.",
            "Cloudflare Workers AI": "Embedding models available in Workers AI catalog.",
            "Scaleway Generative APIs": "Free token allocation can cover embedding tests.",
            "Mistral AI (La Plateforme)": "Embedding endpoints available; limits shown in console.",
            "OVHcloud AI Endpoints": "Open embedding-capable endpoints in EU-hosted catalog.",
        },
    }
    return hints.get(task, {}).get(name, "Check limits and model fit before production use.")


def render_picks(providers: list[dict]) -> str:
    lines = [
        "| Task | Best free pick | Why | Card | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for task, preferred in TASK_PICKS:
        p = pick_provider(providers, preferred)
        if not p:
            continue
        name = p.get("name", "-")
        card = "Yes" if p.get("card_required") else "No"
        status = fmt_status(p.get("status", "unverified"))
        why = best_for(task, p).replace("|", "\\|")
        lines.append(f"| {task} | [{name}]({p.get('source_url','')}) | {why} | {card} | {status} |")
    return "\n".join(lines)


def render_table(providers: list[dict]) -> str:
    lines = [
        "| Provider | Free models | Limits (official summary) | Card | Region notes | Source | Last verified | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for p in providers:
        name = p.get("name", "-").replace("|", "\\|")
        models = fmt_models(p.get("free_models", []))
        limits = fmt_limits(p.get("limits", "-"))
        card = "Yes" if p.get("card_required") else "No"
        region = " ".join(str(p.get("region_notes", "-")).split()).replace("|", "\\|")
        region = region if len(region) <= 90 else region[:89].rstrip() + "…"
        source = p.get("source_url", "")
        source_cell = f"[Source]({source})" if source else "-"
        last_verified = p.get("last_verified", "-")
        status = fmt_status(p.get("status", "unverified"))
        lines.append(
            f"| {name} | {models} | {limits} | {card} | {region} | {source_cell} | {last_verified} | {status} |"
        )
    return "\n".join(lines)


def render_counts(providers: list[dict]) -> str:
    total = len(providers)
    verified = sum(1 for p in providers if str(p.get("status", "")).lower() == "verified")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"_Provider coverage: {total} providers tracked, {verified} verified from official sources (as of {today})._"


def replace_block(text: str, start: str, end: str, content: str) -> str:
    pattern = re.compile(
        rf"({re.escape(start)})(.*?){re.escape(end)}",
        re.DOTALL,
    )
    repl = f"{start}\n{content}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"Markers not found: {start} ... {end}")
    return pattern.sub(repl, text, count=1)


def sync_package_data() -> None:
    PACKAGE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE_DATA_PATH.write_text(DATA_PATH.read_text(encoding="utf-8"), encoding="utf-8")


def update_readme() -> None:
    providers = load_providers()
    sync_package_data()
    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_block(readme, "<!-- COUNTS:START -->", "<!-- COUNTS:END -->", render_counts(providers))
    readme = replace_block(readme, "<!-- PICKS:START -->", "<!-- PICKS:END -->", render_picks(providers))
    readme = replace_block(readme, "<!-- TABLE:START -->", "<!-- TABLE:END -->", render_table(providers))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    readme = re.sub(r"last-verified-\d{4}--\d{2}--\d{2}", f"last-verified-{today.replace('-', '--')}", readme)
    README_PATH.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    update_readme()
    print(f"Updated {README_PATH}")

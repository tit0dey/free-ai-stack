#!/usr/bin/env python3
"""CLI for free-ai-stack."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TASKS = ["coding", "chat", "vision", "long-context", "embeddings"]

TASK_PREFERENCES = {
    "coding": [
        "Groq",
        "Mistral AI (La Plateforme)",
        "Cloudflare Workers AI",
        "OpenRouter",
        "Google AI Studio (Gemini API)",
    ],
    "chat": [
        "Google AI Studio (Gemini API)",
        "Groq",
        "OpenRouter",
        "Cloudflare Workers AI",
        "Mistral AI (La Plateforme)",
    ],
    "vision": [
        "Google AI Studio (Gemini API)",
        "Z.ai (GLM API)",
        "OVHcloud AI Endpoints",
        "Cloudflare Workers AI",
        "Mistral AI (La Plateforme)",
    ],
    "long-context": [
        "Google AI Studio (Gemini API)",
        "OVHcloud AI Endpoints",
        "Z.ai (GLM API)",
        "OpenRouter",
        "Mistral AI (La Plateforme)",
    ],
    "embeddings": [
        "Cohere",
        "Cloudflare Workers AI",
        "Scaleway Generative APIs",
        "Mistral AI (La Plateforme)",
        "OVHcloud AI Endpoints",
    ],
}

TASK_REASONS = {
    "coding": "Fast, practical free inference for code generation and iteration.",
    "chat": "Good general-purpose chat quality with a usable free tier.",
    "vision": "Supports image/multimodal inputs on a free or anonymous tier.",
    "long-context": "Handles larger prompts/documents; verify current context limits.",
    "embeddings": "Offers embedding/vector endpoints or free allocation for embedding tests.",
}


def find_data_file() -> Path:
    candidates = []
    here = Path(__file__).resolve()
    # Packaged data
    candidates.append(here.parent / "data" / "providers.json")
    # Repo root when running from source
    candidates.append(here.parents[1] / "data" / "providers.json")
    candidates.append(here.parents[2] / "data" / "providers.json")
    candidates.append(Path.cwd() / "data" / "providers.json")
    candidates.append(Path.cwd() / "providers.json")
    candidates.append(Path(sys.prefix) / "share" / "free-ai-stack" / "providers.json")
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "Could not find data/providers.json. Run from the repo root or install the package with data."
    )


def load_providers() -> list[dict[str, Any]]:
    path = find_data_file()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("providers.json must contain a JSON array")
    return data


def normalize(s: str) -> str:
    return "".join(ch.lower() for ch in s if ch.isalnum())


def pick_for_task(providers: list[dict[str, Any]], task: str) -> dict[str, Any] | None:
    prefs = TASK_PREFERENCES.get(task, [])
    by_name = {p.get("name", ""): p for p in providers}
    for name in prefs:
        p = by_name.get(name)
        if p and p.get("status") == "verified":
            return p
    for name in prefs:
        p = by_name.get(name)
        if p:
            return p
    for p in providers:
        if p.get("status") == "verified":
            return p
    return providers[0] if providers else None


def cmd_list(providers: list[dict[str, Any]], as_json: bool) -> int:
    if as_json:
        json.dump(providers, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    for p in providers:
        name = p.get("name", "<unknown>")
        status = p.get("status", "unverified")
        card = "card required" if p.get("card_required") else "no card"
        models = p.get("free_models", [])
        model_count = len(models) if isinstance(models, list) else 0
        print(f"- {name} [{status}, {card}, {model_count} free model entries]")
    return 0


def cmd_pick(providers: list[dict[str, Any]], task: str, as_json: bool) -> int:
    p = pick_for_task(providers, task)
    if not p:
        print("No providers found.", file=sys.stderr)
        return 1
    result = {
        "task": task,
        "provider": p.get("name"),
        "reason": TASK_REASONS.get(task, "Good free option for this task."),
        "free_models": p.get("free_models", []),
        "limits": p.get("limits"),
        "card_required": p.get("card_required"),
        "source_url": p.get("source_url"),
        "last_verified": p.get("last_verified"),
        "status": p.get("status"),
    }
    if as_json:
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    print(f"Task: {task}")
    print(f"Pick: {result['provider']}")
    print(f"Why:  {result['reason']}")
    print(f"Card: {'required' if result['card_required'] else 'not required'}")
    print(f"Status: {result['status']}")
    print(f"Last verified: {result['last_verified']}")
    print(f"Source: {result['source_url']}")
    print("Free models:")
    for m in result.get("free_models", [])[:5]:
        print(f"  - {m}")
    if len(result.get("free_models", [])) > 5:
        print(f"  - +{len(result['free_models']) - 5} more")
    print("Limits:")
    print(f"  {result['limits']}")
    return 0


def cmd_show(providers: list[dict[str, Any]], name: str, as_json: bool) -> int:
    needle = normalize(name)
    match = None
    for p in providers:
        if normalize(p.get("name", "")) == needle:
            match = p
            break
    if match is None:
        for p in providers:
            n = normalize(p.get("name", ""))
            if needle in n or n in needle:
                match = p
                break
    if match is None:
        print(f"Provider not found: {name}", file=sys.stderr)
        return 1
    if as_json:
        json.dump(match, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    print(f"Name: {match.get('name')}")
    print(f"Status: {match.get('status')}")
    print(f"Card required: {'yes' if match.get('card_required') else 'no'}")
    print(f"Last verified: {match.get('last_verified')}")
    print(f"Source: {match.get('source_url')}")
    print(f"Region notes: {match.get('region_notes')}")
    print("Free models:")
    for m in match.get("free_models", []):
        print(f"  - {m}")
    print("Limits:")
    print(f"  {match.get('limits')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fas", description="Find genuinely free AI models and APIs.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all providers")
    p_list.add_argument("--json", action="store_true", help="Output JSON")

    p_pick = sub.add_parser("pick", help="Pick best free provider for a task")
    p_pick.add_argument("--task", required=True, choices=TASKS, help="Task type")
    p_pick.add_argument("--json", action="store_true", help="Output JSON")

    p_show = sub.add_parser("show", help="Show details for a provider")
    p_show.add_argument("provider", help="Provider name (exact or partial)")
    p_show.add_argument("--json", action="store_true", help="Output JSON")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        providers = load_providers()
    except Exception as e:  # noqa: BLE001
        print(f"Error loading providers: {e}", file=sys.stderr)
        return 1

    if args.command == "list":
        return cmd_list(providers, args.json)
    if args.command == "pick":
        return cmd_pick(providers, args.task, args.json)
    if args.command == "show":
        return cmd_show(providers, args.provider, args.json)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

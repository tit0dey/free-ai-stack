---
name: free-ai-stack
description: Find genuinely free AI models and APIs from a verified, auto-updated directory. Use when a user asks which free LLM/API/model to use for coding, chat, vision, long context, embeddings, or when they need free-tier limits, signup/card requirements, or official source links.
---

# free-ai-stack

Use this skill to answer "which free AI model/API should I use for X?" with verified data.

## Data source

- Canonical data: `data/providers.json`
- Human-readable table: `README.md`
- CLI: `fas` (`free_ai_stack/cli.py`)

## When to use

- User asks for free LLM/API recommendations.
- User asks about free-tier limits, credit card requirements, or region notes.
- User wants a model for coding, chat, vision, long context, or embeddings.
- User wants an agent/coding tool to pick a free provider.

## How to use

1. **Prefer the CLI** when available:
   ```bash
   fas pick --task coding
   fas pick --task vision --json
   fas show groq
   fas list --json
   ```
2. **If CLI is unavailable**, read `data/providers.json` directly.
3. **Check verification fields** before recommending:
   - `status`: prefer `verified`; disclose `unverified`.
   - `last_verified`: warn if stale.
   - `source_url`: cite the official source.
   - `limits`: report as officially stated; do not invent missing numbers.
   - `card_required`: state clearly.
4. **For task picks**, prioritize verified providers with clear limits and a good fit:
   - Coding: Groq, Mistral, Cloudflare Workers AI, OpenRouter, Gemini
   - Chat: Gemini, Groq, OpenRouter, Cloudflare Workers AI, Mistral
   - Vision: Gemini, Z.ai, OVHcloud, Cloudflare Workers AI, Mistral
   - Long context: Gemini, OVHcloud, Z.ai, OpenRouter, Mistral
   - Embeddings: Cohere, Cloudflare Workers AI, Scaleway, Mistral, OVHcloud

## Response rules

- Cite the provider's `source_url`.
- Include `last_verified` and `status`.
- Say "unverified" when limits cannot be confirmed.
- Never invent prices, quotas, or model availability.
- If the user needs production reliability, recommend checking the official limits page before deployment.

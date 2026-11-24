# free-ai-stack

Verified directory of free AI inference providers, with official-source limits and last-verified dates.

<!-- COUNTS:START -->
_Provider coverage: 13 providers tracked, 13 verified from official sources (as of 2026-11-24)._
<!-- COUNTS:END -->

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Last verified](https://img.shields.io/badge/last--verified-2026--11--24-blue.svg)](data/providers.json)
[![Update workflow](https://github.com/tit0dey/free-ai-stack/actions/workflows/update.yml/badge.svg)](https://github.com/tit0dey/free-ai-stack/actions/workflows/update.yml)

## Best free pick right now

<!-- PICKS:START -->
| Task | Best free pick | Why | Card | Status |
| --- | --- | --- | --- | --- |
| Coding | [Groq](https://console.groq.com/docs/rate-limits) | Fast inference for code/chat models with generous daily token caps. | No | ✅ Verified |
| Chat | [Google AI Studio (Gemini API)](https://ai.google.dev/gemini-api/docs/rate-limits) | Broad free model selection for general chat and assistants. | No | ✅ Verified |
| Vision | [Google AI Studio (Gemini API)](https://ai.google.dev/gemini-api/docs/rate-limits) | Free multimodal models with image/audio support. | No | ✅ Verified |
| Long context | [Google AI Studio (Gemini API)](https://ai.google.dev/gemini-api/docs/rate-limits) | Large-context Gemini models available on free tier. | No | ✅ Verified |
| Embeddings | [Cohere](https://docs.cohere.com/docs/rate-limits) | Trial key includes embed and rerank endpoints. | No | ✅ Verified |
<!-- PICKS:END -->

## Real CLI output

```text
$ fas pick --task coding
Task: coding
Pick: Groq
Why:  Fast, practical free inference for code generation and iteration.
Card: not required
Status: verified
Last verified: 2026-11-24
Source: https://console.groq.com/docs/rate-limits
Free models:
  - openai/gpt-oss-120b
  - openai/gpt-oss-20b
  - qwen/qwen3.8-27b
  - meta-llama/llama-prompt-guard-2-22m
  - meta-llama/llama-prompt-guard-2-86m
  - +4 more
Limits:
  Organization-level rate limits. As listed on Groq docs (2026-11-24): gpt-oss-120b 30 RPM, 1K RPD, 8K TPM, 200K TPD; gpt-oss-20b 30 RPM, 1K RPD, 8K TPM, 200K TPD; qwen/qwen3.8-27b 30 RPM, 1K RPD, 8K TPM, 200K TPD; whisper-large-v3 20 RPM, 2K RPD, 7.2K ASH, 28.8K ASD; whisper-large-v3-turbo 20 RPM, 2K RPD, 7.2K ASH, 28.8K ASD. Check console Limits page for current account limits.
```

## Quick start

```bash
git clone https://github.com/tit0dey/free-ai-stack.git
cd free-ai-stack && pip install -e .
fas pick --task coding
```

## Use it inside your AI agent

Install the skill by copying `skills/free-ai-stack/SKILL.md` into your agent skills folder.
Agents can then read `data/providers.json` or run `fas pick --task <task> --json`.

## Full provider table

<!-- TABLE:START -->
| Provider | Free models | Limits (official summary) | Card | Region notes | Source | Last verified | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Google AI Studio (Gemini API) | Gemini 3.8 Flash (preview) — free-tier RPM/TPM/RPD: see AI Studio (per-model, per-project; not published as fixed numbers on rate-limits page), Gemini 3.6 Flash (preview) — free-tier RPM/TPM/RPD: see AI Studio, Gemini 3.5 Flash-Lite (preview) — free-tier RPM/TPM/RPD: see AI Studio, Gemini 3.1 Flash-Lite (preview) — free-tier RPM/TPM/RPD: see AI Studio, +6 more | Free tier is available in eligible countries/projects; per-project interactive rate limits (RPM/TPM/RPD) differ by model and project and ar… | No | Available in supported countries/territories; free-tier content may be used to improve Go… | [Source](https://ai.google.dev/gemini-api/docs/rate-limits) | 2026-11-24 | ✅ Verified |
| Groq | openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b, meta-llama/llama-prompt-guard-2-22m, +5 more | Organization-level rate limits. As listed on Groq docs (2026-11-24): gpt-oss-120b 30 RPM, 1K RPD, 8K TPM, 200K TPD; gpt-oss-20b 30 RPM, 1K… | No | Service availability subject to Groq supported regions and terms. | [Source](https://console.groq.com/docs/rate-limits) | 2026-11-24 | ✅ Verified |
| OpenRouter | Models with `:free` suffix (rotating catalog; see OpenRouter models list) | Free-model variants (`:free`): 20 requests/minute. 50 requests/day if account has purchased less than 10 credits total; 1000 requests/day a… | No | Global routing service; model/provider availability varies. | [Source](https://openrouter.ai/docs/api-reference/limits) | 2026-11-24 | ✅ Verified |
| Cloudflare Workers AI | Llama 3.3 70B Instruct FP8 Fast, Llama 3.1 8B Instruct (FP8/Fast variants), Llama 3.2 1B/3B/11B Vision Instruct, Gemma 3 12B IT, +8 more | 10,000 Neurons per day at no charge on Workers Free and Paid plans. Limits reset daily at 00:00 UTC. Usage above free allocation requires W… | No | Served via Cloudflare global network; account/feature availability subject to Cloudflare… | [Source](https://developers.cloudflare.com/workers-ai/platform/pricing/) | 2026-11-24 | ✅ Verified |
| Mistral AI (La Plateforme) | Models available in Mistral Free/Experiment mode (availability shown in console; varies over time) | Free mode provides API access with no credit card required for experimentation and prototyping. Rate limits apply; exact limits are shown i… | No | Service availability and data-use policy depend on plan/terms; review Mistral terms befor… | [Source](https://docs.mistral.ai/deployment/laplateforme/tier/) | 2026-11-24 | ✅ Verified |
| Cohere | Command A / Command A Reasoning / Command A Vision (trial), Command R+ / Command R / Command R7B, Embed, Rerank, Tokenize, and other endpoints on trial key | Trial keys are free but limited: 1,000 API calls/month total. Chat: 20 req/min on trial. Embed: 2,000 inputs/min; Embed (Images): 5 inputs/… | No | Global service; trial usage subject to Cohere terms. | [Source](https://docs.cohere.com/docs/rate-limits) | 2026-11-24 | ✅ Verified |
| Z.ai (GLM API) | GLM-4.7-Flash, GLM-4.5-Flash, GLM-4.6V-Flash | Listed at $0 for input, cached input, and output on Z.ai's official pricing. Z.ai does not publish fixed public numeric rate limits for fre… | No | Service availability and data policy vary by region; review Z.ai terms. | [Source](https://docs.z.ai/guides/overview/pricing) | 2026-11-24 | ✅ Verified |
| OVHcloud AI Endpoints | Qwen3.5 397B A17B, Llama 3.3 70B Instruct, GPT-OSS 120B / 20B, Qwen3.6 27B, +5 more | Anonymous access: 2 requests/minute per IP per model, no signup/API key required. Authenticated access with Public Cloud API key: 400 reque… | No | EU-hosted (OVHcloud). Anonymous tier has no signup; authenticated higher limits require P… | [Source](https://endpoints.ai.cloud.ovh.net/) | 2026-11-24 | ✅ Verified |
| Scaleway Generative APIs | Models in Scaleway Generative APIs catalog (examples: Llama 3.3 70B Instruct, GPT-OSS 120B, Qwen3 Coder 30B A3B Instruct; catalog varies) | Free Tier: 1,000,000 tokens for models billed by tokens and 60 minutes of audio transcription for models billed by audio minutes. After fre… | Yes | EU-hosted (Paris, France). Valid payment method/identity verification may be required for… | [Source](https://www.scaleway.com/en/docs/generative-apis/faq/) | 2026-11-24 | ✅ Verified |
| Cerebras Inference | gpt-oss-120b, qwen-3.8-27b | Free Trial provides $5 in credits (expires 30 days after grant) after adding a verified payment method; no permanent no-card free tier. Tri… | Yes | Payment method required to activate trial; service subject to Cerebras terms. | [Source](https://inference-docs.cerebras.ai/support/rate-limits) | 2026-11-24 | ✅ Verified |
| Vercel AI Gateway | Free-tier subset of models routed through Vercel AI Gateway (model availability varies; see dashboard/docs) | $5/month in included AI Gateway credits on eligible Hobby accounts and teams. Free-tier subset of models only; lower per-model rate limits… | No | Global edge platform; model/provider availability and data handling vary by upstream prov… | [Source](https://vercel.com/docs/ai-gateway/pricing) | 2026-11-24 | ✅ Verified |
| Kilo Gateway | Models tagged `:free` in Kilo Gateway catalog (includes `kilo-auto/free`; live catalog varies) | Free models are available at no cost and subject to rate limits. All free-model requests (anonymous and authenticated) are rate-limited to… | No | Global service; anonymous access allowed; free requests rate-limited by IP. | [Source](https://kilo.ai/docs/gateway/usage-and-billing) | 2026-11-24 | ✅ Verified |
| Alibaba Cloud Model Studio | Select Qwen and other models marked with free quota in Model Studio (Singapore/International scope; varies by model/release) | New-user free quota for eligible models in Singapore region with International scope. Quota is typically 1,000,000 tokens per model, valid… | No | Singapore region, International scope only for the documented new-user free quota; accoun… | [Source](https://www.alibabacloud.com/help/en/model-studio/new-free-quota) | 2026-11-24 | ✅ Verified |
<!-- TABLE:END -->

## How it stays fresh

- `data/providers.json` is the single source of truth. `scripts/build_readme.py` regenerates README tables from it and syncs the packaged copy at `free_ai_stack/data/providers.json`; the daily workflow does **not** auto-edit provider data.
- The daily GitHub Action runs `scripts/check_links.py --json` to check every `source_url` and flag stale entries (>30 days) and real broken links (404, 410, 5xx, or timeouts/network errors on a working network). HTTP 403/429 responses are treated as bot-protection warnings, not broken links. The link-check report is uploaded as a workflow artifact (not committed).
- If the check finds broken or stale entries, the workflow creates or updates one open GitHub issue titled "Stale or broken provider entries"; when there are no broken or stale entries, it closes that issue automatically.
- The workflow opens a pull request only when `data/providers.json`, `free_ai_stack/data/providers.json`, or README table/content actually changed (no timestamp-only churn). Every entry keeps an official source URL and `last_verified` date; providers without confirmable official free-tier/limit details are marked unverified or removed.

## Contribute in 30 seconds

Found an outdated limit? [Open an outdated-limit issue](../../issues/new?template=outdated-limit.yml).

Want to add a provider? See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)

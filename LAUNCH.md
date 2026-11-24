# Launch Pack: free-ai-stack

## GitHub About

**Description (160 chars max):**
> Verified, auto-updated directory of genuinely free AI models and APIs, with a CLI and agent skill.

(99 characters)

**Topics (12):**
`ai`, `llm`, `free`, `api`, `developer-tools`, `cli`, `agents`, `open-source`, `machine-learning`, `generative-ai`, `llmops`, `awesome-list`

## Show HN

### Title options (max 80 chars)

1. Show HN: Free AI Stack – verified directory of free LLM APIs, updated daily
2. Show HN: I built a daily-verified directory of genuinely free AI model APIs
3. Show HN: Free AI Stack – find which LLM APIs are actually free right now
4. Show HN: A no-hype, auto-updated list of free AI APIs with a tiny CLI
5. Show HN: Free AI Stack – verified free LLM APIs + CLI for coding agents

### First comment (copy-paste)

Hi HN — I built **free-ai-stack**, a directory of AI model APIs that are genuinely free to use right now.

The problem: “free tier” info goes stale fast. Limits change, cards become required, and old blog posts keep ranking. I wanted one repo where every entry has an official source URL, a `last_verified` date, and a status field.

What’s in the repo:
- `data/providers.json` with 15+ providers, official limits, card requirements, and source links.
- A daily GitHub Action that checks links/staleness and opens a PR when data changes.
- A tiny stdlib-only Python CLI (`fas pick --task coding`) for humans and coding agents.
- An agent skill so tools like Claude Code/Cursor can pick a free model with source-backed data.

Accuracy over volume: if I can’t verify a limit, it’s marked `unverified` instead of guessed.

I’d love feedback on: which providers I missed, better verification signals, and whether the data schema is useful for agent workflows.

Repo: https://github.com/tit0dey/free-ai-stack

## Reddit posts

### r/LocalLLaMA

**Title:** Built a verified, auto-updated directory of free hosted LLM APIs (with sources and CLI)

**Body:**
I know this community leans local-first (same here), but I kept getting asked "what's a free hosted API for quick testing before I run it locally?" 

I made `free-ai-stack`: a GitHub repo that tracks genuinely free AI model APIs. Every provider entry includes official source URL, limits as stated by docs, card requirement, region notes, and last verified date. A daily Action checks links and opens a PR when something changes.

It also has a small stdlib-only CLI (`fas pick --task coding`) and an agent skill. No affiliate links, no fake star tactics, MIT licensed.

If you see a stale limit or a missing provider, I’d appreciate an issue/PR. Repo: https://github.com/tit0dey/free-ai-stack

### r/ChatGPTCoding

**Title:** I made a daily-verified list of free AI APIs for coding agents (with CLI)

**Body:**
I built `free-ai-stack` because I was tired of outdated "free LLM API" lists. It’s a verified directory of free model APIs with official source links, last-verified dates, and card/limit notes.

Useful bits for coding workflows:
- `fas pick --task coding --json` gives a source-backed pick.
- `data/providers.json` is easy for scripts/agents to consume.
- Daily GitHub Action checks links and flags stale entries.

It’s MIT, Python stdlib-only, and accuracy-first (unverified when not confirmed). Feedback welcome: https://github.com/tit0dey/free-ai-stack

### r/opensource

**Title:** free-ai-stack: an MIT, auto-updated directory of genuinely free AI APIs

**Body:**
Sharing an open-source project I’ve been building: `free-ai-stack`.

It’s a verified directory of AI models/APIs that are genuinely free to use right now. The focus is maintainability and trust:
- Data in `data/providers.json` with official source URLs and verification dates.
- Scripts to regenerate README tables and check links/staleness.
- Daily GitHub Action that opens a PR when data changes.
- Python 3.9+ stdlib-only CLI, no dependencies.

I’d value maintainer feedback on the data schema, automation, and contribution flow. Repo: https://github.com/tit0dey/free-ai-stack

### r/programming

**Title:** Open-source, auto-updated directory of free AI APIs with verifiable source data

**Body:**
I built `free-ai-stack`, a small open-source repo that tracks free AI model/API tiers with verifiable metadata.

Design choices:
- JSON as the source of truth (`data/providers.json`).
- Every entry has `source_url`, `last_verified`, `status`, and limits as officially stated.
- GitHub Action runs daily link/staleness checks and opens PRs on changes.
- Python stdlib-only CLI (`fas`) outputs human or JSON for agent workflows.

Not trying to be a huge marketing list; accuracy over volume. If a limit can’t be verified, it’s marked `unverified`.

Repo: https://github.com/tit0dey/free-ai-stack

## X/Twitter thread (6 tweets)

1/6 I built free-ai-stack: a verified, auto-updated directory of genuinely free AI model APIs. No hype, just official sources and dates. https://github.com/tit0dey/free-ai-stack

2/6 Every provider entry includes: free models, limits as officially stated, card required, region notes, source URL, and last_verified date.

3/6 If a limit can’t be verified, it’s marked `unverified`. Accuracy over volume.

4/6 It ships with a tiny stdlib-only CLI: `fas pick --task coding --json` for humans, scripts, and coding agents.

5/6 A daily GitHub Action checks links, flags stale entries, regenerates the README table, and opens a PR when data changes.

6/6 MIT licensed. If you spot an outdated limit, open an issue with the official source: https://github.com/tit0dey/free-ai-stack/issues/new?template=outdated-limit.yml

## Chinese-language post (V2EX/Juejin)

**标题：** 做了一个每日自动核验的免费 AI API / 模型目录（含 CLI 和 Agent Skill）

**正文：**
大家好，我做了一个开源项目 **free-ai-stack**，目标是整理“现在真的能免费用”的 AI 模型/API。

很多免费额度信息很快就过期了，所以这个仓库强调可验证性：每个 provider 都有官方来源链接、`last_verified` 日期、是否需要信用卡、额度限制（按官方文档表述），无法确认的就标记为 `unverified`，不瞎猜。

仓库还包含：
- `data/providers.json` 数据源
- 每日自动检查链接/过期条目的 GitHub Action
- Python 标准库 CLI：`fas pick --task coding --json`
- 给 Claude Code/Cursor 等 Agent 用的 skill

MIT 协议，欢迎提 Issue/PR 修正额度信息：  
https://github.com/tit0dey/free-ai-stack

## Real "awesome" lists worth a PR

Only submit where the list is active and accepts PRs; follow each repo’s contribution rules and avoid self-promo spam.

| List | Why it fits | Check before PR |
| --- | --- | --- |
| [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | Meta-awesome; only if you first get listed in a relevant topic awesome list and meet quality bar | Very strict; usually not a direct first PR target |
| [eudk/awesome-ai-tools](https://github.com/eudk/awesome-ai-tools) | Active AI tools directory | Confirm it accepts repo/tool submissions and match category |
| [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) | Large AI audience, but not a perfect fit | Likely not relevant; avoid irrelevant PRs |
| [steven2358/awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai) | Generative AI resources/tools | Verify active maintenance and contribution format |
| [Hannibal046/Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM) | LLM-focused resource list | Check if tools/directories are accepted; follow PR template |
| [tensorchord/Awesome-LLMOps](https://github.com/tensorchord/Awesome-LLMOps) | LLM tooling/ops audience | Confirm directory/tools section accepts external repos |

**Recommended approach:** start with 1-2 highly relevant, active lists where your repo clearly fits, and tailor the PR description to that list’s audience.

## Best posting days/times (UTC)

General developer-community windows (adjust for your audience and verify with your own analytics):

| Channel | Good days (UTC) | Good times (UTC) | Notes |
| --- | --- | --- | --- |
| Show HN | Tue–Thu | 14:00–16:00 | Avoid major US holidays; be active in comments first hour. |
| r/LocalLLaMA | Mon–Thu | 13:00–17:00 | Technical, practical tone works best. |
| r/ChatGPTCoding | Mon–Thu | 14:00–18:00 | Focus on workflow/agent utility. |
| r/opensource | Tue–Thu | 14:00–17:00 | Emphasize maintenance, license, contribution flow. |
| r/programming | Tue–Thu | 14:00–16:00 | Keep it technical; avoid promotional language. |
| X/Twitter | Tue–Thu | 14:00–18:00 | Thread format; post when US/EU overlap. |
| V2EX/Juejin | Mon–Fri | 01:00–04:00 UTC (09:00–12:00 CST) | Local morning/weekday posting usually performs better. |

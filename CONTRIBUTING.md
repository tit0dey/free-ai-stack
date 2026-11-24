# Contributing to free-ai-stack

Thanks for helping keep free AI provider data accurate.

## Quick ways to contribute

- **Report an outdated limit**: [Open an outdated-limit issue](../../issues/new?template=outdated-limit.yml).
- **Add a provider**: [Open an add-provider issue](../../issues/new?template=add-provider.yml) or submit a PR.
- **Fix docs/scripts**: Open a PR with a clear description.

## Add or update a provider

1. Edit `data/providers.json`.
2. Include required fields:
   - `name`
   - `free_models`
   - `limits` (as officially stated)
   - `card_required`
   - `region_notes`
   - `source_url` (official docs/pricing page)
   - `last_verified` (`YYYY-MM-DD`)
   - `status` (`verified` or `unverified`)
3. Do **not** invent limits. If you cannot verify, set `status` to `unverified` and explain in the PR.
4. Regenerate README tables:
   ```bash
   python scripts/build_readme.py
   ```
5. Optionally run link checks:
   ```bash
   python scripts/check_links.py
   ```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
fas list
python scripts/build_readme.py
python scripts/check_links.py
```

## Rules

- Accuracy over volume.
- Official sources only for limits/pricing claims.
- No API keys, secrets, or proprietary data.
- No fake stars, bots, or misleading claims.
- Keep changes small and reviewable.

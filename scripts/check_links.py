#!/usr/bin/env python3
"""Check provider source URLs and staleness.

- Checks every source_url returns HTTP 200.
- Flags entries not verified in 30+ days.
- Writes a Markdown report to reports/link_check.md (unless --json).
- If every URL fails due to network/TLS unavailability, treats it as network
  unavailable, prints a warning, does not write a broken-links report, and exits 0.
- HTTP 403/429 are treated as blocked by bot protection (warning, not broken).
- Only 404, 410, 5xx, and timeouts/network errors on a working network count as broken.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "providers.json"
REPORT_PATH = ROOT / "reports" / "link_check.md"
USER_AGENT = "free-ai-stack-link-check/1.0 (+https://github.com/tit0dey/free-ai-stack)"


def load_providers() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("providers.json must be a JSON array")
    return data


def check_url(url: str, timeout: int = 20) -> tuple[bool, str, str]:
    """Return (ok, detail, category).

    Categories:
      ok           - HTTP 200
      blocked      - HTTP 403/429 (bot protection / rate limit), warning not broken
      broken_http  - HTTP 404/410/5xx
      warning_http - other HTTP errors, warning not broken
      network      - URL/timeout/TLS/connection errors
    """
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
            if code == 200:
                return True, f"HTTP {code}", "ok"
            if code in (403, 429):
                return False, f"HTTP {code} (blocked by bot protection)", "blocked"
            if code in (404, 410) or 500 <= code < 600:
                return False, f"HTTP {code}", "broken_http"
            return False, f"HTTP {code}", "warning_http"
    except HTTPError as e:
        code = e.code
        if code in (403, 429):
            return False, f"HTTP {code} (blocked by bot protection)", "blocked"
        if code in (404, 410) or 500 <= code < 600:
            return False, f"HTTP {code}", "broken_http"
        return False, f"HTTP {code}", "warning_http"
    except (URLError, TimeoutError) as e:
        return False, f"Network/timeout error: {e}", "network"
    except Exception as e:  # noqa: BLE001
        return False, f"Network/error: {e}", "network"


def days_since(date_str: str) -> int | None:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:  # noqa: BLE001
        return None
    now = datetime.now(timezone.utc)
    return (now - dt).days


def write_report(rows: list[dict], broken: list[dict], stale: list[dict], warnings: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Link Check Report",
        "",
        f"- Providers checked: {len(rows)}",
        f"- Broken source URLs: {len(broken)}",
        f"- Warnings (blocked/non-broken): {len(warnings)}",
        f"- Stale entries (>30 days or invalid date): {len(stale)}",
        "",
        "## Results",
        "",
        "| Provider | Source URL | Link | Last verified | Age (days) | Stale |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        age = "" if r["age_days"] is None else str(r["age_days"])
        stale_mark = "Yes" if r["stale"] else "No"
        if r["link_ok"]:
            link_mark = "OK"
        elif r["category"] in ("blocked", "warning_http"):
            link_mark = f"WARN ({r['detail']})"
        else:
            link_mark = f"FAIL ({r['detail']})"
        url = r["url"] or "-"
        safe_name = r["name"].replace("|", "\\|")
        safe_link_mark = link_mark.replace("|", "\\|")
        lines.append(
            f"| {safe_name} | {url} | {safe_link_mark} | {r['last_verified']} | {age} | {stale_mark} |"
        )

    if broken:
        lines += ["", "## Broken Links", ""]
        for r in broken:
            lines.append(f"- **{r['name']}**: {r['url']} — {r['detail']}")

    if warnings:
        lines += ["", "## Warnings (not counted as broken)", ""]
        for r in warnings:
            lines.append(f"- **{r['name']}**: {r['url']} — {r['detail']}")

    if stale:
        lines += ["", "## Stale Entries", ""]
        for r in stale:
            age_text = "unknown" if r["age_days"] is None else f"{r['age_days']} days"
            lines.append(f"- **{r['name']}**: last_verified={r['last_verified'] or 'missing'} ({age_text})")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_broken(row: dict, network_working: bool) -> bool:
    if row["link_ok"]:
        return False
    if row["category"] in ("blocked", "warning_http"):
        return False
    if row["category"] == "broken_http":
        return True
    if row["category"] == "network":
        return network_working
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check provider links and staleness.")
    parser.add_argument("--json", action="store_true", dest="json_mode", help="Print JSON summary to stdout.")
    args = parser.parse_args()

    providers = load_providers()
    rows = []
    stale = []

    for p in providers:
        name = p.get("name", "<unknown>")
        url = p.get("source_url", "")
        last_verified = p.get("last_verified", "")
        age = days_since(last_verified)
        stale_flag = age is None or age > 30

        ok, detail, category = (False, "Missing source_url", "broken_http")
        if url:
            ok, detail, category = check_url(url)

        row = {
            "name": name,
            "url": url,
            "link_ok": ok,
            "detail": detail,
            "category": category,
            "last_verified": last_verified,
            "age_days": age,
            "stale": stale_flag,
        }
        rows.append(row)
        if stale_flag:
            stale.append(row)

    checked = [r for r in rows if r["url"]]
    any_success = any(r["link_ok"] for r in checked)
    all_network_failures = bool(checked) and all((not r["link_ok"] and r["category"] == "network") for r in checked)
    network_working = any_success or not all_network_failures

    broken = [r for r in rows if is_broken(r, network_working)]
    warnings = [r for r in rows if (not r["link_ok"] and r["category"] in ("blocked", "warning_http"))]

    if all_network_failures and not any_success:
        if REPORT_PATH.exists():
            REPORT_PATH.unlink()
        summary = {
            "network_unavailable": True,
            "providers_checked": len(rows),
            "broken": [],
            "stale": [{"name": r["name"], "url": r["url"], "last_verified": r["last_verified"], "age_days": r["age_days"]} for r in stale],
            "warnings": [],
        }
        if args.json_mode:
            print(json.dumps(summary, indent=2))
        else:
            print("WARNING: Network unavailable — all source URL checks failed with network/TLS errors.")
            print("Skipping broken-links report. Re-run in an environment with outbound HTTPS access.")
        return 0

    summary = {
        "network_unavailable": False,
        "providers_checked": len(rows),
        "broken": [{"name": r["name"], "url": r["url"], "detail": r["detail"], "category": r["category"]} for r in broken],
        "stale": [{"name": r["name"], "url": r["url"], "last_verified": r["last_verified"], "age_days": r["age_days"]} for r in stale],
        "warnings": [{"name": r["name"], "url": r["url"], "detail": r["detail"], "category": r["category"]} for r in warnings],
    }

    if network_working:
        write_report(rows, broken, stale, warnings)
    if args.json_mode:
        print(json.dumps(summary, indent=2))
    else:
        if network_working:
            print(f"Wrote {REPORT_PATH}")
        print(f"Broken: {len(broken)}, Warnings: {len(warnings)}, Stale: {len(stale)}")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())

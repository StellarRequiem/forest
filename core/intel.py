#!/usr/bin/env python3
"""
Forest Threat Intel v1.0 — AbuseIPDB lookup with local file cache

Checks external IPs discovered by NetworkWatcher against AbuseIPDB's
free tier (https://www.abuseipdb.com). Results are cached for 24 hours
to stay well within the free tier limit of 1,000 checks/day.

Setup:
  1. Create a free account at https://www.abuseipdb.com
  2. Generate an API key (Settings → API)
  3. Add to your .env file:  ABUSEIPDB_API_KEY=your_key_here
  4. source .env  (or let setup.sh do this automatically)

If no API key is set, all functions are no-ops and return empty results —
the system runs fine without it; you just won't get cloud reputation checks.

Free tier limits (as of 2026):
  - 1,000 IP checks / day
  - 1,000 reports / day
  - Rate limit: ~1 req/sec
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────────────

ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")
ABUSEIPDB_URL     = "https://api.abuseipdb.com/api/v2/check"

# Confidence score threshold — only report IPs at or above this level
# 25 = low noise, 75 = high-confidence confirmed malicious
CONFIDENCE_THRESHOLD: int = int(os.getenv("ABUSEIPDB_THRESHOLD", "25"))

VAULT_DIR   = Path.home() / "ForestVault"
CACHE_FILE  = VAULT_DIR / "intel_cache.json"
CACHE_TTL_H = 24   # hours before a cached result expires

# RFC1918 + loopback — never query AbuseIPDB for these
_PRIVATE_PREFIXES: tuple[str, ...] = (
    "127.", "10.", "192.168.",
    "172.16.", "172.17.", "172.18.", "172.19.", "172.2",
    "::1", "fe80", "fd", "fc", "0.",
)


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    VAULT_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def _cache_expired(entry: dict) -> bool:
    try:
        fetched_at = datetime.fromisoformat(entry["fetched_at"])
        return datetime.now() - fetched_at > timedelta(hours=CACHE_TTL_H)
    except Exception:
        return True


# ── IP helpers ────────────────────────────────────────────────────────────────

def _is_private(ip: str) -> bool:
    return any(ip.startswith(p) for p in _PRIVATE_PREFIXES)


def _extract_host(conn: str) -> str:
    """
    Extract the host portion from a "host:port" connection string.
    Handles IPv4 ("1.2.3.4:443") and IPv6 ("[::1]:443").
    """
    if conn.startswith("["):
        # IPv6 bracket notation
        end = conn.find("]")
        return conn[1:end] if end != -1 else conn
    return conn.rsplit(":", 1)[0]


# ── AbuseIPDB query ───────────────────────────────────────────────────────────

def _query_abuseipdb(ip: str) -> dict | None:
    """
    Single IP lookup against AbuseIPDB v2.
    Returns the 'data' dict from the response, or None on failure.
    """
    if not _REQUESTS_AVAILABLE:
        return None
    try:
        resp = _requests.get(
            ABUSEIPDB_URL,
            headers={"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
            timeout=8,
        )
        if resp.status_code == 200:
            return resp.json().get("data", {})
        if resp.status_code == 429:
            # Rate limited — back off silently, don't crash
            return None
        if resp.status_code == 401:
            # Bad key — log once and bail
            print("[INTEL] AbuseIPDB returned 401 — check ABUSEIPDB_API_KEY")
            return None
    except Exception:
        pass
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def check_ips(conn_list: list[str]) -> list[dict]:
    """
    Check a list of "host:port" connection strings against AbuseIPDB.

    Returns a list of finding dicts for IPs that meet the confidence
    threshold — empty list if no key is set, no hits, or all cached clean.

    Each finding dict:
      {
        "ip":          str,
        "confidence":  int,    # 0-100, AbuseIPDB abuseConfidenceScore
        "total_reports": int,
        "country":     str,
        "domain":      str,    # reverse DNS if available
        "last_reported": str,  # ISO date
        "alert":       str,    # formatted [INTEL ALERT] string
        "from_cache":  bool,
      }
    """
    if not ABUSEIPDB_API_KEY:
        return []

    cache = _load_cache()
    findings: list[dict] = []
    cache_dirty = False

    # Deduplicate IPs first
    ips_seen: set[str] = set()
    for conn in conn_list:
        ip = _extract_host(conn)
        if not ip or _is_private(ip) or ip in ips_seen:
            continue
        ips_seen.add(ip)

        from_cache = False
        data: dict | None = None

        # Check cache
        if ip in cache and not _cache_expired(cache[ip]):
            data = cache[ip].get("data")
            from_cache = True
        else:
            # Live query — small sleep to respect rate limit
            time.sleep(0.5)
            data = _query_abuseipdb(ip)
            if data is not None:
                cache[ip] = {
                    "fetched_at": datetime.now().isoformat(),
                    "data": data,
                }
                cache_dirty = True

        if data is None:
            continue

        confidence = data.get("abuseConfidenceScore", 0)
        total_reports = data.get("totalReports", 0)

        if confidence >= CONFIDENCE_THRESHOLD:
            country = data.get("countryCode", "??")
            domain = data.get("domain", "")
            last_reported = data.get("lastReportedAt", "")

            severity = (
                "HIGH" if confidence >= 75 else
                "MEDIUM" if confidence >= 50 else
                "LOW"
            )

            alert = (
                f"[INTEL ALERT — {severity}] IP {ip} has confidence score "
                f"{confidence}/100 ({total_reports} abuse reports) on AbuseIPDB. "
                f"Country: {country}. "
                + (f"Domain: {domain}. " if domain else "")
                + (f"Last reported: {last_reported[:10]}." if last_reported else "")
            )

            findings.append({
                "ip":            ip,
                "confidence":    confidence,
                "total_reports": total_reports,
                "country":       country,
                "domain":        domain,
                "last_reported": last_reported,
                "alert":         alert,
                "from_cache":    from_cache,
            })

    if cache_dirty:
        _save_cache(cache)

    return findings


def format_intel_alerts(findings: list[dict]) -> str:
    """
    Format intel findings into a block for LLM prompt injection.
    Returns empty string if no findings.
    """
    if not findings:
        return ""
    block = "[ABUSEIPDB THREAT INTEL — cross-reference with network findings]\n"
    block += "\n".join(f"  • {f['alert']}" for f in findings)
    return block


def cache_stats() -> dict:
    """Return a summary of the current intel cache."""
    cache = _load_cache()
    if not cache:
        return {"entries": 0, "expired": 0}
    now = datetime.now()
    expired = sum(
        1 for v in cache.values()
        if _cache_expired(v)
    )
    return {"entries": len(cache), "expired": expired}


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Intel smoke test ===\n")

    if not ABUSEIPDB_API_KEY:
        print("No ABUSEIPDB_API_KEY set — skipping live query.")
        print("Set the key in .env and re-run to test.")
    else:
        print(f"API key: {ABUSEIPDB_API_KEY[:8]}***")
        # Test with a known-bad IP (this one is frequently reported)
        test_conns = ["185.220.101.1:443", "8.8.8.8:53"]
        findings = check_ips(test_conns)
        if findings:
            print(format_intel_alerts(findings))
        else:
            print("No hits above threshold — either clean IPs or key issue.")

    stats = cache_stats()
    print(f"\nCache: {stats['entries']} entries, {stats['expired']} expired")

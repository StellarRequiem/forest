#!/usr/bin/env python3
"""
Forest Audit Chain Verifier — tools/audit.py

Verifies the integrity of ~/ForestVault/training_chain.json.

The chain file has two historical formats written by different versions:

  FORMAT A (legacy JSON, first ~5 000 lines):
    A JSON array where each entry contains a "previous_hash" field that
    must equal the "hash" field of the preceding entry — a true hash chain.

  FORMAT B (current text, all remaining lines):
    One event per line:
      TIMESTAMP | EVENT_TYPE | DETAILS | Hash: <sha256[:24]>
    The hash is sha256(f"{TIMESTAMP} | {EVENT_TYPE} | {DETAILS}")[:24].
    Each line is independently verifiable.

Usage:
    python3 tools/audit.py               # verify last 1 000 text entries + full JSON chain
    python3 tools/audit.py --full        # verify every text entry (slow on 270K lines)
    python3 tools/audit.py --tail 500    # verify last N text entries
    python3 tools/audit.py --events      # print recent events table
    python3 tools/audit.py --stats       # vault-wide statistics only

Exit code: 0 = clean, 1 = tampered entries found.
"""

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

VAULT      = Path.home() / "ForestVault"
CHAIN_FILE = VAULT / "training_chain.json"

# ── Terminal helpers ──────────────────────────────────────────────────────────

_USE_COLOR = sys.stdout.isatty()
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"
WHITE  = "\033[97m"

def _c(text: str, *codes) -> str:
    if not _USE_COLOR:
        return text
    return "".join(codes) + str(text) + RESET

def _hr(char="─", width=80) -> str:
    import shutil
    w = min(shutil.get_terminal_size().columns, width)
    return char * w


# ── Format B — text line parser & verifier ────────────────────────────────────

_HASH_SUFFIX = " | Hash: "
_HEX_RE      = re.compile(r"^[a-f0-9]+$")
_TEXT_RE     = re.compile(r"^(.+) \| Hash: [a-f0-9]+$")

def _verify_text_line(raw: str) -> tuple[bool | None, str, str, str]:
    """
    Returns (ok, event_type, timestamp, details_snippet).
    ok=None  → line is not a Format-B text entry (skip it).
    ok=True  → hash verified.
    ok=False → hash mismatch (tampered or corrupted).

    Split on the literal ' | Hash: ' suffix using rsplit so that any
    trailing whitespace inside the entry is preserved exactly as-written
    (which is what was hashed at write time).
    """
    line  = raw.rstrip("\n")
    parts = line.rsplit(_HASH_SUFFIX, 1)

    if len(parts) != 2:
        return None, "", "", ""

    entry, stored_hash = parts[0], parts[1].strip()

    if not _HEX_RE.match(stored_hash):
        return None, "", "", ""

    computed = hashlib.sha256(entry.encode()).hexdigest()[:24]
    ok       = (computed == stored_hash)

    # Extract fields from "timestamp | EVENT_TYPE | details"
    fields     = entry.split(" | ", 2)
    timestamp  = fields[0] if len(fields) > 0 else ""
    event_type = fields[1] if len(fields) > 1 else ""
    snippet    = fields[2][:60] if len(fields) > 2 else ""

    return ok, event_type, timestamp, snippet


def verify_text_entries(
    lines: list[str],
    tail:  int | None = 1000,
    verbose: bool = False,
) -> dict:
    """
    Scan text-format lines (Format B).
    tail=None → verify all; tail=N → verify last N matching lines.
    Returns summary dict.
    """
    # Collect all text-format line indices first (fast pass)
    def _is_text_line(l: str) -> bool:
        s = l.rstrip("\n")
        if _HASH_SUFFIX not in s:
            return False
        tail = s.rsplit(_HASH_SUFFIX, 1)[-1].strip()
        return bool(_HEX_RE.match(tail))

    text_indices = [i for i, l in enumerate(lines) if _is_text_line(l)]

    total_text = len(text_indices)
    if tail is not None:
        check_indices = text_indices[-tail:]
    else:
        check_indices = text_indices

    checked  = 0
    ok_count = 0
    bad      = []          # (line_number, event_type, stored, computed)
    event_counts: dict[str, int] = {}
    newest_ts = ""
    oldest_ts = ""

    for idx in check_indices:
        raw = lines[idx]
        ok, etype, ts, snippet = _verify_text_line(raw)
        if ok is None:
            continue
        checked += 1
        event_counts[etype] = event_counts.get(etype, 0) + 1
        if not newest_ts or ts > newest_ts:
            newest_ts = ts
        if not oldest_ts or ts < oldest_ts:
            oldest_ts = ts
        if ok:
            ok_count += 1
        else:
            parts    = raw.rstrip("\n").rsplit(_HASH_SUFFIX, 1)
            stored_r = parts[1].strip() if len(parts) == 2 else "?"
            comp_r   = hashlib.sha256(parts[0].encode()).hexdigest()[:24]
            bad.append((idx + 1, etype, stored_r, comp_r, snippet))

        if verbose and not ok:
            print(_c(f"  ✗ Line {idx+1}: {etype} — hash mismatch", RED))

    return {
        "total_text":   total_text,
        "checked":      checked,
        "ok":           ok_count,
        "tampered":     len(bad),
        "bad_entries":  bad,
        "event_counts": event_counts,
        "oldest_ts":    oldest_ts,
        "newest_ts":    newest_ts,
    }


# ── Format A — JSON chain verifier ───────────────────────────────────────────

def verify_json_chain(lines: list[str]) -> dict:
    """
    Parse the legacy JSON block (Format A) and verify that each entry's
    previous_hash matches the preceding entry's hash field.
    Returns summary dict.
    """
    result = {"entries": 0, "chain_ok": True, "breaks": [], "parse_error": None}

    # The JSON block ends at the first ']' character that appears at the
    # start of a line or immediately before a text-format line.
    json_chars = []
    for line in lines:
        stripped = line.strip()
        if _HASH_SUFFIX in stripped and _HEX_RE.match(stripped.rsplit(_HASH_SUFFIX, 1)[-1].strip()):
            # We've hit the text section; capture any trailing ']' first
            if stripped.startswith("]"):
                json_chars.append("]")
            break
        # Handle the mixed line like ']2026-04-...'
        if stripped.startswith("]"):
            json_chars.append("]")
            break
        json_chars.append(line)

    raw_json = "".join(json_chars).strip()
    if not raw_json.endswith("]"):
        raw_json += "]"

    try:
        entries = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        result["parse_error"] = str(exc)
        return result

    result["entries"] = len(entries)
    prev_hash = None

    for i, entry in enumerate(entries):
        curr_hash = entry.get("hash") or entry.get("prev_hash")
        entry_prev = entry.get("previous_hash") or entry.get("prev_hash")

        if prev_hash is not None and entry_prev is not None:
            if entry_prev != prev_hash:
                result["chain_ok"] = False
                result["breaks"].append({
                    "index":    i,
                    "expected": prev_hash[:16],
                    "found":    entry_prev[:16],
                    "type":     entry.get("type", "?"),
                })
        prev_hash = curr_hash or prev_hash

    return result


# ── Recent events table ───────────────────────────────────────────────────────

def print_recent_events(lines: list[str], n: int = 20) -> None:
    text_lines = [
        l.rstrip("\n") for l in lines
        if _HASH_SUFFIX in l and _HEX_RE.match(l.rstrip("\n").rsplit(_HASH_SUFFIX, 1)[-1].strip())
    ]
    recent     = text_lines[-n:]

    print()
    print(_c(f"  Recent {len(recent)} events", BOLD, WHITE))
    print(_c("  " + _hr(), DIM))

    for raw in recent:
        m = _TEXT_RE.match(raw)
        if not m:
            continue
        entry = m.group(1)
        parts = entry.split(" | ", 2)
        ts    = parts[0][-19:] if len(parts) > 0 else ""   # trim to HH:MM:SS
        etype = parts[1]       if len(parts) > 1 else ""
        det   = parts[2][:55]  if len(parts) > 2 else ""

        # Color by event type
        if "PROMOTE" in etype or "APPROVED" in etype or "PASSED" in etype:
            etype_col = _c(f"{etype:<30}", GREEN)
        elif "BLOCK" in etype or "DENY" in etype or "KILL" in etype:
            etype_col = _c(f"{etype:<30}", RED)
        elif "GRADING" in etype:
            etype_col = _c(f"{etype:<30}", CYAN)
        else:
            etype_col = _c(f"{etype:<30}", DIM)

        ts_col = _c(ts[-8:], DIM)
        print(f"  {ts_col}  {etype_col}  {_c(det, DIM)}")

    print()


# ── Main report ───────────────────────────────────────────────────────────────

def run_report(tail: int | None, show_events: bool, stats_only: bool, full: bool) -> int:
    if not CHAIN_FILE.exists():
        print(_c("  Chain file not found: " + str(CHAIN_FILE), RED))
        return 1

    print()
    print(_c("  🔐 Forest Audit Chain Verifier", BOLD, WHITE))
    print(_c("  " + _hr(), DIM))
    print(_c(f"  File: {CHAIN_FILE}", DIM))

    # Load all lines once
    with open(CHAIN_FILE, errors="replace") as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(_c(f"  Lines: {total_lines:,}", DIM))
    print(_c("  " + _hr(), DIM))

    if show_events:
        print_recent_events(lines)
        return 0

    # ── JSON chain ────────────────────────────────────────────────────────────
    if not stats_only:
        print()
        print(_c("  FORMAT A — Legacy JSON chain", BOLD))
        jresult = verify_json_chain(lines)
        if jresult["parse_error"]:
            print(_c(f"    Parse error: {jresult['parse_error'][:80]}", YELLOW))
        else:
            entries = jresult["entries"]
            if jresult["chain_ok"]:
                icon = _c("✓", GREEN, BOLD)
                status = _c("INTACT", GREEN, BOLD)
            else:
                icon = _c("✗", RED, BOLD)
                status = _c(f"BROKEN — {len(jresult['breaks'])} break(s)", RED, BOLD)
            print(f"    {icon} {entries:,} entries — chain {status}")
            for b in jresult["breaks"][:5]:
                print(_c(f"      Break at index {b['index']}: type={b['type']} "
                         f"expected={b['expected']} found={b['found']}", RED))

    # ── Text entries ──────────────────────────────────────────────────────────
    print()
    if full:
        tail_param = None
        scope_label = "all text entries"
    else:
        tail_param = tail
        scope_label = f"last {tail:,} text entries"

    print(_c(f"  FORMAT B — Text entries ({scope_label})", BOLD))
    tresult = verify_text_entries(lines, tail=tail_param)

    total   = tresult["total_text"]
    checked = tresult["checked"]
    ok      = tresult["ok"]
    bad_n   = tresult["tampered"]

    icon   = _c("✓", GREEN, BOLD) if bad_n == 0 else _c("✗", RED, BOLD)
    status = (_c("ALL VERIFIED", GREEN, BOLD) if bad_n == 0
              else _c(f"{bad_n} TAMPERED", RED, BOLD))
    print(f"    {icon} {checked:,} checked of {total:,} total — {status}")
    print(f"       Time range: {tresult['oldest_ts'][:19]}  →  {tresult['newest_ts'][:19]}")

    if bad_n > 0:
        print()
        print(_c("  Tampered entries:", RED, BOLD))
        for line_no, etype, stored, computed, snippet in tresult["bad_entries"][:10]:
            print(_c(f"    Line {line_no:,}: {etype}", RED))
            print(_c(f"      stored  : {stored}", RED))
            print(_c(f"      computed: {computed}", RED))
            print(_c(f"      content : {snippet}", DIM))

    # ── Event breakdown ───────────────────────────────────────────────────────
    print()
    print(_c("  Event breakdown (checked window):", BOLD))
    counts = sorted(tresult["event_counts"].items(), key=lambda x: -x[1])
    for etype, count in counts[:15]:
        bar_len = min(30, count // max(1, max(v for _, v in counts) // 30))
        bar     = _c("█" * bar_len, CYAN)
        print(f"    {etype:<35} {count:>6,}  {bar}")

    # ── Summary line ──────────────────────────────────────────────────────────
    print()
    print(_c("  " + _hr(), DIM))
    if bad_n == 0:
        print(_c("  ✓ Chain integrity: VERIFIED — no tampering detected", GREEN, BOLD))
    else:
        print(_c(f"  ✗ Chain integrity: {bad_n} entries FAILED hash verification", RED, BOLD))
    print(_c("  " + _hr(), DIM))
    print()

    return 1 if bad_n > 0 else 0


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args  = sys.argv[1:]
    full  = "--full" in args
    stats = "--stats" in args
    evts  = "--events" in args

    tail = 1000
    if "--tail" in args:
        idx = args.index("--tail")
        try:
            tail = int(args[idx + 1])
        except (IndexError, ValueError):
            print("Usage: --tail <number>")
            sys.exit(1)

    sys.exit(run_report(tail=tail, show_events=evts,
                        stats_only=stats, full=full))

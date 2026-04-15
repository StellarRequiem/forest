#!/usr/bin/env python3
"""
Forest Report Generator — tools/report.py

Reads ~/ForestVault/training_chain.json, extracts all GRADING_COMPLETED events,
computes per-worker score statistics, identifies trends, and writes a dated
Markdown report to ~/ForestVault/reports/.

Usage:
    python3 tools/report.py               # generate report for all time
    python3 tools/report.py --days 7      # last 7 days only
    python3 tools/report.py --stdout      # print to terminal, don't save
    ./bin/forest-report                   # via launcher
"""

import argparse
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

VAULT_DIR    = Path.home() / "ForestVault"
CHAIN_FILE   = VAULT_DIR  / "training_chain.json"
REPORTS_DIR  = VAULT_DIR  / "reports"
HASH_SUFFIX  = " | Hash: "

WORKERS = ["network_watcher", "log_anomaly_specialist", "threat_pattern_detector"]
WORKER_SHORT = {
    "network_watcher":        "Network",
    "log_anomaly_specialist": "Log",
    "threat_pattern_detector":"Threat",
}


# ── Parse audit chain ─────────────────────────────────────────────────────────

def _parse_grading_events(since: datetime | None = None) -> list[dict]:
    """
    Extract all GRADING_COMPLETED events from the chain file.
    Returns list of dicts: {timestamp, worker, score, decision, const, useful, eff, nov}
    """
    if not CHAIN_FILE.exists():
        return []

    events = []
    pattern = re.compile(
        r"(\S+) \| GRADING_COMPLETED \| (\w+) \| "
        r"score=([\d.]+) \| decision=(\w+) \| "
        r"const=(\d+) useful=(\d+) eff=(\d+) nov=(\d+)"
    )

    with open(CHAIN_FILE, errors="replace") as f:
        for line in f:
            if "GRADING_COMPLETED" not in line:
                continue
            m = pattern.search(line)
            if not m:
                continue
            try:
                ts = datetime.fromisoformat(m.group(1))
            except ValueError:
                continue
            if since and ts < since:
                continue
            events.append({
                "timestamp": ts,
                "worker":    m.group(2),
                "score":     float(m.group(3)),
                "decision":  m.group(4),
                "const":     int(m.group(5)),
                "useful":    int(m.group(6)),
                "eff":       int(m.group(7)),
                "nov":       int(m.group(8)),
            })

    return events


# ── Statistics ────────────────────────────────────────────────────────────────

def _stats(scores: list[float]) -> dict:
    if not scores:
        return {"n": 0, "mean": 0, "min": 0, "max": 0, "stdev": 0, "trend": "—"}
    n = len(scores)
    mean  = round(statistics.mean(scores), 1)
    lo    = round(min(scores), 1)
    hi    = round(max(scores), 1)
    stdev = round(statistics.stdev(scores), 1) if n >= 2 else 0.0

    # Simple trend: compare first-half mean vs second-half mean
    if n >= 6:
        half    = n // 2
        first   = statistics.mean(scores[:half])
        second  = statistics.mean(scores[half:])
        delta   = second - first
        if delta > 2:
            trend = f"↑ +{delta:.1f}"
        elif delta < -2:
            trend = f"↓ {delta:.1f}"
        else:
            trend = "→ stable"
    else:
        trend = "→ (need more data)"

    return {"n": n, "mean": mean, "min": lo, "max": hi, "stdev": stdev, "trend": trend}


def _decision_counts(events: list[dict]) -> dict[str, dict]:
    counts: dict[str, dict] = defaultdict(lambda: {"PROMOTE": 0, "MAINTAIN": 0, "REVIEW": 0})
    for e in events:
        d = e["decision"]
        if d in counts[e["worker"]]:
            counts[e["worker"]][d] += 1
    return dict(counts)


# ── Report rendering ──────────────────────────────────────────────────────────

def _bar(value: float, max_val: float = 100, width: int = 20) -> str:
    """ASCII progress bar."""
    filled = round(value / max_val * width)
    return "█" * filled + "░" * (width - filled)


def build_report(events: list[dict], days: int | None = None) -> str:
    now      = datetime.now()
    period   = f"Last {days} days" if days else "All time"
    n_events = len(events)

    lines = [
        f"# Forest CUS — Score Report",
        f"",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Period:** {period}  ",
        f"**Total grading events:** {n_events}",
        f"",
    ]

    if n_events == 0:
        lines.append("*No grading events found for this period. "
                     "Run at least one swarm cycle first.*")
        return "\n".join(lines)

    # Group by worker
    by_worker: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        by_worker[e["worker"]].append(e)

    decisions = _decision_counts(events)

    # ── Per-worker summary ────────────────────────────────────────────────────
    lines += ["## Per-Worker Summary", ""]
    lines += [
        "| Worker | Cycles | Mean | Min | Max | Stdev | Trend | PROMOTE | MAINTAIN | REVIEW |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for w in WORKERS:
        evts   = by_worker.get(w, [])
        scores = [e["score"] for e in evts]
        s      = _stats(scores)
        dc     = decisions.get(w, {"PROMOTE": 0, "MAINTAIN": 0, "REVIEW": 0})
        short  = WORKER_SHORT.get(w, w)
        lines.append(
            f"| {short} | {s['n']} | **{s['mean']}** | {s['min']} | {s['max']} "
            f"| {s['stdev']} | {s['trend']} | {dc['PROMOTE']} | {dc['MAINTAIN']} | {dc['REVIEW']} |"
        )

    lines += [""]

    # ── Score distribution bar chart ──────────────────────────────────────────
    lines += ["## Score Distribution", ""]
    buckets = {"90–100": 0, "80–89": 0, "70–79": 0, "60–69": 0, "<60": 0}
    for e in events:
        s = e["score"]
        if s >= 90:   buckets["90–100"] += 1
        elif s >= 80: buckets["80–89"]  += 1
        elif s >= 70: buckets["70–79"]  += 1
        elif s >= 60: buckets["60–69"]  += 1
        else:         buckets["<60"]    += 1

    for bucket, count in buckets.items():
        pct  = count / n_events * 100 if n_events else 0
        bar  = _bar(pct)
        lines.append(f"  `{bucket:6s}` {bar} {count:3d} ({pct:4.1f}%)")

    lines += [""]

    # ── Dimension analysis ────────────────────────────────────────────────────
    lines += ["## Grading Dimension Averages", ""]
    lines += ["| Dimension | Weight | Average | Bar |",
              "|---|---|---|---|"]

    dims = [
        ("constitution", "const", "45%"),
        ("usefulness",   "useful","30%"),
        ("efficiency",   "eff",   "15%"),
        ("novelty",      "nov",   "10%"),
    ]
    for label, key, weight in dims:
        vals  = [e[key] for e in events if key in e]
        avg   = statistics.mean(vals) if vals else 0
        bar   = _bar(avg)
        lines.append(f"| {label:<14} | {weight} | {avg:5.1f} | `{bar}` |")

    lines += [""]

    # ── Recent 10 cycles ──────────────────────────────────────────────────────
    recent = sorted(events, key=lambda e: e["timestamp"], reverse=True)[:15]
    lines += ["## Most Recent 15 Grading Events", ""]
    lines += ["| Time | Worker | Score | Decision |",
              "|---|---|---|---|"]
    for e in recent:
        ts    = e["timestamp"].strftime("%m-%d %H:%M")
        short = WORKER_SHORT.get(e["worker"], e["worker"])
        dec   = e["decision"]
        badge = {"PROMOTE": "🟢", "MAINTAIN": "🟡", "REVIEW": "🔴"}.get(dec, "⚪")
        lines.append(f"| {ts} | {short} | {e['score']:.1f} | {badge} {dec} |")

    lines += [""]

    # ── Health summary ────────────────────────────────────────────────────────
    total_scores = [e["score"] for e in events]
    overall_mean = statistics.mean(total_scores) if total_scores else 0
    promote_pct  = buckets["90–100"] + buckets["80–89"]
    promote_rate = promote_pct / n_events * 100 if n_events else 0

    if overall_mean >= 85 and promote_rate >= 70:
        health = "🟢 **HEALTHY** — swarm is performing well"
    elif overall_mean >= 70:
        health = "🟡 **STABLE** — acceptable performance, monitor for degradation"
    else:
        health = "🔴 **DEGRADED** — review worker outputs and model availability"

    lines += [
        "## Swarm Health",
        "",
        f"Overall mean score: **{overall_mean:.1f}**  ",
        f"PROMOTE rate: **{promote_rate:.0f}%**  ",
        f"Status: {health}",
        "",
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Forest report generator — reads audit chain, outputs Markdown"
    )
    parser.add_argument(
        "--days", type=int, default=0, metavar="N",
        help="Limit to last N days (default: all time)",
    )
    parser.add_argument(
        "--stdout", action="store_true",
        help="Print report to terminal instead of saving to file",
    )
    args = parser.parse_args()

    since = None
    if args.days > 0:
        since = datetime.now() - timedelta(days=args.days)

    events = _parse_grading_events(since=since)
    report = build_report(events, days=args.days if args.days > 0 else None)

    if args.stdout:
        print(report)
        return

    REPORTS_DIR.mkdir(exist_ok=True)
    fname = REPORTS_DIR / f"forest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    fname.write_text(report)
    print(f"Report saved → {fname}")
    print(f"  Events analysed : {len(events)}")
    if events:
        scores = [e["score"] for e in events]
        print(f"  Overall mean    : {statistics.mean(scores):.1f}")
        print(f"  Score range     : {min(scores):.1f} – {max(scores):.1f}")


if __name__ == "__main__":
    main()

"""
Forest Dashboard — dashboard/app.py

Three tabs:
  🌲 Swarm Monitor  — live worker outputs, scores, recent audit events
  🎯 Trainer Hub    — phishing, URL, and password trainers
  🔐 Audit Chain    — chain integrity + event breakdown

Run:
    streamlit run dashboard/app.py
    # or
    ./bin/forest-dash
"""

import json
import re
import hashlib
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
import psutil

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Forest CUS",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
VAULT         = Path.home() / "ForestVault"
PROPOSALS_DIR = VAULT / "proposals"
ARCHIVE_DIR   = VAULT / "proposals_archive"
CHAIN_FILE    = VAULT / "training_chain.json"
HASH_SUFFIX   = " | Hash: "

# ── Scenario data ─────────────────────────────────────────────────────────────
try:
    from dashboard.scenarios import PHISHING_SCENARIOS, URL_SCENARIOS, evaluate_password
except ImportError:
    from scenarios import PHISHING_SCENARIOS, URL_SCENARIOS, evaluate_password


# ══════════════════════════════════════════════════════════════════════════════
# Data loading helpers
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30)
def load_proposals(directory: Path) -> list[dict]:
    """Parse all proposal .md files into dicts."""
    results = []
    for f in sorted(directory.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            text = f.read_text(errors="replace")
            p    = {"file": f.name, "worker": "unknown", "timestamp": "",
                    "task": "", "output": "", "score": 0.0,
                    "decision": "REVIEW", "points": 0}

            m = re.match(r"#\s+(\S+)\s+[—-]\s+(.+)", text)
            if m:
                p["worker"]    = m.group(1)
                p["timestamp"] = m.group(2).strip()

            m = re.search(r"\*\*Task\*\*:\s*(.+)", text)
            if m:
                p["task"] = m.group(1).strip()

            m = re.search(r"\*\*Output\*\*:\s*\n(.*?)\n\*\*Grade\*\*", text, re.DOTALL)
            if m:
                p["output"] = m.group(1).strip()

            m = re.search(r"\*\*Grade\*\*:\s*([\d.]+)\s*[→>]\s*(\w+)\s*\(\+(\d+)", text)
            if m:
                p["score"]    = float(m.group(1))
                p["decision"] = m.group(2)
                p["points"]   = int(m.group(3))

            results.append(p)
        except Exception:
            pass
    return results


@st.cache_data(ttl=30)
def load_recent_events(n: int = 50) -> list[dict]:
    """Read last N text-format events from the audit chain."""
    if not CHAIN_FILE.exists():
        return []
    events = []
    try:
        with open(CHAIN_FILE, errors="replace") as f:
            lines = f.readlines()
        for line in reversed(lines):
            line = line.rstrip("\n")
            if HASH_SUFFIX not in line:
                continue
            parts = line.rsplit(HASH_SUFFIX, 1)
            if len(parts) != 2:
                continue
            entry, stored = parts
            fields     = entry.split(" | ", 2)
            if len(fields) < 2:
                continue
            events.append({
                "timestamp":  fields[0],
                "event_type": fields[1],
                "details":    fields[2] if len(fields) > 2 else "",
                "hash":       stored.strip(),
            })
            if len(events) >= n:
                break
    except Exception:
        pass
    return events


@st.cache_data(ttl=60)
def chain_stats() -> dict:
    """Quick stats: total text lines, event counts."""
    if not CHAIN_FILE.exists():
        return {"total": 0, "counts": {}}
    counts: dict[str, int] = {}
    total = 0
    try:
        with open(CHAIN_FILE, errors="replace") as f:
            for line in f:
                if HASH_SUFFIX in line:
                    total += 1
                    parts = line.split(" | ", 2)
                    if len(parts) >= 2:
                        e = parts[1].strip()
                        counts[e] = counts.get(e, 0) + 1
    except Exception:
        pass
    return {"total": total, "counts": counts}


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> None:
    st.sidebar.title("🌲 Forest CUS")
    st.sidebar.caption("Blue-Team AI Monitoring Swarm")
    st.sidebar.divider()

    queue_count   = len(list(PROPOSALS_DIR.glob("*.md")))
    archive_count = len(list(ARCHIVE_DIR.rglob("*.md")))
    cs            = chain_stats()

    st.sidebar.metric("Proposals in queue", queue_count)
    st.sidebar.metric("Proposals archived", archive_count)
    st.sidebar.metric("Audit events",       f"{cs['total']:,}")

    st.sidebar.divider()

    # System snapshot
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    st.sidebar.caption("System")
    st.sidebar.progress(int(cpu),  text=f"CPU {cpu:.0f}%")
    st.sidebar.progress(int(mem.percent), text=f"RAM {mem.percent:.0f}%")

    st.sidebar.divider()
    st.sidebar.caption(f"Refreshed: {datetime.now().strftime('%H:%M:%S')}")
    if st.sidebar.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Tab 1 — Swarm Monitor
# ══════════════════════════════════════════════════════════════════════════════

DECISION_COLOR = {"PROMOTE": "🟢", "MAINTAIN": "🟡", "REVIEW": "🔴"}
WORKER_ICON    = {
    "network_watcher":        "🌐",
    "log_anomaly_specialist": "📋",
    "threat_pattern_detector":"🛡️",
}

def render_swarm_monitor() -> None:
    st.header("🌲 Swarm Monitor")

    all_props  = load_proposals(PROPOSALS_DIR)
    arch_props = load_proposals(ARCHIVE_DIR) if ARCHIVE_DIR.exists() else []
    all_data   = all_props + arch_props

    if not all_data:
        st.info("No proposals yet. Run a swarm cycle to see data here.\n\n"
                "```bash\necho 'yes' | python3 core/cus_langgraph.py\n```")
        return

    # ── Latest cycle summary ──────────────────────────────────────────────────
    st.subheader("Latest Cycle")
    latest = all_props[:3] if all_props else all_data[:3]

    cols = st.columns(len(latest))
    for col, p in zip(cols, latest):
        icon  = WORKER_ICON.get(p["worker"], "🔹")
        badge = DECISION_COLOR.get(p["decision"], "⚪")
        with col:
            st.metric(
                label=f"{icon} {p['worker'].replace('_', ' ').title()}",
                value=f"{p['score']:.1f}",
                delta=f"{badge} {p['decision']}",
            )
            with st.expander("View output"):
                st.write(p["output"])
                st.caption(f"Task: {p['task']}")
                st.caption(f"File: {p['file']}")

    st.divider()

    # ── Score trend ───────────────────────────────────────────────────────────
    if len(all_data) >= 3:
        st.subheader("Score Trend (all cycles)")

        # Group into cycles of 3 by file timestamp, build chart data
        import pandas as pd

        rows = []
        for p in reversed(all_data):
            ts_str = p["timestamp"][:16] if p["timestamp"] else p["file"]
            rows.append({
                "time":   ts_str,
                "worker": p["worker"].replace("_", " "),
                "score":  p["score"],
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            # Pivot so each worker is a column
            try:
                pivot = df.pivot_table(
                    index="time", columns="worker",
                    values="score", aggfunc="mean"
                ).reset_index()
                pivot = pivot.set_index("time")
                st.line_chart(pivot, height=250)
            except Exception:
                st.line_chart(df[["score"]], height=200)

    st.divider()

    # ── Proposal queue table ──────────────────────────────────────────────────
    st.subheader(f"Proposal Queue ({len(all_props)} pending)")
    if all_props:
        for p in all_props:
            icon  = WORKER_ICON.get(p["worker"], "🔹")
            badge = DECISION_COLOR.get(p["decision"], "⚪")
            with st.expander(
                f"{icon} {p['worker']}  —  {badge} {p['decision']}  "
                f"({p['score']:.1f})  —  {p['timestamp'][:16]}"
            ):
                st.write(p["output"])
                st.caption(f"Points: +{p['points']}  |  File: {p['file']}")
    else:
        st.caption("Queue is empty. Run a cycle to populate it.")

    st.divider()

    # ── Recent audit events ───────────────────────────────────────────────────
    st.subheader("Recent Audit Events")
    events = load_recent_events(20)
    if events:
        import pandas as pd
        df_e = pd.DataFrame([{
            "Time":       e["timestamp"][11:19],
            "Event":      e["event_type"],
            "Details":    e["details"][:80],
        } for e in events])
        st.dataframe(df_e, use_container_width=True, hide_index=True)
    else:
        st.caption("No audit events found.")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2 — Trainer Hub
# ══════════════════════════════════════════════════════════════════════════════

def render_trainer_hub() -> None:
    st.header("🎯 Trainer Hub")
    st.caption("Blue-team awareness training — phishing detection, URL analysis, password hygiene")

    trainer = st.radio(
        "Select trainer",
        ["🎣 Phishing Detection", "🔗 URL Risk Scanner", "🔑 Password Hygiene"],
        horizontal=True,
    )

    st.divider()

    if trainer == "🎣 Phishing Detection":
        render_phishing_trainer()
    elif trainer == "🔗 URL Risk Scanner":
        render_url_trainer()
    else:
        render_password_trainer()


# ── Phishing trainer ──────────────────────────────────────────────────────────

def render_phishing_trainer() -> None:
    st.subheader("🎣 Phishing Detection")
    st.write("Read each email. Decide: is it phishing or legitimate?")

    # Session state
    if "ph_idx" not in st.session_state:
        st.session_state.ph_idx      = 0
        st.session_state.ph_score    = 0
        st.session_state.ph_answered = False
        st.session_state.ph_order    = list(range(len(PHISHING_SCENARIOS)))
        random.shuffle(st.session_state.ph_order)
        st.session_state.ph_history  = []

    idx   = st.session_state.ph_idx
    order = st.session_state.ph_order
    total = len(PHISHING_SCENARIOS)

    # Score bar
    col1, col2, col3 = st.columns(3)
    col1.metric("Question", f"{min(idx + 1, total)} / {total}")
    col2.metric("Score",    f"{st.session_state.ph_score} / {idx}")
    pct = round(st.session_state.ph_score / idx * 100) if idx > 0 else 0
    col3.metric("Accuracy", f"{pct}%")

    if idx >= total:
        _show_phishing_results()
        return

    scenario = PHISHING_SCENARIOS[order[idx]]

    # Progress
    st.progress((idx) / total)

    # Email card
    st.markdown("**Email:**")
    st.code(scenario["prompt"], language=None)
    st.caption(f"Category: {scenario['category']}")

    if not st.session_state.ph_answered:
        col_a, col_b = st.columns(2)
        if col_a.button("🚨 Phishing", use_container_width=True, type="primary"):
            _ph_submit("phishing", scenario)
        if col_b.button("✅ Legitimate", use_container_width=True):
            _ph_submit("safe", scenario)
    else:
        _ph_show_feedback(scenario)
        if st.button("Next →", type="primary"):
            st.session_state.ph_idx     += 1
            st.session_state.ph_answered = False
            st.rerun()


def _ph_submit(answer: str, scenario: dict) -> None:
    correct = answer == scenario["answer"]
    if correct:
        st.session_state.ph_score += 1
    st.session_state.ph_answered = True
    st.session_state.ph_last_correct = correct
    st.rerun()


def _ph_show_feedback(scenario: dict) -> None:
    if st.session_state.ph_last_correct:
        st.success(f"✅ Correct! **{scenario['answer'].upper()}**")
    else:
        st.error(f"❌ Wrong — this was **{scenario['answer'].upper()}**")
        st.info(f"💡 {scenario['hint']}")
    st.write(f"**Why:** {scenario['explanation']}")


def _show_phishing_results() -> None:
    total = len(PHISHING_SCENARIOS)
    score = st.session_state.ph_score
    pct   = round(score / total * 100)
    st.balloons() if pct >= 80 else None

    if pct >= 90:
        grade, msg = "A", "Excellent — you have strong phishing awareness."
    elif pct >= 75:
        grade, msg = "B", "Good — review the scenarios you missed."
    elif pct >= 60:
        grade, msg = "C", "Fair — consider re-reading the phishing indicators."
    else:
        grade, msg = "D", "Needs work — carefully study the explanations below."

    st.metric("Final Score", f"{score}/{total} ({pct}%)", delta=f"Grade: {grade}")
    st.write(msg)

    _save_session("phishing", score, total, pct)

    if st.button("🔄 Restart"):
        for k in ["ph_idx", "ph_score", "ph_answered", "ph_order", "ph_history"]:
            del st.session_state[k]
        st.rerun()


# ── URL trainer ───────────────────────────────────────────────────────────────

_RISK_COLORS = {"high": "🔴 HIGH", "medium": "🟡 MEDIUM", "low": "🟢 LOW"}

def render_url_trainer() -> None:
    st.subheader("🔗 URL Risk Scanner")
    st.write("Assess the risk level of each URL: High / Medium / Low.")

    if "url_idx" not in st.session_state:
        st.session_state.url_idx      = 0
        st.session_state.url_score    = 0
        st.session_state.url_answered = False
        st.session_state.url_order    = list(range(len(URL_SCENARIOS)))
        random.shuffle(st.session_state.url_order)

    idx   = st.session_state.url_idx
    order = st.session_state.url_order
    total = len(URL_SCENARIOS)

    col1, col2, col3 = st.columns(3)
    col1.metric("Question", f"{min(idx + 1, total)} / {total}")
    col2.metric("Score",    f"{st.session_state.url_score} / {idx}")
    pct = round(st.session_state.url_score / idx * 100) if idx > 0 else 0
    col3.metric("Accuracy", f"{pct}%")

    if idx >= total:
        _show_url_results()
        return

    scenario = URL_SCENARIOS[order[idx]]
    st.progress(idx / total)

    st.markdown("**URL:**")
    st.code(scenario["url"], language=None)
    st.caption(f"Category: {scenario['category']}")

    if not st.session_state.url_answered:
        c1, c2, c3 = st.columns(3)
        if c1.button("🔴 High Risk",   use_container_width=True, type="primary"):
            _url_submit("high", scenario)
        if c2.button("🟡 Medium Risk", use_container_width=True):
            _url_submit("medium", scenario)
        if c3.button("🟢 Low Risk",    use_container_width=True):
            _url_submit("low", scenario)
    else:
        _url_show_feedback(scenario)
        if st.button("Next →", type="primary"):
            st.session_state.url_idx     += 1
            st.session_state.url_answered = False
            st.rerun()


def _url_submit(answer: str, scenario: dict) -> None:
    correct = answer == scenario["risk"]
    if correct:
        st.session_state.url_score += 1
    st.session_state.url_answered = True
    st.session_state.url_last_correct = correct
    st.rerun()


def _url_show_feedback(scenario: dict) -> None:
    label = _RISK_COLORS[scenario["risk"]]
    if st.session_state.url_last_correct:
        st.success(f"✅ Correct! Risk level: **{label}**")
    else:
        st.error(f"❌ Wrong — actual risk: **{label}**")
        st.info(f"💡 {scenario['hint']}")
    st.write(f"**Why:** {scenario['explanation']}")


def _show_url_results() -> None:
    total = len(URL_SCENARIOS)
    score = st.session_state.url_score
    pct   = round(score / total * 100)
    st.metric("Final Score", f"{score}/{total} ({pct}%)")
    _save_session("url_risk", score, total, pct)
    if st.button("🔄 Restart"):
        for k in ["url_idx", "url_score", "url_answered", "url_order"]:
            del st.session_state[k]
        st.rerun()


# ── Password trainer ──────────────────────────────────────────────────────────

def render_password_trainer() -> None:
    st.subheader("🔑 Password Hygiene Checker")
    st.write("Test the strength of any password and see exactly what to improve.")

    pw = st.text_input("Enter a password to evaluate:", type="password",
                       placeholder="Type any password…")

    if not pw:
        st.caption("Your password is never stored or transmitted.")
        st.info(
            "**Tips for a strong password:**\n"
            "- 16+ characters\n"
            "- Mix of uppercase, lowercase, numbers, symbols\n"
            "- Avoid common words and keyboard patterns\n"
            "- Use a passphrase: `correct-horse-battery-staple`"
        )
        return

    result = evaluate_password(pw)
    score  = result["score"]
    rating = result["rating"]

    # Score meter
    color = {"strong": "green", "moderate": "orange", "weak": "red"}[rating]
    st.progress(score / 100)

    col1, col2 = st.columns(2)
    col1.metric("Strength Score", f"{score}/100")
    col2.metric("Rating", rating.upper(), delta=None)

    # Issues and good points
    c_good, c_bad = st.columns(2)
    with c_good:
        if result["good_points"]:
            st.markdown("**✅ Strengths**")
            for g in result["good_points"]:
                st.markdown(f"- {g}")
    with c_bad:
        if result["issues"]:
            st.markdown("**❌ Issues**")
            for i in result["issues"]:
                st.markdown(f"- {i}")

    # Improvement suggestion
    if rating != "strong":
        st.divider()
        st.markdown("**Suggested improvement:**")
        import secrets, string
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        suggestion = "".join(secrets.choice(chars) for _ in range(20))
        st.code(suggestion)
        st.caption("(Randomly generated — do not use this exact example)")


# ── Session saver ─────────────────────────────────────────────────────────────

def _save_session(trainer: str, score: int, total: int, pct: int) -> None:
    log_file = VAULT / f"{trainer}_sessions.json"
    entry    = {
        "date":       datetime.now().isoformat(),
        "score":      score,
        "total":      total,
        "percentage": pct,
    }
    try:
        history = json.loads(log_file.read_text()) if log_file.exists() else []
        history.append(entry)
        log_file.write_text(json.dumps(history, indent=2))
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3 — Audit Chain
# ══════════════════════════════════════════════════════════════════════════════

def render_audit_tab() -> None:
    st.header("🔐 Audit Chain")
    st.caption("SHA-256 integrity verification for ~/ForestVault/training_chain.json")

    cs = chain_stats()

    col1, col2 = st.columns(2)
    col1.metric("Total audited events", f"{cs['total']:,}")

    # Quick verification of last 200 events
    if CHAIN_FILE.exists():
        ok, bad, checked = _quick_verify(200)
        if bad == 0:
            col2.metric("Chain integrity", "✅ VERIFIED", delta=f"{checked} events checked")
            st.success(f"Last {checked} entries verified — no tampering detected.")
        else:
            col2.metric("Chain integrity", "⚠️ ISSUES", delta=f"{bad} failed")
            st.error(f"{bad} entries failed SHA-256 verification.")
    else:
        col2.metric("Chain integrity", "⚠️ No chain file")

    st.divider()

    # Event breakdown
    if cs["counts"]:
        st.subheader("Event Breakdown")
        import pandas as pd
        df = pd.DataFrame(
            sorted(cs["counts"].items(), key=lambda x: -x[1]),
            columns=["Event Type", "Count"],
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # Full event feed
    st.subheader("Event Feed")
    n = st.slider("Events to show", 10, 200, 50, step=10)
    events = load_recent_events(n)
    if events:
        import pandas as pd
        df_e = pd.DataFrame([{
            "Timestamp":  e["timestamp"][:19],
            "Event Type": e["event_type"],
            "Details":    e["details"][:100],
            "Hash":       e["hash"][:12] + "…",
        } for e in events])
        st.dataframe(df_e, use_container_width=True, hide_index=True)


def _quick_verify(n: int) -> tuple[int, int, int]:
    """Verify last N text-format entries. Returns (ok, bad, checked)."""
    if not CHAIN_FILE.exists():
        return 0, 0, 0
    lines = []
    try:
        with open(CHAIN_FILE, errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return 0, 0, 0

    text_lines = [
        l for l in lines
        if HASH_SUFFIX in l
    ][-n:]

    ok = bad = 0
    for line in text_lines:
        parts = line.rstrip("\n").rsplit(HASH_SUFFIX, 1)
        if len(parts) != 2:
            continue
        entry, stored = parts
        computed = hashlib.sha256(entry.encode()).hexdigest()[:24]
        if computed == stored.strip():
            ok += 1
        else:
            bad += 1
    return ok, bad, ok + bad


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    render_sidebar()

    tab1, tab2, tab3 = st.tabs([
        "🌲 Swarm Monitor",
        "🎯 Trainer Hub",
        "🔐 Audit Chain",
    ])

    with tab1:
        render_swarm_monitor()

    with tab2:
        render_trainer_hub()

    with tab3:
        render_audit_tab()


if __name__ == "__main__":
    main()

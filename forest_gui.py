#!/usr/bin/env python3
"""
Forest Control Panel — Shippable macOS GUI (Streamlit)
Double-click ready once packaged.
"""
import streamlit as st
from pathlib import Path
import json
import subprocess
import time
from datetime import datetime

st.set_page_config(page_title="Forest Control Panel", page_icon="🌲", layout="wide")
st.title("🌲 Forest Control Panel")
st.caption("Living blue-team organism — fully local, refusal-first")

VAULT = Path.home() / "ForestVault"
WELL_DIR = VAULT / "TheWell"
REPORT_DIR = VAULT / "DailyReports"

# Sidebar controls
st.sidebar.header("Controls")
if st.sidebar.button("🚀 Run 15-minute Hard Cycle"):
    with st.spinner("Launching cycle..."):
        subprocess.run(["tmux", "send-keys", "-t", "forest", "cd ~/Forest && source venv/bin/activate && python forest_workday_runner.py --hours 0.25", "C-m"])
    st.success("Cycle launched in tmux 'forest'")

if st.sidebar.button("🔄 Refresh Dashboard"):
    st.rerun()

# Live Dashboard
st.subheader("Live Status")
if Path("forest_dashboard.py").exists():
    try:
        result = subprocess.run(["python", "forest_dashboard.py"], capture_output=True, text=True, timeout=5)
        st.text(result.stdout)
    except:
        st.info("Dashboard running in background — check terminal if needed")
else:
    st.warning("forest_dashboard.py not found")

# Nutrients Browser
st.subheader("TheWell Nutrients")
nutrients = list(WELL_DIR.glob("nutrient_*.json"))
st.write(f"Total stored: **{len(nutrients)}**")
if nutrients:
    latest = max(nutrients, key=lambda p: p.stat().st_mtime)
    with st.expander("View Latest Nutrient", expanded=True):
        data = json.loads(latest.read_text())
        st.json(data)

# Reports
st.subheader("Recent Reports")
reports = sorted(REPORT_DIR.glob("work_report_*.md"), reverse=True)[:5]
for r in reports:
    st.write(f"**{r.name}** — {r.stat().st_mtime}")
    with st.expander("View Report"):
        st.markdown(r.read_text())

st.caption("Forest is alive and improving itself. Run cycles from the sidebar. The full app will be packaged into a double-clickable .app next.")

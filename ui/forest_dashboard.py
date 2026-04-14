#!/usr/bin/env python3
"""
Forest Unified Monitoring Dashboard
Real-time visualization of all Forest systems
- Live Cryptex logs
- Agent performance
- Network topology
- System health
- Process monitoring
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add Forest path
FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from core.dashboard.data_aggregator import DataAggregator

# Page configuration
st.set_page_config(
    page_title="🌲 Forest Dashboard",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    .stMetric {
        background-color: #1f1f1f;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize aggregator
@st.cache_resource
def get_aggregator():
    return DataAggregator()

agg = get_aggregator()

# Sidebar
st.sidebar.markdown("# 🌲 FOREST CONTROL CENTER")
st.sidebar.markdown("---")

refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 10)
selected_tabs = st.sidebar.multiselect(
    "Show Sections",
    ["Overview", "Cryptex Logs", "Agent Performance", "Network", "System Health", "Processes"],
    default=["Overview", "Cryptex Logs", "Agent Performance", "System Health"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**System Info**")
st.sidebar.write(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# Main content
st.markdown("# 🌲 FOREST UNIFIED MONITORING DASHBOARD")
st.markdown("Real-time visibility into all Forest systems")

# Refresh data
all_data = agg.get_all_data()

# ===== OVERVIEW TAB =====
if "Overview" in selected_tabs:
    st.markdown("## 📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stats = all_data['cryptex']['stats']
        st.metric(
            "Total Events (Cryptex)",
            f"{stats['total_events']:,}",
            f"Last 24h: {stats['recent_24h']}"
        )
    
    with col2:
        agents = all_data['agents']
        st.metric(
            "Agents Tracked",
            len(agents),
            f"Active performance data"
        )
    
    with col3:
        system = all_data['system']
        st.metric(
            "CPU Usage",
            f"{system['cpu_percent']:.1f}%",
            f"of {system['cpu_count']} cores"
        )
    
    with col4:
        st.metric(
            "Memory Usage",
            f"{system['memory']['percent']:.1f}%",
            f"{system['memory']['used'] / (1024**3):.1f}GB / {system['memory']['total'] / (1024**3):.1f}GB"
        )
    
    # System health gauge
    st.markdown("### System Health Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpu = all_data['system']['cpu_percent']
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cpu,
            title={'text': "CPU Usage"},
            delta={'reference': 50},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "green" if cpu < 50 else "yellow" if cpu < 80 else "red"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 80], 'color': "gray"},
                       {'range': [80, 100], 'color': "darkgray"}
                   ],
                   'threshold': {'line': {'color': "red"}, 'thickness': 4, 'value': 90}}
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='#1f1f1f',
            plot_bgcolor='#0a0a0a',
            font=dict(color='#e0e0e0')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        mem = all_data['system']['memory']['percent']
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=mem,
            title={'text': "Memory Usage"},
            delta={'reference': 60},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "green" if mem < 60 else "yellow" if mem < 85 else "red"},
                   'steps': [
                       {'range': [0, 60], 'color': "lightgray"},
                       {'range': [60, 85], 'color': "gray"},
                       {'range': [85, 100], 'color': "darkgray"}
                   ],
                   'threshold': {'line': {'color': "red"}, 'thickness': 4, 'value': 90}}
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='#1f1f1f',
            plot_bgcolor='#0a0a0a',
            font=dict(color='#e0e0e0')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        disk = all_data['system']['disk']['percent']
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=disk,
            title={'text': "Disk Usage"},
            delta={'reference': 70},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "green" if disk < 70 else "yellow" if disk < 85 else "red"},
                   'steps': [
                       {'range': [0, 70], 'color': "lightgray"},
                       {'range': [70, 85], 'color': "gray"},
                       {'range': [85, 100], 'color': "darkgray"}
                   ],
                   'threshold': {'line': {'color': "red"}, 'thickness': 4, 'value': 90}}
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='#1f1f1f',
            plot_bgcolor='#0a0a0a',
            font=dict(color='#e0e0e0')
        )
        st.plotly_chart(fig, use_container_width=True)

# ===== CRYPTEX LOGS TAB =====
if "Cryptex Logs" in selected_tabs:
    st.markdown("## 🔐 Cryptex Audit Logs")
    
    logs = all_data['cryptex']['logs']
    
    if logs:
        # Create dataframe
        df = pd.DataFrame(logs)
        df = df[['timestamp', 'event_type', 'details', 'hash']]
        df.columns = ['Timestamp', 'Event Type', 'Details', 'Hash']
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            event_filter = st.multiselect(
                "Filter by Event Type",
                df['Event Type'].unique().tolist(),
                default=df['Event Type'].unique().tolist()[:5]
            )
        
        with col2:
            search_term = st.text_input("Search Details", "")
        
        # Apply filters
        filtered_df = df[df['Event Type'].isin(event_filter)]
        if search_term:
            filtered_df = filtered_df[filtered_df['Details'].str.contains(search_term, case=False)]
        
        # Display
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Event type distribution
        st.markdown("### Event Distribution")
        event_counts = df['Event Type'].value_counts()
        fig = px.pie(
            values=event_counts.values,
            names=event_counts.index,
            title="Cryptex Events by Type"
        )
        fig.update_layout(
            paper_bgcolor='#1f1f1f',
            plot_bgcolor='#0a0a0a',
            font=dict(color='#e0e0e0')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No Cryptex logs found yet")

# ===== AGENT PERFORMANCE TAB =====
if "Agent Performance" in selected_tabs:
    st.markdown("## 🤖 Agent Performance Metrics")
    
    agents = all_data['agents']
    
    if agents:
        # Agent summary table
        agent_list = []
        for name, data in agents.items():
            agent_list.append({
                'Agent': name,
                'Latest Score': f"{data['latest_score']:.1f}",
                'Average Score': f"{data['avg_score']:.1f}",
                'Decision': data['latest_decision'],
                'Tests': len(data['scores'])
            })
        
        df_agents = pd.DataFrame(agent_list)
        st.dataframe(df_agents, use_container_width=True)
        
        # Individual agent details
        st.markdown("### Agent Details")
        selected_agent = st.selectbox("Select Agent", list(agents.keys()))
        
        if selected_agent:
            agent_data = agents[selected_agent]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Latest Score", f"{agent_data['latest_score']:.1f}/100")
            with col2:
                st.metric("Average Score", f"{agent_data['avg_score']:.1f}/100")
            with col3:
                st.metric("Status", agent_data['latest_decision'])
            
            # Score history
            if agent_data['scores']:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=agent_data['scores'],
                    mode='lines+markers',
                    name='Score',
                    line=dict(color='#22c55e', width=2),
                    marker=dict(size=8)
                ))
                fig.update_layout(
                    title=f"Score History - {selected_agent}",
                    xaxis_title="Test #",
                    yaxis_title="Score",
                    paper_bgcolor='#1f1f1f',
                    plot_bgcolor='#0a0a0a',
                    font=dict(color='#e0e0e0'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No agent performance data available yet. Agents will appear after grading.")

# ===== NETWORK TAB =====
if "Network" in selected_tabs:
    st.markdown("## 🌐 Network Configuration")
    
    net_info = all_data['network']['info']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hostname", net_info['hostname'])
    with col2:
        st.metric("Local IP", net_info['local_ip'])
    
    st.markdown("### Network Interfaces")
    if net_info['interfaces']:
        interfaces_df = pd.DataFrame(net_info['interfaces'])
        st.dataframe(interfaces_df, use_container_width=True)
    
    # Network stats
    st.markdown("### Network I/O Statistics")
    net_stats = all_data['network']['stats']
    
    if net_stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Bytes Sent", f"{net_stats['bytes_sent'] / (1024**3):.2f} GB")
        with col2:
            st.metric("Bytes Received", f"{net_stats['bytes_recv'] / (1024**3):.2f} GB")
        with col3:
            st.metric("Errors In", net_stats.get('errors_in', 0))
        with col4:
            st.metric("Errors Out", net_stats.get('errors_out', 0))

# ===== SYSTEM HEALTH TAB =====
if "System Health" in selected_tabs:
    st.markdown("## 💻 System Health")
    
    system = all_data['system']
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Memory")
        mem_used = system['memory']['used'] / (1024**3)
        mem_total = system['memory']['total'] / (1024**3)
        st.write(f"**Used:** {mem_used:.2f} GB / {mem_total:.2f} GB ({system['memory']['percent']:.1f}%)")
    
    with col2:
        st.markdown("### Disk")
        disk_used = system['disk']['used'] / (1024**3)
        disk_total = system['disk']['total'] / (1024**3)
        st.write(f"**Used:** {disk_used:.2f} GB / {disk_total:.2f} GB ({system['disk']['percent']:.1f}%)")
    
    st.markdown("### Processes")
    st.write(f"**Total Running:** {system['processes']}")

# ===== PROCESSES TAB =====
if "Processes" in selected_tabs:
    st.markdown("## 🔍 Forest Processes")
    
    processes = all_data['processes']
    
    if processes:
        procs_df = pd.DataFrame(processes)
        procs_df = procs_df[['pid', 'name', 'command', 'cpu', 'memory']]
        procs_df.columns = ['PID', 'Name', 'Command', 'CPU %', 'Memory %']
        
        st.dataframe(procs_df, use_container_width=True, height=400)
    else:
        st.info("No Forest processes currently running")

# Footer
st.markdown("---")
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Data Source:** Live Forest Systems")
st.markdown("🌲 Forest Unified Monitoring Dashboard v1.0")

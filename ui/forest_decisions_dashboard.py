#!/usr/bin/env python3
"""
Forest Decisions Dashboard
Real-time visualization of all agent decisions
Built with Streamlit
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from core.decision_middleware import get_middleware, DecisionType, DecisionStatus
from core.decision_timeline_provider import DecisionTimelineProvider

# Page configuration
st.set_page_config(page_title="Forest Decisions Dashboard", layout="wide", initial_sidebar_state="expanded")

# Initialize
middleware = get_middleware()
provider = DecisionTimelineProvider()

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)


def render_title():
    """Render dashboard title and status"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🌲 Forest Decisions Dashboard")
        st.markdown("Real-time agent decision tracking and monitoring")
    
    with col2:
        st.metric("Status", "🟢 Online", "+2 sec")
    
    with col3:
        refresh_button = st.button("🔄 Refresh", use_container_width=True)
        return refresh_button


def render_stats():
    """Render key statistics"""
    try:
        data = provider.get_dashboard_data()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Decisions",
                data['total_decisions'],
                delta="+5 this session"
            )
        
        with col2:
            st.metric(
                "Approvals",
                data['enforcer']['approved_count'],
                delta=f"{data['enforcer']['approval_rate']:.1%}"
            )
        
        with col3:
            st.metric(
                "Blocks",
                data['enforcer']['blocked_count'],
                delta=f"{1 - data['enforcer']['approval_rate']:.1%}"
            )
        
        with col4:
            st.metric(
                "Agents Graded",
                data['brain']['total_grades'],
                delta=f"{data['brain']['promotion_rate']:.1%} promoted"
            )
        
        with col5:
            st.metric(
                "Decision Types",
                len(data['by_type']),
                delta=f"{max(data['by_type'].values()) if data['by_type'] else 0} most common"
            )
    except Exception as e:
        st.error(f"Error rendering statistics: {str(e)}")


def render_timeline():
    """Render decision timeline"""
    st.subheader("📋 Decision Timeline")
    
    try:
        timeline = provider.get_timeline(limit=100)
        
        if timeline:
            df = pd.DataFrame(timeline)
            
            # Color code by status
            color_map = {
                'PENDING': '🟡',
                'APPROVED': '🟢',
                'BLOCKED': '🔴',
                'EXECUTED': '✅',
                'FAILED': '❌',
                'REVERSED': '↩️'
            }
            
            df['icon'] = df['status'].map(color_map)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
            
            # Display
            st.dataframe(
                df[['icon', 'timestamp', 'type', 'agent_id', 'action', 'status']].tail(20),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No decisions recorded yet")
    except Exception as e:
        st.error(f"Error rendering timeline: {str(e)}")


def render_enforcer_panel():
    """Render Enforcer gate statistics"""
    st.subheader("🔒 Enforcer Gate Status")
    
    try:
        col1, col2 = st.columns(2)
        
        enforcer_data = provider.get_enforcer_actions()
        
        with col1:
            # Approval gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=enforcer_data['approval_rate'] * 100,
                title={'text': "Approval Rate"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Decision breakdown pie
            sizes = [enforcer_data['approved_count'], enforcer_data['blocked_count']]
            labels = ['Approved', 'Blocked']
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.4)])
            fig.update_layout(height=250, title="Approve vs Block")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent blocks
        st.markdown("### Recent Blocks")
        if enforcer_data['recent_blocks']:
            for block in enforcer_data['recent_blocks']:
                st.warning(f"**{block['agent_id']}**: {block['action']} @ {block['timestamp']}")
        else:
            st.success("✅ No blocks in recent decisions")
    except Exception as e:
        st.error(f"Error rendering enforcer panel: {str(e)}")


def render_brain_panel():
    """Render Forest Brain grading statistics"""
    st.subheader("🧠 Forest Brain - Agent Grading")
    
    try:
        brain_data = provider.get_brain_grading_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Grades", brain_data['total_grades'])
        
        with col2:
            st.metric("Promotions", brain_data['promotions'], delta=f"{brain_data['promotion_rate']:.1%}")
        
        with col3:
            st.metric("Study", brain_data['study'])
        
        with col4:
            st.metric("Recycled", brain_data['recycled'])
        
        # Grading distribution
        col1, col2 = st.columns(2)
        
        with col1:
            grades_breakdown = {
                'Promoted': brain_data['promotions'],
                'Study': brain_data['study'],
                'Recycled': brain_data['recycled']
            }
            
            # Create bar chart safely
            df_grades = pd.DataFrame({
                'Action': list(grades_breakdown.keys()),
                'Count': list(grades_breakdown.values())
            })
            
            fig = px.bar(
                df_grades,
                x='Action',
                y='Count',
                title="Agent Decisions",
                color='Count',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Recent grades
            st.markdown("### Recent Grades")
            if brain_data['recent_grades']:
                for grade in brain_data['recent_grades']:
                    st.info(f"**{grade['agent_id']}**: {grade['reasoning'][:60]}")
            else:
                st.info("No grades recorded yet")
    except Exception as e:
        st.error(f"Error rendering brain panel: {str(e)}")


def render_decision_flow():
    """Render decision flow sankey diagram"""
    st.subheader("🔀 Decision Flow")
    
    try:
        flows = provider.get_decision_flow()
        
        if flows and len(flows) > 0:
            # Extract unique nodes
            sources = list(set([f['source'] for f in flows]))
            targets = list(set([f['target'] for f in flows]))
            nodes = list(set(sources + targets))
            
            if nodes and len(nodes) > 0:
                # Map to indices
                node_map = {node: i for i, node in enumerate(nodes)}
                
                source_indices = [node_map[f['source']] for f in flows]
                target_indices = [node_map[f['target']] for f in flows]
                values = [f['value'] for f in flows]
                
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color='black', width=0.5),
                        label=nodes,
                        color="#1f77b4"
                    ),
                    link=dict(
                        source=source_indices,
                        target=target_indices,
                        value=values
                    )
                )])
                
                fig.update_layout(title="Decision Routing Flow", height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No flow nodes available")
        else:
            st.info("No decision flow data available")
    except Exception as e:
        st.error(f"Error rendering decision flow: {str(e)}")


def render_decision_types_chart():
    """Render decision types distribution"""
    st.subheader("📊 Decision Types Distribution")
    
    try:
        data = provider.get_dashboard_data()
        
        if data['by_type'] and len(data['by_type']) > 0:
            df = pd.DataFrame({
                'Type': list(data['by_type'].keys()),
                'Count': list(data['by_type'].values())
            })
            
            fig = px.bar(
                df,
                x='Type',
                y='Count',
                title="Decisions by Type",
                color='Count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No decision type data available")
    except Exception as e:
        st.error(f"Error rendering decision types: {str(e)}")


def render_agent_selector():
    """Render agent selector and detail view"""
    st.subheader("🤖 Agent Decision Details")
    
    try:
        # Get all unique agents
        all_decisions = middleware.get_recent_decisions(limit=500)
        agents = sorted(list(set([d.agent_id for d in all_decisions])))
        
        if agents and len(agents) > 0:
            selected_agent = st.selectbox("Select Agent", agents)
            
            if selected_agent:
                agent_history = provider.get_agent_decision_history(selected_agent)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Decisions", agent_history['total_decisions'])
                
                with col2:
                    decision_types = agent_history['by_type']
                    most_common = max(decision_types.items(), key=lambda x: x[1]) if decision_types else ("N/A", 0)
                    st.metric("Most Common", most_common[0], most_common[1])
                
                with col3:
                    statuses = agent_history['by_status']
                    executed = statuses.get('EXECUTED', 0)
                    st.metric("Executed", executed)
                
                # Timeline for this agent
                if agent_history['timeline'] and len(agent_history['timeline']) > 0:
                    df = pd.DataFrame(agent_history['timeline'])
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
                    
                    st.dataframe(df[['timestamp', 'type', 'status', 'action']], use_container_width=True, hide_index=True)
                else:
                    st.info("No timeline data for this agent")
        else:
            st.info("No agents with decisions yet")
    except Exception as e:
        st.error(f"Error loading agents: {str(e)}")


def main():
    """Main dashboard layout"""
    
    # Title and refresh
    if render_title():
        st.rerun()
    
    st.divider()
    
    # Key statistics
    render_stats()
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Timeline",
        "Enforcer",
        "Brain",
        "Flow",
        "Agents"
    ])
    
    with tab1:
        render_timeline()
    
    with tab2:
        render_enforcer_panel()
    
    with tab3:
        render_brain_panel()
    
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            render_decision_flow()
        with col2:
            render_decision_types_chart()
    
    with tab5:
        render_agent_selector()
    
    st.divider()
    
    # Footer
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    with col2:
        try:
            data = provider.get_dashboard_data()
            st.caption(f"Total decisions: {data['total_decisions']}")
        except:
            st.caption("Total decisions: N/A")
    
    with col3:
        st.caption("🌲 Forest — Blue-Team AI Orchestration")


if __name__ == "__main__":
    st.set_option('client.showErrorDetails', False)
    main()

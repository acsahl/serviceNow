"""
Streamlit Dashboard for ServiceNow Technical Accelerators Request Analysis Agent
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="ServiceNow Technical Accelerators Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_analysis():
    """Trigger analysis via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/analyze", 
                               json={
                                   "companies_file": "companies.csv",
                                   "requests_file": "requests.csv", 
                                   "catalog_file": "catalog.csv"
                               })
        return response.status_code == 200
    except:
        return False

def get_analysis_status():
    """Get analysis status from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        return response.json()
    except:
        return {"status": "error", "message": "API not available"}

def get_insights():
    """Get insights from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/insights")
        return response.json()
    except:
        return None

def get_recommendations():
    """Get recommendations from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/recommendations")
        return response.json()
    except:
        return None

def get_emerging_needs():
    """Get emerging needs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/emerging-needs")
        return response.json()
    except:
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 ServiceNow Technical Accelerators Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", [
        "Dashboard Overview",
        "Request Patterns", 
        "Emerging Needs",
        "Accelerator Recommendations",
        "Technology Trends",
        "Industry Analysis"
    ])
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API is not running. Please start the API server first.")
        st.code("python api/main.py", language="bash")
        return
    
    # Main content based on selected page
    if page == "Dashboard Overview":
        show_dashboard_overview()
    elif page == "Request Patterns":
        show_request_patterns()
    elif page == "Emerging Needs":
        show_emerging_needs()
    elif page == "Accelerator Recommendations":
        show_recommendations()
    elif page == "Technology Trends":
        show_technology_trends()
    elif page == "Industry Analysis":
        show_industry_analysis()

def show_dashboard_overview():
    """Show dashboard overview"""
    st.header("📊 Dashboard Overview")
    
    # Analysis status
    status = get_analysis_status()
    
    if status["status"] == "not_started":
        st.warning("No analysis has been run yet.")
        if st.button("🚀 Run Analysis", type="primary"):
            with st.spinner("Running analysis..."):
                if run_analysis():
                    st.success("Analysis started! Please wait for completion.")
                    st.rerun()
                else:
                    st.error("Failed to start analysis.")
        return
    
    elif status["status"] == "error":
        st.error(f"Analysis failed: {status['message']}")
        return
    
    # Get insights
    insights = get_insights()
    if not insights:
        st.error("Failed to load insights")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Requests",
            value=insights["summary"]["total_requests"],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Unique Companies",
            value=insights["summary"]["unique_companies"],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Analysis Status",
            value="✅ Completed",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Last Updated",
            value=insights["summary"]["analysis_timestamp"][:10],
            delta=None
        )
    
    # Quick insights
    st.subheader("📈 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution
        priority_data = insights["distributions"]["priority"]
        fig_priority = px.pie(
            values=list(priority_data.values()),
            names=list(priority_data.keys()),
            title="Request Priority Distribution"
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        # Urgency distribution
        urgency_data = insights["distributions"]["urgency"]
        fig_urgency = px.pie(
            values=list(urgency_data.values()),
            names=list(urgency_data.keys()),
            title="Request Urgency Distribution"
        )
        st.plotly_chart(fig_urgency, use_container_width=True)
    
    # Top technologies
    st.subheader("🔧 Top Technology Trends")
    tech_data = insights["trends"]["technology"]
    if tech_data:
        tech_df = pd.DataFrame(list(tech_data.items()), columns=['Technology', 'Count'])
        tech_df = tech_df.head(10)
        
        fig_tech = px.bar(
            tech_df,
            x='Count',
            y='Technology',
            orientation='h',
            title="Top 10 Technologies in Requests"
        )
        st.plotly_chart(fig_tech, use_container_width=True)

def show_request_patterns():
    """Show request patterns analysis"""
    st.header("🔍 Request Patterns Analysis")
    
    # This would show detailed pattern analysis
    st.info("Request patterns analysis would be displayed here")
    
    # Placeholder for pattern visualizations
    st.subheader("Pattern Clusters")
    st.write("This section would show request clustering and topic modeling results")

def show_emerging_needs():
    """Show emerging needs analysis"""
    st.header("🌟 Emerging Needs & Gaps")
    
    emerging_needs = get_emerging_needs()
    if not emerging_needs:
        st.error("Failed to load emerging needs")
        return
    
    st.metric(
        label="Total Emerging Needs Identified",
        value=emerging_needs["total_emerging_needs"],
        delta=None
    )
    
    # Display emerging needs
    for i, need in enumerate(emerging_needs["emerging_needs"], 1):
        with st.expander(f"Emerging Need #{i}: {need['category']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request Count:** {need['request_count']}")
                st.write(f"**Priority Score:** {need['priority_score']:.1f}")
                st.write(f"**Budget Range:** {need['avg_budget']}")
            
            with col2:
                st.write("**Top Industries:**")
                for industry, count in list(need['industries'].items())[:3]:
                    st.write(f"- {industry}: {count}")
                
                st.write("**Key Technologies:**")
                for tech, count in list(need['technologies'].items())[:3]:
                    st.write(f"- {tech}: {count}")

def show_recommendations():
    """Show accelerator recommendations"""
    st.header("💡 Accelerator Recommendations")
    
    recommendations = get_recommendations()
    if not recommendations:
        st.error("Failed to load recommendations")
        return
    
    st.metric(
        label="Total Recommendations",
        value=recommendations["total_recommendations"],
        delta=None
    )
    
    # Display top recommendations
    for i, rec in enumerate(recommendations["recommendations"], 1):
        st.markdown(f"""
        <div class="recommendation-card">
            <h3>#{i} {rec['accelerator_name']}</h3>
            <p><strong>Category:</strong> {rec['category']}</p>
            <p><strong>Priority Score:</strong> {rec['priority_score']:.1f}</p>
            <p><strong>Market Size:</strong> ${rec['estimated_market_size']:,}</p>
            <p><strong>Success Probability:</strong> {rec['success_probability']:.1%}</p>
            <p><strong>Duration:</strong> {rec['duration_weeks']} weeks</p>
            <p><strong>Complexity:</strong> {rec['complexity']}</p>
            <p><strong>Description:</strong> {rec['description']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_technology_trends():
    """Show technology trends analysis"""
    st.header("🔧 Technology Trends Analysis")
    
    insights = get_insights()
    if not insights:
        st.error("Failed to load insights")
        return
    
    # Technology trends chart
    tech_data = insights["trends"]["technology"]
    if tech_data:
        tech_df = pd.DataFrame(list(tech_data.items()), columns=['Technology', 'Count'])
        tech_df = tech_df.head(15)
        
        fig = px.bar(
            tech_df,
            x='Count',
            y='Technology',
            orientation='h',
            title="Technology Usage in Requests",
            color='Count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Technology word cloud would go here
    st.subheader("Technology Word Cloud")
    st.info("Technology word cloud visualization would be displayed here")

def show_industry_analysis():
    """Show industry analysis"""
    st.header("🏢 Industry Analysis")
    
    insights = get_insights()
    if not insights:
        st.error("Failed to load insights")
        return
    
    # Industry distribution
    industry_data = insights["distributions"]["industry"]
    if industry_data:
        industry_df = pd.DataFrame(list(industry_data.items()), columns=['Industry', 'Count'])
        
        fig = px.pie(
            industry_df,
            values='Count',
            names='Industry',
            title="Request Distribution by Industry"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Industry bar chart
        fig_bar = px.bar(
            industry_df,
            x='Industry',
            y='Count',
            title="Request Count by Industry"
        )
        fig_bar.update_xaxis(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    main()

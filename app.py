"""
FDE Staffing Intelligence Platform
Main Streamlit Application

Entry point for the AI-assisted staffing recommendation and allocation system.
This application provides workforce analytics, AI-assisted recommendations,
and allocation tracking for Forward Deployed Engineer teams.

The platform combines employee profiling, skills tracking, and structured
analytical frameworks to deliver human-centered staffing decisions.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FDE Staffing Intelligence",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "FDE Staffing Intelligence Platform v1.0"
    }
)

# ============================================================================
# THEME AND STYLING
# ============================================================================

# Custom CSS for professional SaaS appearance
st.markdown("""
<style>
    :root {
        --accent: #2653ff;
        --accent-soft: #e8f0ff;
        --bg: #f4f7fb;
        --surface: rgba(255, 255, 255, 0.96);
        --surface-strong: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
    }

    body {
        background: linear-gradient(180deg, #f4f7fb 0%, #e9eef7 100%);
        color: var(--text);
    }

    .stApp {
        background: transparent;
    }

    .css-1outpf7 {
        padding-top: 1rem;
    }

    .main .block-container {
        padding: 2rem 2rem 3rem;
        border-radius: 28px;
        box-shadow: 0 30px 80px rgba(15, 23, 42, 0.08);
        background: var(--surface);
        border: 1px solid rgba(71, 85, 105, 0.08);
    }

    .stSidebar .css-1lcbmhc {
        background: #ffffff;
    }

    .stSidebar {
        border-right: 1px solid rgba(15, 23, 42, 0.08);
        padding-top: 1rem;
    }

    h1, h2, h3, h4 {
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    h1 {
        font-size: 2.4rem;
        letter-spacing: -0.04em;
    }

    h2 {
        color: #1f2a49;
        margin-top: 2rem;
        margin-bottom: 0.75rem;
    }

    .hero-card,
    .feature-card,
    .section-card,
    .insight-card {
        border-radius: 24px;
        background: var(--surface-strong);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 24px 55px rgba(15, 23, 42, 0.08);
        padding: 1.75rem;
        margin-bottom: 1.5rem;
    }

    .hero-card {
        background: linear-gradient(135deg, #2d4ff4 0%, #1b60d2 100%);
        color: white;
        border: none;
        box-shadow: 0 30px 80px rgba(25, 49, 133, 0.18);
    }

    .hero-card h1,
    .hero-card h2,
    .hero-card p,
    .hero-card li {
        color: #f8fbff;
    }

    .hero-card p,
    .hero-card li {
        color: rgba(248, 251, 255, 0.85);
    }

    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(255,255,255,0.14);
        color: #ebf2ff;
        padding: 0.55rem 0.95rem;
        border-radius: 999px;
        font-size: 0.92rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .feature-card h3 {
        margin-top: 0;
        margin-bottom: 0.75rem;
        color: #102a4f;
    }

    .feature-card p {
        color: #475569;
    }

    .button-primary .stButton > button,
    .stButton > button {
        background: linear-gradient(135deg, #2653ff, #1b60d2);
        color: white;
        border-radius: 999px;
        padding: 0.85rem 1.8rem;
        font-weight: 700;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 14px 30px rgba(38, 83, 255, 0.22);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 18px 40px rgba(38, 83, 255, 0.32);
    }

    .metric-row {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .metric-box {
        background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        border-radius: 22px;
        padding: 1.5rem;
        flex: 1 1 220px;
        min-width: 220px;
        border: 1px solid rgba(15, 23, 42, 0.08);
    }

    .metric-box h3 {
        margin: 0 0 0.75rem;
        font-size: 1rem;
        color: #64748b;
    }

    .metric-box strong {
        display: block;
        font-size: 2rem;
        color: #102a4f;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
    }

    .badge-pill {
        display: inline-block;
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .stMarkdown ul {
        margin-top: 0.4rem;
    }

    .stMarkdown li {
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING AND CACHING
# ============================================================================

@st.cache_data
def load_data():
    """
    Load all CSV data files from data/ directory.
    
    This function is cached to avoid reloading data on every page refresh.
    Returns a dictionary of all loaded DataFrames.
    """
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(app_dir, 'data')
        
        # Load all CSV files from the package data folder
        employees = pd.read_csv(os.path.join(data_dir, 'employees.csv'))
        skills = pd.read_csv(os.path.join(data_dir, 'employee_skills.csv'))
        certifications = pd.read_csv(
            os.path.join(data_dir, 'certifications.csv')
        )
        project_history = pd.read_csv(
            os.path.join(data_dir, 'project_history.csv')
        )
        availability = pd.read_csv(os.path.join(data_dir, 'availability.csv'))
        opportunities = pd.read_csv(
            os.path.join(data_dir, 'opportunities.csv')
        )
        self_assessment = pd.read_csv(
            os.path.join(data_dir, 'self_assessment.csv')
        )
        
        # Ensure date columns are datetime
        employees['join_date'] = pd.to_datetime(employees['join_date'])
        certifications['issue_date'] = pd.to_datetime(
            certifications['issue_date']
        )
        certifications['expiry_date'] = pd.to_datetime(
            certifications['expiry_date']
        )
        project_history['start_date'] = pd.to_datetime(
            project_history['start_date']
        )
        project_history['end_date'] = pd.to_datetime(
            project_history['end_date']
        )
        availability['last_updated'] = pd.to_datetime(
            availability['last_updated']
        )
        availability['next_available_date'] = pd.to_datetime(
            availability['next_available_date']
        )
        opportunities['start_date'] = pd.to_datetime(
            opportunities['start_date']
        )
        self_assessment['last_assessment_date'] = pd.to_datetime(
            self_assessment['last_assessment_date']
        )
        
        return {
            'employees': employees,
            'skills': skills,
            'certifications': certifications,
            'projects': project_history,
            'availability': availability,
            'opportunities': opportunities,
            'assessments': self_assessment
        }
        
    except FileNotFoundError as e:
        st.error(
            f"❌ Data files not found: {e}\n\n"
            "Please run: python scripts/generate_sample_data.py"
        )
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

# Initialize session state for cross-page state management
if 'selected_opportunity' not in st.session_state:
    st.session_state.selected_opportunity = None

if 'allocations' not in st.session_state:
    st.session_state.allocations = []

if 'page' not in st.session_state:
    st.session_state.page = "🏠 Home"

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application logic and navigation."""
    
    # Load data
    data = load_data()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 👥 FDE Staffing Intelligence Platform")
        st.markdown(
            "**AI-Assisted Workforce Optimization & Allocation System**"
        )
    with col2:
        st.markdown("### v1.0")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.markdown("## 📊 Navigation")
    
    page = st.sidebar.radio(
        "Select Page",
        options=[
            "🏠 Home",
            "📈 Dashboard",
            "🤖 Recommendations",
            "📋 Allocations",
            "🎯 Allocation Optimizer",
            "📊 Staffing Analytics"
        ],
        key="page"
    )
    
    st.sidebar.markdown("---")
    
    # Sidebar info
    st.sidebar.markdown("### 📌 Quick Stats")
    st.sidebar.metric("Total Workforce", len(data['employees']))
    st.sidebar.metric(
        "Opportunities Open",
        len(data['opportunities'][data['opportunities']['status'] == 'Open'])
    )
    st.sidebar.metric(
        "Skills Tracked",
        data['skills']['skill_name'].nunique()
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "### 📖 Documentation\n"
        "- [README](./README.txt)\n"
        "- [Architecture](./architecture_explainer.txt)\n"
        "- [Implementation](./implementation_notes.txt)"
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home(data)
    elif page == "📈 Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard(data)
    elif page == "🤖 Recommendations":
        from pages.recommendations import show_recommendations
        show_recommendations(data)
    elif page == "📋 Allocations":
        from pages.allocation import show_allocation
        show_allocation(data)
    elif page == "🎯 Allocation Optimizer":
        from pages.allocation_optimizer import show_allocation_optimizer
        show_allocation_optimizer(data)
    elif page == "📊 Staffing Analytics":
        from pages.staffing_analytics import show_staffing_analytics
        show_staffing_analytics(data)

def show_home(data: dict):
    """Home/welcome page."""
    
    st.markdown("""
    <div class="hero-card">
        <div class="hero-pill">Enterprise staffing intelligence</div>
        <h1>FDE Staffing Intelligence</h1>
        <p>Power your staffing decisions with modern workforce analytics, AI-backed recommendations, and professional resource allocation tools.</p>
        <div class="metric-row">
            <div class="metric-box">
                <h3>Total Workforce</h3>
                <strong>{total_emp}</strong>
            </div>
            <div class="metric-box">
                <h3>Open Opportunities</h3>
                <strong>{open_ops}</strong>
            </div>
            <div class="metric-box">
                <h3>Sectors Covered</h3>
                <strong>{sectors}</strong>
            </div>
        </div>
    </div>
    """.format(
        total_emp=len(data['employees']),
        open_ops=len(data['opportunities'][data['opportunities']['status'] == 'Open']),
        sectors=data['employees']['primary_sector'].nunique()
    ), unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="section-card">
        <h2>Elevate resource planning and capacity forecasting</h2>
        <p>FDE Staffing Intelligence centralizes employee skills, certifications, availability, and project demand into one polished SaaS experience.</p>
        <div class="feature-grid">
            <div class="feature-card">
                <span class="badge-pill">Analytics</span>
                <h3>Workforce health at a glance</h3>
                <p>Monitor bench capacity, skill coverage, and project alignment with data-driven dashboards.</p>
            </div>
            <div class="feature-card">
                <span class="badge-pill">AI</span>
                <h3>Smart candidate matching</h3>
                <p>Match talent to opportunities using contextual scoring, and review readiness in one click.</p>
            </div>
            <div class="feature-card">
                <span class="badge-pill">Planning</span>
                <h3>Allocation confidence</h3>
                <p>Track current assignments, forecast availability, and optimize utilization across teams.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Product tour")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📈 Dashboard**")
        st.write("Discover trends in workforce makeup, certifications, and opportunity readiness.")

    with col2:
        st.markdown("**🤖 Recommendations**")
        st.write("See AI-backed matches and supporting rationale for every staffing decision.")

    with col3:
        st.markdown("**📋 Allocations**")
        st.write("Review allocation state, bench risk, and upcoming commitment timelines.")

    st.markdown("---")

    with st.expander("Why this platform?"):
        st.markdown("""
        - **Executive-ready insights** with clean, modern dashboards
        - **Meaningful staffing signals** from skills, availability, and history
        - **Actionable recommendations** with transparency and trust
        - **Future-proof workflow** designed for high-performing teams
        """)

    with st.expander("Data footprint"):
        st.markdown(f"""
        **Datasets loaded:**
        - Employees: {len(data['employees'])} records
        - Skills: {len(data['skills'])} skill assignments
        - Certifications: {len(data['certifications'])} records
        - Project History: {len(data['projects'])} records
        - Opportunities: {len(data['opportunities'])} positions
        - Assessments: {len(data['assessments'])} records
        """)

if __name__ == "__main__":
    main()

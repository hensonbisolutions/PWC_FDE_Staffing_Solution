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

# Custom CSS for professional appearance
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Success/warning boxes */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 0.3rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1557a0;
        transform: scale(1.02);
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
        data_dir = 'data'
        
        # Load all CSV files
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
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🎯 Welcome to FDE Staffing Intelligence")
        
        st.markdown("""
        This platform provides enterprise-grade staffing optimization and
        human-centered decision support for Forward Deployed Engineer teams.
        
        ### What Can You Do?
        
        **📊 Dashboard**
        - View workforce composition and analytics
        - Track skill inventory and gaps
        - Monitor certification compliance
        - Analyze sector coverage and experience
        
        **🤖 AI-Assisted Recommendations**
        - Match employees to staffing opportunities
        - Get explainable scoring for every recommendation
        - Review strengths, considerations, and risks
        - One-click allocation to deploy talent
        
        **📋 Allocation Tracking**
        - Monitor current project assignments
        - Track bench capacity and availability
        - Forecast utilization trends
        - Plan for upcoming staffing needs
        """)
    
    with col2:
        st.markdown("### 📊 Workforce Overview")
        
        total_emp = len(data['employees'])
        allocated = len(data['opportunities'][
            data['opportunities']['status'] == 'Filled'
        ])
        
        st.metric("Total Employees", total_emp)
        st.metric("Open Opportunities", len(data['opportunities'][
            data['opportunities']['status'] == 'Open'
        ]))
        st.metric("Avg Seniority", 
                 data['employees']['seniority_level'].value_counts().index[0])
        
        # Sectors
        st.markdown("**Sectors Covered**")
        sectors = data['employees']['primary_sector'].nunique()
        st.caption(f"{sectors} industries represented")
    
    st.markdown("---")
    
    # Quick start
    st.markdown("### 🚀 Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**1. Explore Dashboard**")
        st.write("Get insights into workforce composition and skills")

    with col2:
        st.markdown("**2. View Recommendations**")
        st.write("Find best-matched candidates for open opportunities")

    with col3:
        st.markdown("**3. Track Allocations**")
        st.write("Monitor current assignments and capacity")
    
    with st.expander("Architecture & Design"):
        st.markdown("""
        **Design Philosophy:**
        - Explainability first: All recommendations are transparent
        - Human oversight: System recommends, humans decide
        - Data-driven: Decisions based on structured data
        - Scalable: Supports 1000s of employees
        
        **Key Features:**
        - Multi-dimensional scoring (7 dimensions)
        - Audit trails for compliance
        - No black-box algorithms
        - Enterprise-ready code structure
        """)
    
    with st.expander("Data Overview"):
        st.markdown(f"""
        **Datasets Loaded:**
        - Employees: {len(data['employees'])} records
        - Skills: {len(data['skills'])} skill assignments
        - Certifications: {len(data['certifications'])} records
        - Project History: {len(data['projects'])} project records
        - Opportunities: {len(data['opportunities'])} open positions
        - Assessments: {len(data['assessments'])} career development records
        """)

if __name__ == "__main__":
    main()

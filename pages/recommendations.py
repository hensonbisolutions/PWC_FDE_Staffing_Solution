"""
Recommendations Page - AI-Assisted Staffing Matching

Provides the core staffing recommendation workflow:
1. Select an opportunity
2. View ranked candidate matches
3. Review detailed scoring and explanations
4. Allocate selected candidate

All recommendations are fully transparent with detailed scoring breakdowns,
rationale explanations, and risk flagging for informed human decision-making.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.matching_engine import MatchingEngine


def show_recommendations(data: dict):
    """Main recommendations page."""
    
    st.markdown("""
    <div class="hero-card">
        <div class="hero-pill">AI-powered staffing</div>
        <h1>AI-Assisted Staffing Recommendations</h1>
        <p>Match the right talent to the right opportunity with transparent scoring, candidate context, and operational readiness.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize matching engine
    engine = MatchingEngine(
        employees_df=data['employees'],
        skills_df=data['skills'],
        certifications_df=data['certifications'],
        project_history_df=data['projects'],
        availability_df=data['availability'],
        opportunities_df=data['opportunities'],
        self_assessment_df=data['assessments']
    )
    
    # Step 1: Opportunity Selection
    st.markdown("## Step 1: Select Opportunity")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get open opportunities
        open_opps = data['opportunities'][
            data['opportunities']['status'] == 'Open'
        ]
        
        if open_opps.empty:
            st.warning("No open opportunities at this time")
            return
        
        opp_options = [
            f"{row['opportunity_id']}: {row['opportunity_name']}"
            for _, row in open_opps.iterrows()
        ]
        
        selected_opp_label = st.selectbox(
            "Select an opportunity to fill",
            options=opp_options,
            label_visibility="collapsed"
        )
        
        # Extract opportunity ID
        opp_id = int(selected_opp_label.split(':')[0])
        selected_opp = open_opps[
            open_opps['opportunity_id'] == opp_id
        ].iloc[0]
    
    with col2:
        if st.button("🔍 Find Candidates", use_container_width=True):
            st.session_state.search_triggered = True
    
    # Display opportunity details
    st.markdown("### Opportunity Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Sector:** {selected_opp['client_sector']}")
        st.markdown(f"**Location:** {selected_opp['location']}")
    
    with col2:
        st.markdown(f"**Required Seniority:** {selected_opp['required_seniority']}")
        st.markdown(f"**Duration:** {selected_opp['allocation_weeks']} weeks")
    
    with col3:
        st.markdown(f"**Start Date:** {selected_opp['start_date'].strftime('%Y-%m-%d')}")
        st.markdown(f"**Priority:** {selected_opp['priority']}")
    
    st.markdown("**Required Skills:**")
    st.caption(selected_opp['required_skills'])
    
    st.markdown("**Description:**")
    st.caption(selected_opp['description'])
    
    st.markdown("---")
    
    # Step 2: Generate Recommendations
    if st.session_state.get('search_triggered', False):
        st.markdown("## Step 2: Candidate Rankings")
        
        # Generate recommendations
        with st.spinner("🔄 Analyzing candidates..."):
            recommendations = engine.rank_candidates(
                opportunity_id=opp_id,
                top_n=10
            )
        
        if not recommendations:
            st.error("No candidates found for this opportunity")
            return
        
        # Display recommendation summary
        st.markdown(f"### Ranked Candidates ({len(recommendations)} total)")
        
        # Create summary table
        summary_data = []
        for i, rec in enumerate(recommendations[:10], 1):
            summary_data.append({
                '#': i,
                'Candidate': rec['name'],
                'Score': f"{rec['overall_score']:.0f}",
                'Seniority': rec['seniority'],
                'Sector': rec['sector'],
                'Skills': f"{rec['scoring_breakdown']['skill_match']:.0f}%",
                'Availability': f"{rec['scoring_breakdown']['availability']:.0f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Step 3: Detailed Review
        st.markdown("## Step 3: Detailed Candidate Review")
        
        # Select candidate to review
        candidate_options = [
            f"{i}: {rec['name']} (Score: {rec['overall_score']:.0f})"
            for i, rec in enumerate(recommendations[:10], 1)
        ]
        
        selected_candidate_label = st.selectbox(
            "Select a candidate to review details",
            options=candidate_options,
            label_visibility="collapsed"
        )
        
        # Extract selected candidate index
        candidate_idx = int(selected_candidate_label.split(':')[0]) - 1
        selected_rec = recommendations[candidate_idx]
        
        # Display detailed profile
        st.markdown(
            f"### 👤 {selected_rec['name']} - "
            f"Employee #{selected_rec['employee_id']}"
        )
        
        # Overall score display (large and prominent)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Create gauge chart for overall score
            overall_score = selected_rec['overall_score']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Match Score"},
                delta={'reference': 75},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 50], 'color': "#FFB6C6"},
                        {'range': [50, 75], 'color': "#FFE4B5"},
                        {'range': [75, 100], 'color': "#90EE90"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 60
                    }
                }
            ))
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Scoring breakdown
        st.markdown("### 📊 Scoring Breakdown")
        
        breakdown = selected_rec['scoring_breakdown']
        
        # Create detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Technical Dimensions:**")
            
            # Skill match
            st.markdown(f"**Skill Match:** {breakdown['skill_match']:.0f}/100")
            st.progress(breakdown['skill_match'] / 100)
            
            # Seniority
            st.markdown(f"**Seniority Alignment:** {breakdown['seniority_alignment']:.0f}/100")
            st.progress(breakdown['seniority_alignment'] / 100)
            
            # Sector
            st.markdown(f"**Sector Experience:** {breakdown['sector_experience']:.0f}/100")
            st.progress(breakdown['sector_experience'] / 100)
        
        with col2:
            st.markdown("**Operational Dimensions:**")
            
            # Availability
            st.markdown(f"**Availability:** {breakdown['availability']:.0f}/100")
            st.progress(breakdown['availability'] / 100)
            
            # Certifications
            st.markdown(f"**Certifications:** {breakdown['certifications']:.0f}/100")
            st.progress(breakdown['certifications'] / 100)
            
            # Location
            st.markdown(f"**Location Fit:** {breakdown['location_fit']:.0f}/100")
            st.progress(breakdown['location_fit'] / 100)
        
        # Career alignment
        st.markdown(f"**Career Alignment:** {breakdown['career_alignment']:.0f}/100")
        st.progress(breakdown['career_alignment'] / 100)
        
        st.markdown("---")
        
        # Explanation narrative
        if 'explanation' in selected_rec:
            explanation = selected_rec['explanation']
            
            st.markdown("### 📝 Recommendation Narrative")
            
            # Recommendation summary
            st.markdown(f"**{explanation['recommendation']}**")
            
            # Strengths
            if explanation['strengths']:
                st.markdown("**✅ Strengths:**")
                for strength in explanation['strengths']:
                    st.markdown(f"- {strength}")
            
            # Considerations
            if explanation['considerations']:
                st.markdown("**⚠️ Considerations:**")
                for consideration in explanation['considerations']:
                    st.markdown(f"- {consideration}")
        
        # Risk flags
        if 'risks' in selected_rec and selected_rec['risks']:
            st.markdown("### 🚩 Risk Flags")
            for risk in selected_rec['risks']:
                if risk.startswith("RED"):
                    st.error(risk)
                elif risk.startswith("YELLOW"):
                    st.warning(risk)
        
        st.markdown("---")
        
        # Step 4: Allocation
        st.markdown("## Step 4: Allocation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                f"✅ Allocate {selected_rec['name']} to this Opportunity",
                use_container_width=True,
                type="primary"
            ):
                # Perform allocation
                st.success(
                    f"✅ {selected_rec['name']} has been allocated to "
                    f"{selected_opp['opportunity_name']}"
                )
                st.balloons()
                
                st.markdown(
                    f"""
                    **Allocation Details:**
                    - Employee: {selected_rec['name']} (#{selected_rec['employee_id']})
                    - Opportunity: {selected_opp['opportunity_name']}
                    - Duration: {selected_opp['allocation_weeks']} weeks
                    - Start: {selected_opp['start_date'].strftime('%Y-%m-%d')}
                    - Score: {selected_rec['overall_score']:.0f}/100
                    
                    Next steps: Contact employee and confirm availability.
                    """
                )
        
        with col2:
            if st.button("📋 View Next Opportunity", use_container_width=True):
                st.session_state.search_triggered = False
                st.rerun()
        
        st.markdown("---")
        
        # Comparison view
        with st.expander("📊 Compare Candidates"):
            st.markdown("### Compare Top 3 Candidates")
            
            comparison_data = []
            for i, rec in enumerate(recommendations[:3]):
                comparison_data.append({
                    'Candidate': rec['name'],
                    'Overall': rec['overall_score'],
                    'Skills': rec['scoring_breakdown']['skill_match'],
                    'Seniority': rec['scoring_breakdown']['seniority_alignment'],
                    'Sector': rec['scoring_breakdown']['sector_experience'],
                    'Available': rec['scoring_breakdown']['availability']
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            fig = go.Figure(data=[
                go.Scatterpolar(
                    r=[
                        row['Skills'],
                        row['Seniority'],
                        row['Sector'],
                        row['Available'],
                        row['Overall']
                    ],
                    theta=['Skills', 'Seniority', 'Sector', 'Availability', 'Overall'],
                    fill='toself',
                    name=row['Candidate']
                )
                for _, row in comparison_df.iterrows()
            ])
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export recommendations
        with st.expander("📥 Export Recommendations"):
            
            if st.button("Export All Recommendations (CSV)"):
                export_data = pd.DataFrame([
                    {
                        'Rank': i+1,
                        'Name': rec['name'],
                        'Employee_ID': rec['employee_id'],
                        'Overall_Score': rec['overall_score'],
                        'Skill_Match': rec['scoring_breakdown']['skill_match'],
                        'Seniority_Alignment': rec['scoring_breakdown']['seniority_alignment'],
                        'Sector_Experience': rec['scoring_breakdown']['sector_experience'],
                        'Availability': rec['scoring_breakdown']['availability'],
                        'Certifications': rec['scoring_breakdown']['certifications'],
                        'Location_Fit': rec['scoring_breakdown']['location_fit']
                    }
                    for i, rec in enumerate(recommendations)
                ])
                
                csv = export_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"recommendations_{opp_id}.csv",
                    mime="text/csv"
                )

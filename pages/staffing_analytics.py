"""
Staffing Analytics - Performance Metrics & KPI Dashboard

Tracks operational performance metrics including:
- Time-to-staff: Speed of filling opportunities
- Utilization rates: Deployment efficiency
- Match quality: Recommendation accuracy
- Client satisfaction: Deployment success

Provides data-driven insights for continuous improvement.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random


def show_staffing_analytics(data: dict):
    """Main staffing analytics display."""
    
    st.markdown("# 📊 Staffing Analytics - Performance Metrics")
    st.markdown("Operational KPIs and performance tracking")
    st.markdown("---")
    
    opportunities = data['opportunities']
    employees = data['employees']
    availability = data['availability']
    
    # Calculate key analytics
    filled_opps = opportunities[opportunities['status'] == 'Filled']
    
    # Time-to-staff calculation (simulated based on start date)
    today = datetime.now()
    filled_opps_with_tat = filled_opps.copy()
    filled_opps_with_tat['days_to_fill'] = (
        filled_opps_with_tat['start_date'] - today
    ).dt.days.abs()
    
    # Average metrics
    avg_tat = filled_opps_with_tat['days_to_fill'].mean() if len(filled_opps_with_tat) > 0 else 0
    avg_utilization = (100 - availability['available_percentage'].mean())
    match_quality = random.randint(75, 92)  # Simulated from scoring engine
    client_satisfaction = random.randint(78, 95)  # Simulated feedback
    
    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg Time-to-Staff", f"{avg_tat:.0f} days",
                 delta="-2 days vs last month", delta_color="inverse")
    
    with col2:
        st.metric("Team Utilization", f"{avg_utilization:.0f}%",
                 delta="+3% vs last month")
    
    with col3:
        st.metric("Match Quality", f"{match_quality}%",
                 delta="+4% vs last month")
    
    with col4:
        st.metric("Client Satisfaction", f"{client_satisfaction}%",
                 delta="+6% vs last month")
    
    st.markdown("---")
    
    # Tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs([
        "⏱️ Time-to-Staff",
        "📈 Utilization Analysis",
        "⭐ Match Quality",
        "😊 Client Satisfaction"
    ])
    
    # ========================================================================
    # TAB 1: TIME-TO-STAFF
    # ========================================================================
    with tab1:
        st.markdown("## Time-to-Staff Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Distribution of Staffing Speed")
            
            if len(filled_opps_with_tat) > 0:
                fig = px.histogram(
                    filled_opps_with_tat,
                    x='days_to_fill',
                    nbins=15,
                    labels={'days_to_fill': 'Days to Fill', 'count': 'Count'},
                    color_discrete_sequence=['#1f77b4'],
                    title="Time-to-Staff Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Monthly Trend")
            
            # Simulate historical trend
            months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
            tat_trend = [35, 32, 28, 25, 22, 18]
            
            fig = px.line(
                x=months,
                y=tat_trend,
                markers=True,
                labels={'x': 'Month', 'y': 'Avg Days'},
                title="Time-to-Staff Improvement Trend"
            )
            fig.add_hline(y=20, line_dash="dash", annotation_text="Target: 20 days")
            st.plotly_chart(fig, use_container_width=True)
        
        # Breakdown by sector
        st.markdown("### Time-to-Staff by Sector")
        
        if len(filled_opps_with_tat) > 0:
            sector_tat = filled_opps_with_tat.groupby('client_sector').agg({
                'days_to_fill': ['mean', 'count']
            }).round(1)
            sector_tat.columns = ['Avg Days', 'Fills']
            sector_tat = sector_tat.sort_values('Avg Days')
            
            fig = px.bar(
                x=sector_tat['Avg Days'],
                y=sector_tat.index,
                orientation='h',
                labels={'x': 'Avg Days to Fill', 'y': 'Sector'},
                color=sector_tat['Avg Days'],
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Best practices
        st.markdown("### Best Practices & Targets")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Avg", f"{avg_tat:.0f} days")
            st.caption("All sectors")
        
        with col2:
            st.metric("Target", "20 days")
            st.caption("Industry standard")
        
        with col3:
            improvement = ((avg_tat - 20) / avg_tat * 100) if avg_tat > 0 else 0
            st.metric("To Target", f"{max(0, avg_tat - 20):.0f} days")
            st.caption(f"Need {improvement:.0f}% improvement")
    
    # ========================================================================
    # TAB 2: UTILIZATION ANALYSIS
    # ========================================================================
    with tab2:
        st.markdown("## Utilization Rate Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Utilization Trend (12 months)")
            
            # Simulate historical utilization
            months = list(pd.date_range(start='2025-06', periods=12, freq='M'))
            month_names = [m.strftime('%b') for m in months]
            util_trend = [65, 68, 70, 72, 74, 75, 76, 78, 79, 80, 82, 85]
            
            fig = px.line(
                x=month_names,
                y=util_trend,
                markers=True,
                labels={'x': 'Month', 'y': 'Utilization %'},
                title="Utilization Rate Improvement"
            )
            fig.add_hline(y=80, line_dash="dash", annotation_text="Target: 80%")
            fig.update_yaxes(range=[60, 95])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Utilization by Seniority")
            
            seniority_util = employees.merge(availability, on='employee_id').groupby(
                'seniority_level'
            )['available_percentage'].mean()
            seniority_util = 100 - seniority_util
            
            fig = px.bar(
                x=seniority_util.values,
                y=seniority_util.index,
                orientation='h',
                labels={'x': 'Utilization %', 'y': 'Seniority'},
                color=seniority_util.values,
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Capacity metrics
        st.markdown("### Capacity Health Scorecard")
        
        cap_col1, cap_col2, cap_col3, cap_col4 = st.columns(4)
        
        emp_avail = employees.merge(availability, on='employee_id')
        
        with cap_col1:
            over_70 = len(emp_avail[100 - emp_avail['available_percentage'] > 70])
            st.metric("Over 70% Utilized", over_70, f"{over_70/len(emp_avail)*100:.0f}% of team")
        
        with cap_col2:
            over_50 = len(emp_avail[100 - emp_avail['available_percentage'] > 50])
            st.metric("Over 50% Utilized", over_50, f"{over_50/len(emp_avail)*100:.0f}% of team")
        
        with cap_col3:
            bench_20 = len(emp_avail[emp_avail['available_percentage'] >= 80])
            st.metric("Bench Available", bench_20, f"{bench_20/len(emp_avail)*100:.0f}% of team")
        
        with cap_col4:
            bench_50 = len(emp_avail[emp_avail['available_percentage'] >= 50])
            st.metric("Flexible Capacity", bench_50, f"{bench_50/len(emp_avail)*100:.0f}% of team")
    
    # ========================================================================
    # TAB 3: MATCH QUALITY
    # ========================================================================
    with tab3:
        st.markdown("## Match Quality Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Overall Match Quality Distribution")
            
            # Simulate match quality scores
            match_scores = [random.randint(60, 98) for _ in range(len(filled_opps))]
            
            fig = px.histogram(
                x=match_scores,
                nbins=10,
                labels={'x': 'Match Score', 'count': 'Count'},
                color_discrete_sequence=['#2ca02c'],
                title="Distribution of Match Scores"
            )
            fig.add_vline(x=75, line_dash="dash", annotation_text="Good: 75+")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Quality Score Components")
            
            components = {
                'Skill Alignment': 82,
                'Seniority Match': 78,
                'Sector Experience': 88,
                'Availability': 75,
                'Certification': 80
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(components.values()),
                    y=list(components.keys()),
                    orientation='h',
                    marker=dict(color=list(components.values()),
                               colorscale='Viridis'),
                    text=[f"{v}%" for v in components.values()],
                    textposition='auto'
                )
            ])
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Quality trends
        st.markdown("### Match Quality Trend")
        
        months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        quality_trend = [72, 74, 76, 78, 80, 82]
        
        fig = px.line(
            x=months,
            y=quality_trend,
            markers=True,
            labels={'x': 'Month', 'y': 'Avg Match Score'},
            title="Match Quality Improvement"
        )
        fig.add_hline(y=85, line_dash="dash", annotation_text="Excellence: 85+")
        st.plotly_chart(fig, use_container_width=True)
        
        # Success rate
        st.markdown("### Allocation Success Rate")
        
        success_col1, success_col2, success_col3 = st.columns(3)
        
        with success_col1:
            excellent = len([s for s in match_scores if s >= 85])
            st.metric("Excellent Matches", f"{excellent}/{len(match_scores)}", 
                     f"{excellent/len(match_scores)*100:.0f}%")
        
        with success_col2:
            good = len([s for s in match_scores if 75 <= s < 85])
            st.metric("Good Matches", f"{good}/{len(match_scores)}", 
                     f"{good/len(match_scores)*100:.0f}%")
        
        with success_col3:
            acceptable = len([s for s in match_scores if s < 75])
            st.metric("Acceptable", f"{acceptable}/{len(match_scores)}", 
                     f"{acceptable/len(match_scores)*100:.0f}%")
    
    # ========================================================================
    # TAB 4: CLIENT SATISFACTION
    # ========================================================================
    with tab4:
        st.markdown("## Client Satisfaction & Feedback")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Satisfaction Rating Distribution")
            
            # Simulate satisfaction scores
            satisfaction_scores = [random.randint(65, 100) for _ in range(len(filled_opps))]
            
            fig = px.histogram(
                x=satisfaction_scores,
                nbins=7,
                labels={'x': 'Satisfaction Score', 'count': 'Projects'},
                color_discrete_sequence=['#ff7f0e'],
                title="Client Satisfaction Distribution"
            )
            fig.add_vline(x=80, line_dash="dash", annotation_text="Target: 80+")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Satisfaction Trend (12 months)")
            
            months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
            sat_trend = [75, 76, 77, 78, 80, 82]
            
            fig = px.line(
                x=months,
                y=sat_trend,
                markers=True,
                labels={'x': 'Month', 'y': 'Avg Satisfaction'},
                title="Satisfaction Improvement"
            )
            fig.add_hline(y=85, line_dash="dash", annotation_text="Target: 85+")
            st.plotly_chart(fig, use_container_width=True)
        
        # Satisfaction by sector
        st.markdown("### Satisfaction by Sector")
        
        sectors = filled_opps['client_sector'].unique()
        sector_sat = {s: random.randint(75, 92) for s in sectors}
        
        fig = px.bar(
            x=list(sector_sat.values()),
            y=list(sector_sat.keys()),
            orientation='h',
            labels={'x': 'Avg Satisfaction', 'y': 'Sector'},
            color=list(sector_sat.values()),
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        st.markdown("### Key Satisfaction Drivers")
        
        drivers = {
            'Employee Technical Skills': 88,
            'Communication & Responsiveness': 85,
            'Deployment Speed': 78,
            'Cost Efficiency': 82,
            'Problem Resolution': 80
        }
        
        fig = go.Figure(data=[go.RadarTrace(
            r=list(drivers.values()),
            theta=list(drivers.keys()),
            fill='toself'
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Investment justification
        st.markdown("### Business Impact Summary")
        
        impact_col1, impact_col2, impact_col3 = st.columns(3)
        
        with impact_col1:
            st.metric("Repeat Client Rate", "84%", "+12% YoY")
        
        with impact_col2:
            st.metric("NPS Score", "72", "+8 points YoY")
        
        with impact_col3:
            st.metric("Retention (Staff)", "91%", "+5% YoY")

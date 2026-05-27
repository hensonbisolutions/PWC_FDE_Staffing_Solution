"""
Dashboard Page - Workforce Analytics

Displays comprehensive workforce analytics including:
- Workforce composition and headcount
- Skills inventory and gaps
- Sector experience and coverage
- Availability and allocation metrics
- Certification compliance tracking

This page provides strategic visibility into workforce capabilities
and capacity planning metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def show_dashboard(data: dict):
    """Main dashboard display function."""
    
    st.markdown("""
    <div class="hero-card">
        <div class="hero-pill">Enterprise workforce intelligence</div>
        <h1>Workforce Analytics Dashboard</h1>
        <p>Visualize skills, allocations, and capacity through executive-ready charts and strategic workforce insights.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_emp = len(data['employees'])
        st.metric(
            label="Total Workforce",
            value=total_emp,
            delta="40 profiles",
            delta_color="off"
        )
    
    with col2:
        avg_seniority = data['employees']['seniority_level'].mode()[0]
        st.metric(
            label="Avg Seniority",
            value=avg_seniority,
            delta="Career stage",
            delta_color="off"
        )
    
    with col3:
        available_pct = data['availability']['available_percentage'].mean()
        st.metric(
            label="Bench Capacity",
            value=f"{available_pct:.0f}%",
            delta="Available for deployment",
            delta_color="off"
        )
    
    with col4:
        sector_count = data['employees']['primary_sector'].nunique()
        st.metric(
            label="Sectors Covered",
            value=sector_count,
            delta="Industry sectors",
            delta_color="off"
        )
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔍 Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        seniority_filter = st.multiselect(
            "Seniority Level",
            options=data['employees']['seniority_level'].unique(),
            default=data['employees']['seniority_level'].unique()
        )
    
    with filter_col2:
        sector_filter = st.multiselect(
            "Sector",
            options=data['employees']['primary_sector'].unique(),
            default=data['employees']['primary_sector'].unique()[:3]
        )
    
    with filter_col3:
        location_filter = st.multiselect(
            "Location",
            options=data['employees']['location'].unique(),
            default=data['employees']['location'].unique()
        )
    
    # Apply filters
    filtered_emp = data['employees'][
        (data['employees']['seniority_level'].isin(seniority_filter)) &
        (data['employees']['primary_sector'].isin(sector_filter)) &
        (data['employees']['location'].isin(location_filter))
    ]
    
    st.markdown("---")
    
    # Section 1: Workforce Composition
    st.markdown("## 👥 Workforce Composition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Seniority Distribution")
        seniority_counts = filtered_emp['seniority_level'].value_counts()
        fig = px.pie(
            values=seniority_counts.values,
            names=seniority_counts.index,
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='label+percent')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Primary Sectors")
        sector_counts = filtered_emp['primary_sector'].value_counts().head(8)
        fig = px.bar(
            x=sector_counts.values,
            y=sector_counts.index,
            orientation='h',
            color=sector_counts.values,
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="",
            xaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Location distribution
    st.markdown("### Location Distribution")
    location_counts = filtered_emp['location'].value_counts()
    fig = px.bar(
        x=location_counts.index,
        y=location_counts.values,
        color=location_counts.values,
        color_continuous_scale="Blues",
        labels={'x': 'Location', 'y': 'Count'}
    )
    fig.update_layout(
        showlegend=False,
        height=300,
        xaxis_title="Location",
        yaxis_title="Number of Employees"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Section 2: Skills Inventory
    st.markdown("## 💼 Skills Inventory & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top Skills in Workforce")
        
        # Get skills for filtered employees
        filtered_emp_ids = filtered_emp['employee_id'].tolist()
        filtered_skills = data['skills'][
            data['skills']['employee_id'].isin(filtered_emp_ids)
        ]
        
        top_skills = filtered_skills['skill_name'].value_counts().head(10)
        fig = px.bar(
            x=top_skills.values,
            y=top_skills.index,
            orientation='h',
            color=top_skills.values,
            color_continuous_scale="Turbo"
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="",
            xaxis_title="Number of Employees"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Proficiency Distribution")
        
        proficiency_dist = filtered_skills['proficiency_level'].value_counts()
        proficiency_order = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        proficiency_dist = proficiency_dist.reindex(
            [x for x in proficiency_order if x in proficiency_dist.index]
        )
        
        fig = px.bar(
            x=proficiency_dist.index,
            y=proficiency_dist.values,
            color=proficiency_dist.index,
            color_discrete_sequence=['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4'],
            labels={'x': 'Proficiency Level', 'y': 'Count'}
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Proficiency Level",
            yaxis_title="Number of Skills"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Skill search
    st.markdown("### 🔎 Search Skill")
    skill_search = st.selectbox(
        "Select a skill to analyze",
        options=sorted(data['skills']['skill_name'].unique()),
        label_visibility="collapsed"
    )
    
    if skill_search:
        skill_data = filtered_skills[
            filtered_skills['skill_name'] == skill_search
        ]
        
        if not skill_data.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                proficiency_counts = skill_data['proficiency_level'].value_counts()
                fig = px.bar(
                    x=proficiency_counts.index,
                    y=proficiency_counts.values,
                    color=proficiency_counts.index,
                    color_discrete_sequence=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728'],
                    title=f"{skill_search} - Proficiency Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric(
                    "People with skill",
                    len(skill_data),
                    f"{len(skill_data)/len(filtered_emp)*100:.0f}% of filtered workforce"
                )
                avg_prof = skill_data['proficiency_level'].map({
                    'Beginner': 1, 'Intermediate': 2,
                    'Advanced': 3, 'Expert': 4
                }).mean()
                st.metric("Avg Proficiency", f"{avg_prof:.1f}/4.0")
    
    st.markdown("---")
    
    # Section 3: Availability & Allocation
    st.markdown("## 📊 Availability & Allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Workforce Capacity Status")
        
        capacity_data = {
            'Status': ['Fully Available', 'Partially Available', 'Allocated'],
            'Count': [
                len(data['availability'][data['availability']['available_percentage'] >= 80]),
                len(data['availability'][
                    (data['availability']['available_percentage'] >= 20) &
                    (data['availability']['available_percentage'] < 80)
                ]),
                len(data['availability'][data['availability']['available_percentage'] < 20])
            ]
        }
        
        fig = px.pie(
            values=capacity_data['Count'],
            names=capacity_data['Status'],
            color_discrete_sequence=['#2ca02c', '#ff7f0e', '#d62728'],
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='label+percent')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Allocation by Sector")
        
        # Join availability with employee sector
        emp_avail = filtered_emp.merge(
            data['availability'],
            on='employee_id',
            how='left'
        )
        
        sector_alloc = emp_avail.groupby('primary_sector').agg({
            'available_percentage': 'mean'
        }).sort_values('available_percentage')
        
        fig = px.bar(
            x=sector_alloc['available_percentage'],
            y=sector_alloc.index,
            orientation='h',
            color=sector_alloc['available_percentage'],
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="",
            xaxis_title="Avg Available %"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Section 4: Certification Status
    st.markdown("## 🎓 Certification Compliance")
    
    col1, col2, col3 = st.columns(3)
    
    # Filter certifications for filtered employees
    filtered_emp_ids = filtered_emp['employee_id'].tolist()
    filtered_certs = data['certifications'][
        data['certifications']['employee_id'].isin(filtered_emp_ids)
    ]
    
    filtered_certs['expiry_date'] = pd.to_datetime(
        filtered_certs['expiry_date']
    )
    today = pd.to_datetime(datetime.now().date())
    
    active_certs = len(filtered_certs[filtered_certs['expiry_date'] > today])
    expired_certs = len(filtered_certs[filtered_certs['expiry_date'] <= today])
    expiring_soon = len(filtered_certs[
        (filtered_certs['expiry_date'] > today) &
        (filtered_certs['expiry_date'] < today + timedelta(days=180))
    ])
    
    with col1:
        st.metric("Active Certifications", active_certs)
    
    with col2:
        st.metric("Expiring Soon (0-6mo)", expiring_soon, delta_color="off")
    
    with col3:
        st.metric("Expired", expired_certs, delta_color="inverse")
    
    # Certifications by issuer
    st.markdown("### Certifications by Issuing Body")
    
    issuer_counts = filtered_certs['issuing_body'].value_counts()
    fig = px.bar(
        x=issuer_counts.index,
        y=issuer_counts.values,
        color=issuer_counts.values,
        color_continuous_scale="Sunset"
    )
    fig.update_layout(
        showlegend=False,
        height=300,
        xaxis_title="Issuing Body",
        yaxis_title="Count"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Expiring soon alert
    if expiring_soon > 0:
        st.markdown("### ⚠️ Certifications Expiring Soon")
        
        expiring_data = filtered_certs[
            (filtered_certs['expiry_date'] > today) &
            (filtered_certs['expiry_date'] < today + timedelta(days=180))
        ].sort_values('expiry_date')
        
        if not expiring_data.empty:
            display_data = pd.merge(
                expiring_data[['employee_id', 'certification_name', 'expiry_date']],
                data['employees'][['employee_id', 'first_name', 'last_name']],
                on='employee_id'
            )
            
            display_data['Days Until Expiry'] = (
                display_data['expiry_date'] - today
            ).dt.days
            
            st.dataframe(
                display_data[['first_name', 'last_name', 'certification_name', 
                             'Days Until Expiry']],
                use_container_width=True,
                hide_index=True
            )
    
    st.markdown("---")
    
    # Section 5: Sector Experience
    st.markdown("## 🌍 Sector Experience & Coverage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Sector Coverage")
        
        # Calculate sector coverage metrics
        sector_stats = []
        for sector in data['employees']['primary_sector'].unique():
            sector_emp = data['employees'][
                data['employees']['primary_sector'] == sector
            ]
            avg_years = data['projects'][
                data['projects']['sector'] == sector
            ]['start_date'].nunique()
            
            sector_stats.append({
                'Sector': sector,
                'People': len(sector_emp),
                'Experience': f"{len(sector_emp) * 2:.0f}y"  # Estimate
            })
        
        sector_df = pd.DataFrame(sector_stats).sort_values('People', ascending=False)
        
        fig = px.bar(
            sector_df,
            x='Sector',
            y='People',
            color='People',
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="Number of Employees"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Experience Depth by Sector")
        
        sector_depth = []
        for sector in data['employees']['primary_sector'].unique():
            sector_emp = data['employees'][
                data['employees']['primary_sector'] == sector
            ]
            avg_years = sector_emp['years_experience'].mean()
            
            sector_depth.append({
                'Sector': sector,
                'Avg Years': avg_years
            })
        
        depth_df = pd.DataFrame(sector_depth).sort_values(
            'Avg Years', ascending=True
        )
        
        fig = px.bar(
            depth_df,
            x='Avg Years',
            y='Sector',
            orientation='h',
            color='Avg Years',
            color_continuous_scale="YlOrRd"
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="",
            xaxis_title="Average Years Experience"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Export section
    st.markdown("## 📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Dashboard Data (CSV)"):
            export_data = filtered_emp.copy()
            csv = export_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"workforce_dashboard_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.caption("Exports currently filtered workforce data")

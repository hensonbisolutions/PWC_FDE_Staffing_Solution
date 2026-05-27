"""
Allocation Optimizer - Portfolio-Level Team Deployment Analysis

Provides strategic insights into:
- Team deployment concentration and utilization
- Risk identification (over-allocation, underutilization)
- Development gaps and skill imbalances
- Capacity optimization recommendations

Enables portfolio-level allocation decision-making.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def show_allocation_optimizer(data: dict):
    """Main allocation optimizer display."""
    
    st.markdown("""
    <div class="hero-card">
        <div class="hero-pill">Portfolio optimization</div>
        <h1>Allocation Optimizer - Portfolio View</h1>
        <p>Identify deployment risks, utilization gaps, and sector concentration across your workforce portfolio.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Calculate key metrics
    employees = data['employees']
    opportunities = data['opportunities']
    availability = data['availability']
    
    filled_opps = opportunities[opportunities['status'] == 'Filled']
    open_opps = opportunities[opportunities['status'] == 'Open']
    
    # Merge availability with employees
    emp_availability = employees.merge(availability, on='employee_id')
    
    # Portfolio metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_util = emp_availability['available_percentage'].mean()
        st.metric("Avg Utilization", f"{100-avg_util:.0f}%", 
                 delta=f"{100-avg_util:.0f}% deployed")
    
    with col2:
        bench_pct = len(emp_availability[emp_availability['available_percentage'] >= 50]) / len(emp_availability) * 100
        st.metric("Bench Capacity", f"{bench_pct:.0f}%")
    
    with col3:
        filled_count = len(filled_opps)
        st.metric("Active Deployments", filled_count)
    
    with col4:
        open_count = len(open_opps)
        st.metric("Unfilled Opportunities", open_count)
    
    with col5:
        risk_high = len(emp_availability[emp_availability['available_percentage'] < 20])
        st.metric("High-Risk Allocations", risk_high)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Utilization Portfolio",
        "⚠️ Risk Assessment",
        "🔄 Rebalancing Recommendations",
        "📈 Sector Allocation"
    ])
    
    # ========================================================================
    # TAB 1: UTILIZATION PORTFOLIO
    # ========================================================================
    with tab1:
        st.markdown("## Team Deployment Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Utilization Distribution")
            
            # Categorize utilization
            util_categories = pd.cut(
                emp_availability['available_percentage'],
                bins=[0, 20, 50, 80, 100],
                labels=['Fully Deployed (0-20%)', 'High (20-50%)', 
                       'Moderate (50-80%)', 'Available (80-100%)']
            )
            
            util_counts = util_categories.value_counts()
            colors = ['#90EE90', '#FFE4B5', '#FFB6C6', '#87CEEB']
            
            fig = go.Figure(data=[go.Pie(
                labels=util_counts.index,
                values=util_counts.values,
                marker=dict(colors=colors),
                hole=0.3
            )])
            fig.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Utilization by Seniority")
            
            seniority_util = emp_availability.groupby('seniority_level').agg({
                'available_percentage': 'mean'
            }).sort_values('available_percentage')
            
            fig = px.bar(
                x=100 - seniority_util['available_percentage'],
                y=seniority_util.index,
                orientation='h',
                labels={'x': 'Deployment %', 'y': 'Seniority Level'},
                color=100 - seniority_util['available_percentage'],
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("### Employee Allocation Status")
        
        detail_df = emp_availability[[
            'first_name', 'last_name', 'seniority_level', 'primary_sector',
            'available_percentage'
        ]].copy()
        
        detail_df['Deployment %'] = 100 - detail_df['available_percentage']
        detail_df['Status'] = detail_df['Deployment %'].apply(
            lambda x: '🔴 Critical' if x < 20 else '🟡 High' if x < 50 
            else '🟢 Moderate' if x < 80 else '⚪ Available'
        )
        
        detail_df = detail_df.sort_values('Deployment %', ascending=False)
        
        display_cols = ['first_name', 'last_name', 'seniority_level', 
                       'primary_sector', 'Deployment %', 'Status']
        display_df = detail_df[display_cols].copy()
        display_df.columns = ['First', 'Last', 'Seniority', 'Sector', 'Deploy %', 'Status']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 2: RISK ASSESSMENT
    # ========================================================================
    with tab2:
        st.markdown("## Risk Identification & Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Concentration Risk")
            
            # Risk by sector
            sector_allocation = filled_opps['client_sector'].value_counts()
            total_filled = len(filled_opps)
            
            fig = px.pie(
                values=sector_allocation.values,
                names=sector_allocation.index,
                title="Allocation Concentration by Sector",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Seniority Concentration")
            
            # Risk by seniority in filled opportunities
            emp_in_opps = filled_opps.merge(employees[['employee_id', 'seniority_level']], 
                                           left_on='opportunity_id', right_on='employee_id',
                                           how='left')
            
            if len(emp_in_opps) > 0:
                senior_dist = employees['seniority_level'].value_counts()
                fig = px.bar(
                    x=senior_dist.index,
                    y=senior_dist.values,
                    labels={'x': 'Seniority Level', 'y': 'Count'},
                    title="Workforce Seniority Distribution"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Risk alerts
        st.markdown("### Risk Alerts")
        
        # Over-allocated employees
        over_allocated = emp_availability[emp_availability['available_percentage'] < 20]
        if len(over_allocated) > 0:
            st.warning(f"🔴 **Critical**: {len(over_allocated)} employees fully deployed (no bench capacity)")
            with st.expander("View over-allocated employees"):
                st.dataframe(
                    over_allocated[['first_name', 'last_name', 'available_percentage']],
                    use_container_width=True,
                    hide_index=True
                )
        
        # Underutilized
        underutilized = emp_availability[emp_availability['available_percentage'] >= 80]
        if len(underutilized) > 0:
            st.info(f"⚪ **Capacity**: {len(underutilized)} employees mostly available (potential underutilization)")
        
        # Sector concentration
        if len(sector_allocation) > 0:
            max_sector_pct = sector_allocation.iloc[0] / total_filled * 100
            if max_sector_pct > 40:
                st.warning(f"⚠️ **Concentration Risk**: {sector_allocation.index[0]} accounts for {max_sector_pct:.0f}% of active allocations")
    
    # ========================================================================
    # TAB 3: REBALANCING RECOMMENDATIONS
    # ========================================================================
    with tab3:
        st.markdown("## Rebalancing & Optimization Recommendations")
        
        recommendations = []
        
        # Check for capacity
        fully_available = len(emp_availability[emp_availability['available_percentage'] >= 80])
        open_positions = len(open_opps)
        
        if fully_available > 0 and open_positions > 0:
            recommendations.append({
                'Priority': 'HIGH',
                'Issue': 'Capacity Available',
                'Recommendation': f'Deploy {min(fully_available, open_positions)} available employees to fill {open_positions} open opportunities',
                'Impact': 'Improve utilization, reduce time-to-staff'
            })
        
        # Check for critical allocation
        if len(over_allocated) > 0:
            recommendations.append({
                'Priority': 'CRITICAL',
                'Issue': 'Overallocation Risk',
                'Recommendation': f'Review and rebalance {len(over_allocated)} critical allocations to prevent burnout',
                'Impact': 'Reduce turnover risk, improve retention'
            })
        
        # Check sector concentration
        if len(sector_allocation) > 0 and sector_allocation.iloc[0] / total_filled > 0.4:
            recommendations.append({
                'Priority': 'MEDIUM',
                'Issue': 'Sector Concentration',
                'Recommendation': f'Diversify away from {sector_allocation.index[0]} sector to reduce client dependency',
                'Impact': 'Improve business resilience'
            })
        
        # Check skill distribution
        skill_diversity = data['skills'].groupby('employee_id')['skill_name'].nunique().mean()
        if skill_diversity < 3:
            recommendations.append({
                'Priority': 'MEDIUM',
                'Issue': 'Low Skill Diversity',
                'Recommendation': 'Invest in cross-training to improve team flexibility',
                'Impact': 'Increase deployment options'
            })
        
        if recommendations:
            rec_df = pd.DataFrame(recommendations)
            
            # Display by priority
            for priority in ['CRITICAL', 'HIGH', 'MEDIUM']:
                priority_recs = rec_df[rec_df['Priority'] == priority]
                if len(priority_recs) > 0:
                    st.markdown(f"### {priority} Priority")
                    for _, rec in priority_recs.iterrows():
                        if priority == 'CRITICAL':
                            st.error(f"**{rec['Issue']}**\n\n{rec['Recommendation']}\n\n*Impact*: {rec['Impact']}")
                        elif priority == 'HIGH':
                            st.warning(f"**{rec['Issue']}**\n\n{rec['Recommendation']}\n\n*Impact*: {rec['Impact']}")
                        else:
                            st.info(f"**{rec['Issue']}**\n\n{rec['Recommendation']}\n\n*Impact*: {rec['Impact']}")
        else:
            st.success("✅ No critical recommendations at this time. Portfolio is well-balanced.")
    
    # ========================================================================
    # TAB 4: SECTOR ALLOCATION
    # ========================================================================
    with tab4:
        st.markdown("## Sector-Level Deployment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Workforce by Sector")
            
            sector_emp = employees['primary_sector'].value_counts()
            fig = px.bar(
                x=sector_emp.values,
                y=sector_emp.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Sector'},
                color=sector_emp.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Active Deployments by Sector")
            
            sector_deploy = filled_opps['client_sector'].value_counts()
            fig = px.bar(
                x=sector_deploy.values,
                y=sector_deploy.index,
                orientation='h',
                labels={'x': 'Active Allocations', 'y': 'Sector'},
                color=sector_deploy.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Supply vs Demand by Sector")
        
        # Create comparison
        supply_demand = pd.DataFrame({
            'Supply': employees['primary_sector'].value_counts(),
            'Demand': filled_opps['client_sector'].value_counts()
        }).fillna(0)
        
        supply_demand['Gap'] = supply_demand['Supply'] - supply_demand['Demand']
        supply_demand = supply_demand.sort_values('Supply', ascending=True)
        
        fig = go.Figure(data=[
            go.Bar(y=supply_demand.index, x=supply_demand['Supply'], 
                  name='Available Employees', orientation='h'),
            go.Bar(y=supply_demand.index, x=supply_demand['Demand'],
                  name='Active Deployments', orientation='h')
        ])
        fig.update_layout(barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)

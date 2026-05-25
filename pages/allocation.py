"""
Allocation Page - Workforce Tracking and Capacity Planning

Provides visibility into:
- Current project assignments
- Bench (available) workforce
- Upcoming opportunities and timelines
- Capacity forecasting and utilization trends
- Allocation planning and scheduling

Enables allocation decisions and capacity-aware planning.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def show_allocation(data: dict):
    """Main allocation tracking page."""
    
    st.markdown("# 📋 Workforce Allocation & Capacity Planning")
    st.markdown("Track assignments, monitor capacity, and plan for upcoming needs")
    st.markdown("---")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_emp = len(data['employees'])
    allocated_opp = len(data['opportunities'][
        data['opportunities']['status'] == 'Filled'
    ])
    open_opp = len(data['opportunities'][
        data['opportunities']['status'] == 'Open'
    ])
    total_bench = len(data['availability'][
        data['availability']['available_percentage'] >= 50
    ])
    
    with col1:
        st.metric("Total Workforce", total_emp)
    
    with col2:
        st.metric("Active Allocations", allocated_opp)
    
    with col3:
        st.metric("Open Opportunities", open_opp)
    
    with col4:
        st.metric("Available for Deployment", total_bench)
    
    st.markdown("---")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Current Allocations",
        "👥 Bench (Available)",
        "📈 Upcoming",
        "📉 Forecast",
        "📤 Export"
    ])
    
    # ========================================================================
    # TAB 1: CURRENT ALLOCATIONS
    # ========================================================================
    with tab1:
        st.markdown("## Active Project Assignments")
        
        # Filter and sort
        col1, col2 = st.columns(2)
        
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                options=["End Date", "Employee", "Sector", "Duration"]
            )
        
        with col2:
            filter_sector = st.multiselect(
                "Filter by Sector",
                options=data['opportunities']['client_sector'].unique(),
                default=None
            )
        
        # Get filled opportunities
        filled_opps = data['opportunities'][
            data['opportunities']['status'] == 'Filled'
        ]
        
        if filter_sector:
            filled_opps = filled_opps[
                filled_opps['client_sector'].isin(filter_sector)
            ]
        
        if filled_opps.empty:
            st.info("No active allocations at this time")
        else:
            # Create allocation display
            allocation_data = []
            for _, opp in filled_opps.iterrows():
                allocation_data.append({
                    'Opportunity': opp['opportunity_name'],
                    'Sector': opp['client_sector'],
                    'Location': opp['location'],
                    'Start': opp['start_date'].strftime('%Y-%m-%d'),
                    'Duration (weeks)': opp['allocation_weeks'],
                    'End Date': (opp['start_date'] + 
                               timedelta(weeks=opp['allocation_weeks'])).strftime('%Y-%m-%d'),
                    'Priority': opp['priority'],
                    'Status': opp['status']
                })
            
            alloc_df = pd.DataFrame(allocation_data)
            
            st.dataframe(
                alloc_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Allocation timeline
            st.markdown("### Allocation Timeline")
            
            # Create Gantt-style timeline
            timeline_data = []
            for _, opp in filled_opps.iterrows():
                end_date = opp['start_date'] + timedelta(
                    weeks=opp['allocation_weeks']
                )
                timeline_data.append({
                    'Task': opp['opportunity_name'],
                    'Start': opp['start_date'],
                    'End': end_date,
                    'Duration': f"{opp['allocation_weeks']}w",
                    'Sector': opp['client_sector']
                })
            
            timeline_df = pd.DataFrame(timeline_data)
            
            fig = px.timeline(
                timeline_df,
                x_start="Start",
                x_end="End",
                y="Task",
                color="Sector",
                hover_name="Task",
                hover_data=['Duration'],
                title="Project Timeline (Next 52 weeks)",
                height=400
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="",
                hovermode="y unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # TAB 2: BENCH (AVAILABLE WORKFORCE)
    # ========================================================================
    with tab2:
        st.markdown("## Available Workforce (Bench)")
        
        # Get available employees
        avg_available = data['availability']['available_percentage'].mean()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Avg Availability",
                f"{avg_available:.0f}%"
            )
        
        with col2:
            fully_available = len(data['availability'][
                data['availability']['available_percentage'] >= 80
            ])
            st.metric("Fully Available", fully_available)
        
        with col3:
            partial_available = len(data['availability'][
                (data['availability']['available_percentage'] >= 20) &
                (data['availability']['available_percentage'] < 80)
            ])
            st.metric("Partially Available", partial_available)
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            min_available = st.slider(
                "Minimum availability %",
                min_value=0,
                max_value=100,
                value=50,
                step=10
            )
        
        with col2:
            willing_remote = st.checkbox(
                "Willing to work remotely",
                value=False
            )
        
        # Filter and merge data
        bench = data['availability'][
            data['availability']['available_percentage'] >= min_available
        ].merge(
            data['employees'],
            on='employee_id'
        )
        
        if willing_remote:
            bench = bench[bench['remote_willing'] == True]
        
        if bench.empty:
            st.info("No matching available workforce")
        else:
            # Sort by availability
            bench = bench.sort_values('available_percentage', ascending=False)
            
            # Display bench workforce
            display_data = bench[[
                'first_name', 'last_name', 'seniority_level',
                'primary_sector', 'location', 'available_percentage',
                'next_available_date'
            ]].copy()
            
            display_data.columns = [
                'First Name', 'Last Name', 'Seniority',
                'Sector', 'Location', 'Available %', 'Ready Date'
            ]
            
            display_data['Ready Date'] = display_data['Ready Date'].dt.strftime(
                '%Y-%m-%d'
            )
            
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Availability distribution
            st.markdown("### Availability Distribution")
            
            fig = px.histogram(
                bench,
                x='available_percentage',
                nbins=10,
                labels={'available_percentage': 'Available %', 'count': 'Count'},
                title="Distribution of Workforce Availability"
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Quick allocate option
            st.markdown("### 🚀 Quick Allocate")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_emp = st.selectbox(
                    "Select employee to allocate",
                    options=bench['first_name'].tolist()
                )
            
            with col2:
                if st.button("📌 Allocate to Opportunity"):
                    st.info(
                        f"Redirecting to Recommendations page to allocate "
                        f"{selected_emp}..."
                    )
    
    # ========================================================================
    # TAB 3: UPCOMING OPPORTUNITIES
    # ========================================================================
    with tab3:
        st.markdown("## Upcoming Opportunities")
        
        # Filter to open and in-progress
        upcoming = data['opportunities'][
            data['opportunities']['status'].isin(['Open', 'In Progress'])
        ].sort_values('start_date')
        
        if upcoming.empty:
            st.info("No upcoming opportunities")
        else:
            # Timeline of upcoming
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(
                    f"**Total Upcoming:** {len(upcoming)} opportunities"
                )
            
            with col2:
                next_30_days = len(upcoming[
                    upcoming['start_date'] <= 
                    datetime.now() + timedelta(days=30)
                ])
                st.markdown(f"**Starting in next 30 days:** {next_30_days}")
            
            # Opportunities table
            opp_display = upcoming[[
                'opportunity_id', 'opportunity_name', 'client_sector',
                'location', 'required_seniority', 'start_date',
                'allocation_weeks', 'priority'
            ]].copy()
            
            opp_display.columns = [
                'ID', 'Opportunity', 'Sector', 'Location',
                'Seniority', 'Start', 'Weeks', 'Priority'
            ]
            
            opp_display['Start'] = opp_display['Start'].dt.strftime('%Y-%m-%d')
            opp_display['Days Until Start'] = (
                upcoming['start_date'] - datetime.now()
            ).dt.days
            
            st.dataframe(
                opp_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Priority breakdown
            st.markdown("### Priority Breakdown")
            
            priority_counts = upcoming['priority'].value_counts()
            
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                color_discrete_map={
                    'Critical': '#d62728',
                    'High': '#ff7f0e',
                    'Medium': '#2ca02c',
                    'Low': '#1f77b4'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sector distribution of upcoming
            st.markdown("### Sector Distribution")
            
            sector_dist = upcoming['client_sector'].value_counts()
            
            fig = px.bar(
                x=sector_dist.index,
                y=sector_dist.values,
                color=sector_dist.values,
                color_continuous_scale="Viridis"
            )
            
            fig.update_layout(
                xaxis_title="Sector",
                yaxis_title="Number of Opportunities",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # TAB 4: CAPACITY FORECAST
    # ========================================================================
    with tab4:
        st.markdown("## 📉 Capacity Forecast (90-Day View)")
        
        # Generate forecast data
        forecast_data = []
        
        for days_ahead in range(0, 91, 7):
            forecast_date = datetime.now() + timedelta(days=days_ahead)
            
            # Count people still allocated at this date
            allocated = 0
            for _, opp in data['opportunities'].iterrows():
                if opp['status'] == 'Filled':
                    end_date = opp['start_date'] + timedelta(
                        weeks=opp['allocation_weeks']
                    )
                    if opp['start_date'] <= forecast_date <= end_date:
                        allocated += 1
            
            available = len(data['employees']) - allocated
            utilization = (allocated / len(data['employees'])) * 100
            
            forecast_data.append({
                'Date': forecast_date,
                'Days Ahead': days_ahead,
                'Allocated': allocated,
                'Available': available,
                'Utilization %': utilization
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        
        # Utilization trend
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'],
            y=forecast_df['Utilization %'],
            mode='lines+markers',
            name='Utilization',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            fill='tozeroy'
        ))
        
        fig.add_hline(
            y=75,
            line_dash="dash",
            line_color="orange",
            annotation_text="Target Utilization (75%)"
        )
        
        fig.update_layout(
            title="Workforce Utilization Forecast",
            xaxis_title="Date",
            yaxis_title="Utilization %",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast metrics
        col1, col2, col3 = st.columns(3)
        
        current_util = forecast_df.iloc[0]['Utilization %']
        peak_util = forecast_df['Utilization %'].max()
        low_util = forecast_df['Utilization %'].min()
        
        with col1:
            st.metric("Current Utilization", f"{current_util:.0f}%")
        
        with col2:
            st.metric("Peak Utilization", f"{peak_util:.0f}%")
        
        with col3:
            st.metric("Lowest Point", f"{low_util:.0f}%")
        
        # Risk assessment
        st.markdown("### 📋 Capacity Analysis")
        
        if peak_util > 90:
            st.warning(
                f"⚠️ Peak utilization ({peak_util:.0f}%) exceeds 90%. "
                "Consider increasing bench or spreading timelines."
            )
        
        if low_util < 40:
            st.info(
                f"💡 Lowest point ({low_util:.0f}%) indicates bench opportunity. "
                "Consider planning development initiatives or new projects."
            )
        
        # Forecast table
        st.markdown("### Detailed Forecast")
        
        display_forecast = forecast_df[[
            'Date', 'Allocated', 'Available', 'Utilization %'
        ]].copy()
        
        display_forecast['Date'] = display_forecast['Date'].dt.strftime('%Y-%m-%d')
        display_forecast['Utilization %'] = display_forecast['Utilization %'].round(1)
        
        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True
        )
    
    # ========================================================================
    # TAB 5: EXPORT
    # ========================================================================
    with tab5:
        st.markdown("## 📤 Export Data")
        
        st.markdown("### Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Allocations (CSV)"):
                filled_opps = data['opportunities'][
                    data['opportunities']['status'] == 'Filled'
                ]
                
                export_data = filled_opps[[
                    'opportunity_id', 'opportunity_name', 'client_sector',
                    'location', 'start_date', 'allocation_weeks', 'status'
                ]].copy()
                
                csv = export_data.to_csv(index=False)
                st.download_button(
                    label="Download Allocations",
                    data=csv,
                    file_name=f"allocations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📥 Export Bench Workforce (CSV)"):
                bench = data['availability'][
                    data['availability']['available_percentage'] >= 50
                ].merge(
                    data['employees'],
                    on='employee_id'
                )
                
                export_data = bench[[
                    'employee_id', 'first_name', 'last_name',
                    'seniority_level', 'primary_sector',
                    'available_percentage', 'next_available_date'
                ]].copy()
                
                csv = export_data.to_csv(index=False)
                st.download_button(
                    label="Download Bench",
                    data=csv,
                    file_name=f"bench_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        st.markdown("---")
        
        st.info(
            "📊 All exports include current date and can be used for "
            "further analysis in Excel or BI tools."
        )

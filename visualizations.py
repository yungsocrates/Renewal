"""
Visualization Module for NYC Public Schools Substitute Renewal Analytics
Handles chart creation, maps, and heatmap generation using Plotly
"""

import plotly.graph_objects as go
import plotly.offline as pyo
import pandas as pd
import os
from geographic_analysis import map_zip_to_borough

def get_zip_coordinates(zip_code):
    """
    Get approximate coordinates for a ZIP code using borough centroids
    
    Args:
        zip_code (str): ZIP code
        
    Returns:
        dict: Coordinates with 'lat' and 'lon' keys, or None if not found
    """
    import random
    
    # Use borough mapping to get approximate coordinates
    from_borough = map_zip_to_borough(zip_code)
    if from_borough != 'Unknown':
        # Borough centroids
        borough_coords = {
            'Manhattan': {'lat': 40.7831, 'lon': -73.9712},
            'Brooklyn': {'lat': 40.6782, 'lon': -73.9442},
            'Queens': {'lat': 40.7282, 'lon': -73.7949},
            'Bronx': {'lat': 40.8448, 'lon': -73.8648},
            'Staten Island': {'lat': 40.5795, 'lon': -74.1502},
            'Westchester County': {'lat': 41.1220, 'lon': -73.7949},
            'Nassau County': {'lat': 40.6546, 'lon': -73.5594},
            'Suffolk County': {'lat': 40.8176, 'lon': -72.6851},
            'Bergen County, NJ': {'lat': 40.9264, 'lon': -74.0431},
            'Hudson County, NJ': {'lat': 40.7282, 'lon': -74.0776},
            'Union County, NJ': {'lat': 40.6218, 'lon': -74.3107},
            'Essex County, NJ': {'lat': 40.7864, 'lon': -74.2191},
            'Rockland County, NY': {'lat': 41.1489, 'lon': -73.9441},
            'Fairfield County, CT': {'lat': 41.2033, 'lon': -73.2967}
        }
        
        if from_borough in borough_coords:
            # Add small random offset to spread points within borough
            base_coords = borough_coords[from_borough]
            lat_offset = random.uniform(-0.02, 0.02)
            lon_offset = random.uniform(-0.02, 0.02)
            
            return {
                'lat': base_coords['lat'] + lat_offset,
                'lon': base_coords['lon'] + lon_offset
            }
    
    return None

def create_nyc_borough_map(borough_data, output_dir):
    """
    Create interactive NYC area map showing substitute data for boroughs and neighboring counties
    
    Args:
        borough_data (dict): Borough/county analysis results
        output_dir (str): Output directory for HTML file
        
    Returns:
        str: Path to generated HTML file
    """
    # NYC Borough and neighboring county centroids for positioning
    area_coords = {
        # NYC Boroughs
        'Manhattan': {'lat': 40.7831, 'lon': -73.9712},
        'Brooklyn': {'lat': 40.6782, 'lon': -73.9442},
        'Queens': {'lat': 40.7282, 'lon': -73.7949},
        'Bronx': {'lat': 40.8448, 'lon': -73.8648},
        'Staten Island': {'lat': 40.5795, 'lon': -74.1502},
        
        # Neighboring Counties
        'Westchester County': {'lat': 41.1220, 'lon': -73.7949},
        'Nassau County': {'lat': 40.6546, 'lon': -73.5594},
        'Suffolk County': {'lat': 40.8176, 'lon': -72.6851},
        'Bergen County, NJ': {'lat': 40.9264, 'lon': -74.0431},
        'Hudson County, NJ': {'lat': 40.7282, 'lon': -74.0776},
        'Union County, NJ': {'lat': 40.6218, 'lon': -74.3107},
        'Essex County, NJ': {'lat': 40.7864, 'lon': -74.2191},
        'Rockland County, NY': {'lat': 41.1489, 'lon': -73.9441},
        'Fairfield County, CT': {'lat': 41.2033, 'lon': -73.2967}
    }
    
    # Prepare data for visualization
    lats = []
    lons = []
    area_names = []
    para_counts = []
    teacher_counts = []
    para_completion_rates = []
    teacher_completion_rates = []
    hover_texts = []
    area_types = []  # To distinguish NYC vs neighboring areas
    
    for area, coords in area_coords.items():
        if area in borough_data:
            data = borough_data[area]
            
            # Only include areas with data
            if data['para_eligible'] > 0 or data['teacher_eligible'] > 0:
                lats.append(coords['lat'])
                lons.append(coords['lon'])
                area_names.append(area)
                para_counts.append(data['para_eligible'])
                teacher_counts.append(data['teacher_eligible'])
                para_completion_rates.append(data['para_completion_rate'])
                teacher_completion_rates.append(data['teacher_completion_rate'])
                
                # Determine area type for color coding
                if area in ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']:
                    area_types.append('NYC Borough')
                else:
                    area_types.append('Neighboring County')
                
                # Create hover text
                hover_text = f"""
                <b>{area}</b><br>
                <b>Substitute Paraprofessionals:</b><br>
                • Total Eligible: {data['para_eligible']:,}<br>
                • Completed: {data['para_complete']:,}<br>
                • Outstanding: {data['para_outstanding']:,}<br>
                • Completion Rate: {data['para_completion_rate']:.1f}%<br>
                <br>
                <b>Substitute Teachers:</b><br>
                • Total Eligible: {data['teacher_eligible']:,}<br>
                • Completed: {data['teacher_complete']:,}<br>
                • Outstanding: {data['teacher_outstanding']:,}<br>
                • Completion Rate: {data['teacher_completion_rate']:.1f}%
                """
                hover_texts.append(hover_text)
    
    # Create the map
    fig = go.Figure()
    
    # Add scatter points for paraprofessionals
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=[max(15, min(80, count/10)) for count in para_counts],  # Size based on para count
            color=para_completion_rates,
            colorscale='RdYlGn',
            cmin=0,
            cmax=100,
            colorbar=dict(
                title=dict(
                    text="Para Completion Rate (%)",
                    side="right"
                ),
                tickmode="linear",
                tick0=0,
                dtick=20,
                x=-0.1,  # Position on the left side
                y=0.5
            ),
            sizemode='diameter',
            opacity=0.8
        ),
        text=area_names,
        hovertext=hover_texts,
        hoverinfo='text',
        name='Paraprofessionals'
    ))
    
    # Add a second trace for teachers (smaller circles)
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=[max(12, min(60, count/15)) for count in teacher_counts],  # Size based on teacher count
            color=teacher_completion_rates,
            colorscale='Blues',
            cmin=0,
            cmax=100,
            colorbar=dict(
                title=dict(
                    text="Teacher Completion Rate (%)",
                    side="right"
                ),
                tickmode="linear",
                tick0=0,
                dtick=20,
                x=1.02,  # Position on the right side
                y=0.5
            ),
            sizemode='diameter',
            opacity=0.7
        ),
        text=area_names,
        hovertext=hover_texts,
        hoverinfo='text',
        name='Teachers'
    ))
    
    # Update layout for expanded view
    fig.update_layout(
        title=dict(
            text="NYC & Tri-State Area Substitute Renewal Analytics",
            x=0.5,
            font=dict(size=24, color='#2c3e50', family='Arial Black')
        ),
        mapbox=dict(
            style='carto-positron',  # Use carto-positron for all maps
            center=dict(lat=40.7589, lon=-73.7004),
            zoom=8.5
        ),
        height=800,
        width=1200,
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        ),
        annotations=[
            dict(
                x=0.02,
                y=0.02,
                xref='paper',
                yref='paper',
                text='<b>Circle Size:</b> Number of Eligible Substitutes<br><b>Color:</b> Completion Rate<br><b>Border:</b> Dark Blue = NYC, Purple = Counties',
                showarrow=False,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1,
                font=dict(size=10)
            )
        ]
    )
    
    # Save as HTML using plotly.offline to match other charts
    output_file = os.path.join(output_dir, 'nyc_borough_map.html')
    pyo.plot(fig, filename=output_file, auto_open=False)
    
    return output_file

def create_para_zipcode_heatmap(df_para, output_dir):
    """
    Create ZIP code heatmap showing paraprofessional distribution density
    
    Args:
        df_para (pd.DataFrame): Paraprofessional data with ZIP codes
        output_dir (str): Output directory for HTML file
        
    Returns:
        str: Path to generated HTML file
    """
    # Process paraprofessional data
    zip_counts = {}
    if df_para is not None and not df_para.empty:
        para_zip_counts = df_para['Postal'].value_counts()
        for zip_code, count in para_zip_counts.items():
            if str(zip_code) not in ['Unknown', 'nan', 'None', '']:
                zip_counts[str(zip_code)] = count
    
    # Get actual ZIP code coordinates
    lats = []
    lons = []
    counts = []
    zip_codes = []
    hover_texts = []
    
    for zip_code, count in zip_counts.items():
        coords = get_zip_coordinates(zip_code)
        if coords:
            lats.append(coords['lat'])
            lons.append(coords['lon'])
            counts.append(count)
            zip_codes.append(zip_code)
            
            # Create hover text with ZIP code and count
            hover_text = f"<b>ZIP Code: {zip_code}</b><br>Paraprofessionals: {count:,}"
            hover_texts.append(hover_text)
    
    # Create heatmap
    fig = go.Figure()
    
    if lats and lons and counts:
        # Get the actual maximum for this dataset
        max_count = max(counts) if counts else 100
        
        fig.add_trace(go.Densitymapbox(
            lat=lats,
            lon=lons,
            z=counts,
            radius=20,
            colorscale='Viridis',
            showscale=True,
            zmin=0,
            zmax=max_count,
            colorbar=dict(
                title=f"Number of Paraprofessionals<br>(Max: {max_count:,})",
                x=1.02
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="NYC Substitute Paraprofessionals - ZIP Code Distribution",
            x=0.5,
            font=dict(size=20, color='#2c3e50')
        ),
        mapbox=dict(
            style='carto-positron',
            center=dict(lat=40.7128, lon=-73.9060),
            zoom=9
        ),
        height=800,
        width=1200,
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    # Save as HTML
    output_file = os.path.join(output_dir, 'para_zipcode_heatmap.html')
    pyo.plot(fig, filename=output_file, auto_open=False)
    
    return output_file

def create_teacher_zipcode_heatmap(df_teacher, output_dir):
    """
    Create ZIP code heatmap showing teacher distribution density
    
    Args:
        df_teacher (pd.DataFrame): Teacher data with ZIP codes
        output_dir (str): Output directory for HTML file
        
    Returns:
        str: Path to generated HTML file
    """
    # Process teacher data
    zip_counts = {}
    if df_teacher is not None and not df_teacher.empty:
        teacher_zip_counts = df_teacher['Postal'].value_counts()
        for zip_code, count in teacher_zip_counts.items():
            # Clean ZIP code - remove .0 from floats and convert to string
            clean_zip = str(zip_code).replace('.0', '').strip()
            if clean_zip not in ['Unknown', 'nan', 'None', '']:
                zip_counts[clean_zip] = count
    
    # Get actual ZIP code coordinates
    lats = []
    lons = []
    counts = []
    zip_codes = []
    hover_texts = []
    
    for zip_code, count in zip_counts.items():
        coords = get_zip_coordinates(zip_code)
        if coords:
            lats.append(coords['lat'])
            lons.append(coords['lon'])
            counts.append(count)
            zip_codes.append(zip_code)
            
            # Create hover text with ZIP code and count
            hover_text = f"<b>ZIP Code: {zip_code}</b><br>Teachers: {count:,}"
            hover_texts.append(hover_text)
    
    # Create heatmap
    fig = go.Figure()
    
    if lats and lons and counts:
        # Get the actual maximum for this dataset
        max_count = max(counts) if counts else 100
        
        fig.add_trace(go.Densitymapbox(
            lat=lats,
            lon=lons,
            z=counts,
            radius=20,
            colorscale='Plasma',
            showscale=True,
            zmin=0,
            zmax=max_count,
            colorbar=dict(
                title=f"Number of Teachers<br>(Max: {max_count:,})",
                x=1.02
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="NYC Substitute Teachers - ZIP Code Distribution",
            x=0.5,
            font=dict(size=20, color='#2c3e50')
        ),
        mapbox=dict(
            style='carto-positron',
            center=dict(lat=40.7128, lon=-73.9060),
            zoom=9
        ),
        height=800,
        width=1200,
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    # Save as HTML
    output_file = os.path.join(output_dir, 'teacher_zipcode_heatmap.html')
    pyo.plot(fig, filename=output_file, auto_open=False)
    
    return output_file

def create_visualization_charts(para_results, teacher_results, output_dir):
    """
    Create interactive visualization charts
    
    Args:
        para_results (dict): Paraprofessional analysis results
        teacher_results (dict): Teacher analysis results
        output_dir (str): Output directory for charts
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    
    # Helper function for formatting numbers
    def format_number(num):
        return f"{num:,}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Combined Stacked Bar Chart - one bar for SPA, one bar for STE
    # Each bar shows the breakdown of renewal statuses
    
    # Define the status categories and their colors
    status_categories = ['Completed', 'Outstanding - RA Incomplete', 'Outstanding - Days Only', 
                        'Outstanding - Child Abuse Only', 'Outstanding - ATAS Only', 'Outstanding - Other']
    colors = ['#28a745', '#dc3545', '#fd7e14', '#ffc107', '#17a2b8', '#6f42c1']
    
    # SPA data breakdown
    spa_completed = para_results.get('total_complete', 0)
    spa_ra_incomplete = para_results.get('ra_not_complete', 0)
    spa_days_only = para_results.get('days_worked_only', 0)
    spa_child_abuse_only = para_results.get('child_abuse_workshop_only', 0)
    spa_atas_only = para_results.get('atas_only', 0)
    spa_other = para_results.get('total_outstanding', 0) - spa_ra_incomplete - spa_days_only - spa_child_abuse_only - spa_atas_only
    spa_other = max(0, spa_other)  # Ensure non-negative
    
    # STE data breakdown (using PRC/PRU)
    ste_completed = teacher_results.get('total_prc_pru_complete', 0)
    ste_ra_incomplete = teacher_results.get('prc_pru_ra_not_complete', 0)
    ste_days_only = teacher_results.get('prc_pru_days_worked_only', 0)
    ste_child_abuse_only = teacher_results.get('prc_pru_child_abuse_workshop_only', 0)
    ste_atas_only = teacher_results.get('prc_pru_other_requirements_only', 0)  # Using "other requirements" as ATAS equivalent
    ste_other = teacher_results.get('total_prc_pru_outstanding', 0) - ste_ra_incomplete - ste_days_only - ste_child_abuse_only - ste_atas_only
    ste_other = max(0, ste_other)  # Ensure non-negative
    
    # Create stacked bar chart
    fig_overview = go.Figure()
    
    # Add each status category as a separate trace
    spa_values = [spa_completed, spa_ra_incomplete, spa_days_only, spa_child_abuse_only, spa_atas_only, spa_other]
    ste_values = [ste_completed, ste_ra_incomplete, ste_days_only, ste_child_abuse_only, ste_atas_only, ste_other]
    
    # Calculate totals for percentage calculations
    spa_total = sum(spa_values)
    ste_total = sum(ste_values)
    
    for i, (category, color) in enumerate(zip(status_categories, colors)):
        # Calculate percentages
        spa_percentage = (spa_values[i] / spa_total * 100) if spa_total > 0 else 0
        ste_percentage = (ste_values[i] / ste_total * 100) if ste_total > 0 else 0
        
        # Create text labels with count and percentage (only show if value > 0)
        spa_text = f"{format_number(spa_values[i])}<br>({spa_percentage:.1f}%)" if spa_values[i] > 0 else ""
        ste_text = f"{format_number(ste_values[i])}<br>({ste_percentage:.1f}%)" if ste_values[i] > 0 else ""
        
        fig_overview.add_trace(go.Bar(
            name=category,
            x=['Substitute Paraprofessionals (SPA)', 'Substitute Teachers (STE)'],
            y=[spa_values[i], ste_values[i]],
            marker_color=color,
            text=[spa_text, ste_text],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial Black"),
            hovertemplate='<b>%{x}</b><br><b>' + category + '</b><br>Count: %{y:,}<br>Percentage: %{customdata:.1f}%<extra></extra>',
            customdata=[spa_percentage, ste_percentage]
        ))
    
    fig_overview.update_layout(
        title='NYC DOE Substitute Renewal Status Breakdown: SPA vs STE',
        xaxis_title='Substitute Groups',
        yaxis_title='Number of Substitutes',
        barmode='stack',
        height=600,
        width=900,
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150, l=60, t=80, b=60)  # Adjusted margins for better fit
    )
    
    # Add total counts as annotations (positioned higher above the bars)
    spa_total_eligible = para_results.get('total_eligible', 0)
    ste_total_eligible = teacher_results.get('total_prc_pru_eligible', 0)
    
    # Calculate the maximum height for positioning
    max_spa_height = sum(spa_values)
    max_ste_height = sum(ste_values)
    
    fig_overview.add_annotation(
        x=0, y=max_spa_height + (max_spa_height * 0.08),  # Position 8% above the bar
        text=f"Total Eligible: {format_number(spa_total_eligible)}",
        showarrow=False,
        font=dict(size=14, color="#2C5282", family="Arial Black"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#2C5282",
        borderwidth=1
    )
    
    fig_overview.add_annotation(
        x=1, y=max_ste_height + (max_ste_height * 0.08),  # Position 8% above the bar
        text=f"Total Eligible: {format_number(ste_total_eligible)}",
        showarrow=False,
        font=dict(size=14, color="#2C5282", family="Arial Black"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#2C5282",
        borderwidth=1
    )
    
    # Add grid lines for better readability
    fig_overview.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    overview_chart_file = os.path.join(output_dir, 'combined_overview.html')
    pyo.plot(fig_overview, filename=overview_chart_file, auto_open=False)
    
    # Detailed Paraprofessional Chart (keep for reference)
    para_labels = ['Total Eligible', 'Completed', 'Outstanding', 'RA Not Complete', 
                   'Days Only', 'ATAS Only', 'Child Abuse Only']
    para_values_detailed = [
        para_results.get('total_eligible', 0),
        para_results.get('total_complete', 0),
        para_results.get('total_outstanding', 0),
        para_results.get('ra_not_complete', 0),
        para_results.get('days_worked_only', 0),
        para_results.get('atas_only', 0),
        para_results.get('child_abuse_workshop_only', 0)
    ]
    
    fig_para = go.Figure(data=[
        go.Bar(
            x=para_labels,
            y=para_values_detailed,
            marker_color=['#2C5282', '#28a745', '#fd7e14', '#dc3545', 
                         '#6f42c1', '#17a2b8', '#ffc107'],
            text=[format_number(v) for v in para_values_detailed],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>'
        )
    ])
    
    fig_para.update_layout(
        title='Substitute Paraprofessional (SPA) Detailed Analysis',
        xaxis_title='Renewal Categories',
        yaxis_title='Number of Substitutes',
        height=500,
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white'
    )
    
    fig_para.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig_para.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    para_chart_file = os.path.join(output_dir, 'paraprofessional_overview.html')
    pyo.plot(fig_para, filename=para_chart_file, auto_open=False)
    
    # Detailed Teacher Chart (keep for reference)
    teacher_labels = ['Total Eligible', 'PRC/PRU Eligible', 'PRC/PRU Complete', 
                     'PRC/PRU Outstanding', 'Teachers On Leave', 'Retirees']
    teacher_values_detailed = [
        teacher_results.get('total_eligible', 0),
        teacher_results.get('total_prc_pru_eligible', 0),
        teacher_results.get('total_prc_pru_complete', 0),
        teacher_results.get('total_prc_pru_outstanding', 0),
        teacher_results.get('total_teachers_on_leave', 0),
        teacher_results.get('total_retirees', 0)
    ]
    
    fig_teacher = go.Figure(data=[
        go.Bar(
            x=teacher_labels,
            y=teacher_values_detailed,
            marker_color=['#1976d2', '#28a745', '#fd7e14', '#dc3545', 
                         '#6f42c1', '#17a2b8'],
            text=[format_number(v) for v in teacher_values_detailed],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>'
        )
    ])
    
    fig_teacher.update_layout(
        title='Substitute Teacher (STE) Detailed Analysis',
        xaxis_title='Renewal Categories',
        yaxis_title='Number of Substitutes',
        height=500,
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white'
    )
    
    fig_teacher.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig_teacher.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    teacher_chart_file = os.path.join(output_dir, 'teacher_overview.html')
    pyo.plot(fig_teacher, filename=teacher_chart_file, auto_open=False)
    
    # Combined Comparison Pie Chart (keep existing)
    fig_combined = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Paraprofessionals', 'Teachers'),
        specs=[[{"type": "domain"}, {"type": "domain"}]]
    )
    
    # Paraprofessional pie chart
    fig_combined.add_trace(
        go.Pie(
            labels=['Complete', 'Outstanding'],
            values=[para_results.get('total_complete', 0), 
                   para_results.get('total_outstanding', 0)],
            name="Paraprofessionals",
            hole=0.3,
            marker_colors=['#28a745', '#fd7e14'],
            showlegend=True
        ),
        row=1, col=1
    )

    # Teacher pie chart
    fig_combined.add_trace(
        go.Pie(
            labels=['Complete', 'Outstanding', 'On Leave', 'Retirees'],
            values=[teacher_results.get('total_prc_pru_complete', 0),
                   teacher_results.get('total_prc_pru_outstanding', 0),
                   teacher_results.get('total_teachers_on_leave', 0),
                   teacher_results.get('total_retirees', 0)],
            name="Teachers",
            hole=0.3,
            marker_colors=['#28a745', '#fd7e14', '#6f42c1', '#17a2b8'],
            showlegend=True
        ),
        row=1, col=2
    )
    
    fig_combined.update_layout(
        title_text="Renewal Status Comparison: Paraprofessionals vs Teachers",
        height=500,
        width=1200,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            traceorder="normal"
        )
    )
    
    combined_chart_file = os.path.join(output_dir, 'combined_comparison.html')
    pyo.plot(fig_combined, filename=combined_chart_file, auto_open=False)
    
    return [overview_chart_file, para_chart_file, teacher_chart_file, combined_chart_file]

def create_zipcode_choropleth_map_dual(df_para, df_teacher, df_boundaries, output_file, para_col='count', teacher_col='count', zip_col='zip_code', boundary_zip_col='MODZCTA'):
    """
    Create a dual ZIP code choropleth map for substitute paraprofessional and teacher counts in NYC.
    Allows toggling between para and teacher counts using Plotly dropdown.

    Args:
        df_para (pd.DataFrame): DataFrame with para counts by ZIP code (columns: zip_col, para_col)
        df_teacher (pd.DataFrame): DataFrame with teacher counts by ZIP code (columns: zip_col, teacher_col)
        df_boundaries (pd.DataFrame): DataFrame with ZIP code boundaries (columns: boundary_zip_col, 'the_geom' as WKT)
        output_file (str): Path to save the HTML file
        para_col (str): Column name for para counts in df_para
        teacher_col (str): Column name for teacher counts in df_teacher
        zip_col (str): Column name for ZIP code in df_para/df_teacher
        boundary_zip_col (str): Column name for ZIP code in df_boundaries
    """
    import geopandas as gpd
    from shapely import wkt
    import plotly.graph_objects as go
    import plotly.offline as pyo

    # Prepare boundaries GeoDataFrame
    gdf = df_boundaries.copy()
    gdf['geometry'] = gdf['the_geom'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf[boundary_zip_col] = gdf[boundary_zip_col].astype(str)

    # Merge para and teacher counts
    df_para = df_para.copy()
    df_para[zip_col] = df_para[zip_col].astype(str)
    df_teacher = df_teacher.copy()
    df_teacher[zip_col] = df_teacher[zip_col].astype(str)

    gdf_para = gdf.merge(df_para[[zip_col, para_col]], left_on=boundary_zip_col, right_on=zip_col, how='left')
    gdf_teacher = gdf.merge(df_teacher[[zip_col, teacher_col]], left_on=boundary_zip_col, right_on=zip_col, how='left')

    # Fill NaN counts with 0
    gdf_para[para_col] = gdf_para[para_col].fillna(0)
    gdf_teacher[teacher_col] = gdf_teacher[teacher_col].fillna(0)

    # Create Plotly traces
    def make_trace(gdf, value_col, name, colorscale):
        return go.Choroplethmapbox(
            geojson=gdf.set_index(boundary_zip_col)['geometry'].__geo_interface__,
            locations=gdf[boundary_zip_col],
            z=gdf[value_col],
            colorscale=colorscale,
            marker_line_width=0.5,
            marker_line_color='black',
            colorbar_title=f'{name} Count',
            zmin=0,
            zmax=max(gdf[value_col].max(), 1),
            text=gdf[boundary_zip_col],
            hovertemplate=f'ZIP: %{{text}}<br>{name}: %{{z}}<extra></extra>',
            name=name,
            visible=True if name == 'Paraprofessionals' else False
        )

    trace_para = make_trace(gdf_para, para_col, 'Paraprofessionals', 'Viridis')
    trace_teacher = make_trace(gdf_teacher, teacher_col, 'Teachers', 'Plasma')

    # Create figure with both traces, only one visible at a time
    fig = go.Figure(data=[trace_para, trace_teacher])
    fig.update_layout(
        mapbox_style='carto-positron',
        mapbox_zoom=9,
        mapbox_center={"lat": 40.7128, "lon": -73.9060},
        height=800,
        width=1200,
        title_text="NYC Substitute Counts by ZIP Code (Choropleth)",
        title=dict(
            x=0,  # Left align the title
            font=dict(size=22, color='#2c3e50', family='Arial Black')
        ),
        margin=dict(l=0, r=0, t=90, b=0),
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        args=[{"visible": [True, False]}],
                        label="Paraprofessionals",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, True]}],
                        label="Teachers",
                        method="update"
                    )
                ],
                direction="left",
                pad={"r": 0, "t": 0},
                showactive=True,
                type="buttons",
                x=1,
                xanchor="right",
                y=1.08,
                yanchor="top"
            ),
        ]
    )
    pyo.plot(fig, filename=output_file, auto_open=False)
    return output_file

def create_zipcode_heatmap_dual(df_para, df_teacher, output_dir):
    """
    Create a dual ZIP code heatmap for substitute paraprofessional and teacher distribution density with toggle buttons.

    Args:
        df_para (pd.DataFrame): Paraprofessional data with ZIP codes
        df_teacher (pd.DataFrame): Teacher data with ZIP codes
        output_dir (str): Output directory for HTML file
    Returns:
        str: Path to generated HTML file
    """
    import plotly.graph_objects as go
    import plotly.offline as pyo
    import os

    # Helper to process data
    def process_zip_counts(df, label):
        zip_counts = {}
        if df is not None and not df.empty:
            counts = df['Postal'].value_counts()
            for zip_code, count in counts.items():
                clean_zip = str(zip_code).replace('.0', '').strip()
                if clean_zip not in ['Unknown', 'nan', 'None', '']:
                    zip_counts[clean_zip] = count
        lats, lons, counts, zip_codes, hover_texts = [], [], [], [], []
        for zip_code, count in zip_counts.items():
            coords = get_zip_coordinates(zip_code)
            if coords:
                lats.append(coords['lat'])
                lons.append(coords['lon'])
                counts.append(count)
                zip_codes.append(zip_code)
                hover_text = f"<b>ZIP Code: {zip_code}</b><br>{label}: {count:,}"
                hover_texts.append(hover_text)
        return lats, lons, counts, zip_codes, hover_texts

    # Para data
    para_lats, para_lons, para_counts, para_zip_codes, para_hover_texts = process_zip_counts(df_para, "Paraprofessionals")
    # Teacher data
    teacher_lats, teacher_lons, teacher_counts, teacher_zip_codes, teacher_hover_texts = process_zip_counts(df_teacher, "Teachers")

    max_para = max(para_counts) if para_counts else 1
    max_teacher = max(teacher_counts) if teacher_counts else 1

    # Create traces
    trace_para = go.Densitymapbox(
        lat=para_lats,
        lon=para_lons,
        z=para_counts,
        radius=20,
        colorscale='Viridis',
        showscale=True,
        zmin=0,
        zmax=max_para,
        colorbar=dict(title=f"Number of Paraprofessionals<br>(Max: {max_para:,})", x=1.02),
        text=para_hover_texts,
        hovertemplate='%{text}<extra></extra>',
        visible=True,
        name="Paraprofessionals"
    )
    trace_teacher = go.Densitymapbox(
        lat=teacher_lats,
        lon=teacher_lons,
        z=teacher_counts,
        radius=20,
        colorscale='Plasma',
        showscale=True,
        zmin=0,
        zmax=max_teacher,
        colorbar=dict(title=f"Number of Teachers<br>(Max: {max_teacher:,})", x=1.02),
        text=teacher_hover_texts,
        hovertemplate='%{text}<extra></extra>',
        visible=False,
        name="Teachers"
    )

    fig = go.Figure(data=[trace_para, trace_teacher])
    fig.update_layout(
        mapbox=dict(
            style='carto-positron',
            center=dict(lat=40.7128, lon=-73.9060),
            zoom=9
        ),
        height=800,
        width=1200,
        title_text="NYC Substitute ZIP Code Heatmap (Toggle)",
        title=dict(
            x=0,
            font=dict(size=20, color='#2c3e50')
        ),
        margin=dict(l=0, r=0, t=90, b=0),
        updatemenus=[
            dict(
                buttons=[
                    dict(args=[{"visible": [True, False]}], label="Paraprofessionals", method="update"),
                    dict(args=[{"visible": [False, True]}], label="Teachers", method="update")
                ],
                direction="left",
                pad={"r": 0, "t": 0},
                showactive=True,
                type="buttons",
                x=1,
                xanchor="right",
                y=1.08,
                yanchor="top"
            ),
        ]
    )
    output_file = os.path.join(output_dir, 'nyc_zipcode_heatmap_dual.html')
    pyo.plot(fig, filename=output_file, auto_open=False)
    return output_file

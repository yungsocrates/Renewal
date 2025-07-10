"""
Visualization Module for NYC Public Schools Substitute Renewal Analytics
Handles chart creation, maps, and heatmap generation using Plotly
"""

import plotly.graph_objects as go
import plotly.offline as pyo
import pandas as pd
import os
from geographic_analysis import map_zip_to_borough

# Accurate ZIP code coordinates for NYC and nearby areas (add more as needed)
zip_coords = {
        # Manhattan ZIP codes
        '10001': {'lat': 40.7505, 'lon': -73.9934}, '10002': {'lat': 40.7157, 'lon': -73.9860},
        '10003': {'lat': 40.7322, 'lon': -73.9867}, '10004': {'lat': 40.7047, 'lon': -74.0142},
        '10005': {'lat': 40.7069, 'lon': -74.0113}, '10006': {'lat': 40.7096, 'lon': -74.0130},
        '10007': {'lat': 40.7133, 'lon': -74.0070}, '10009': {'lat': 40.7268, 'lon': -73.9779},
        '10010': {'lat': 40.7397, 'lon': -73.9773}, '10011': {'lat': 40.7405, 'lon': -74.0014},
        '10012': {'lat': 40.7253, 'lon': -74.0034}, '10013': {'lat': 40.7200, 'lon': -74.0026},
        '10014': {'lat': 40.7342, 'lon': -74.0064}, '10016': {'lat': 40.7464, 'lon': -73.9756},
        '10017': {'lat': 40.7520, 'lon': -73.9717}, '10018': {'lat': 40.7549, 'lon': -73.9930},
        '10019': {'lat': 40.7658, 'lon': -73.9873}, '10020': {'lat': 40.7584, 'lon': -73.9738},
        '10021': {'lat': 40.7697, 'lon': -73.9598}, '10022': {'lat': 40.7575, 'lon': -73.9709},
        '10023': {'lat': 40.7765, 'lon': -73.9814}, '10024': {'lat': 40.7875, 'lon': -73.9745},
        '10025': {'lat': 40.7982, 'lon': -73.9671}, '10026': {'lat': 40.8017, 'lon': -73.9527},
        '10027': {'lat': 40.8115, 'lon': -73.9530}, '10028': {'lat': 40.7763, 'lon': -73.9532},
        '10029': {'lat': 40.7919, 'lon': -73.9441}, '10030': {'lat': 40.8182, 'lon': -73.9444},
        '10031': {'lat': 40.8251, 'lon': -73.9495}, '10032': {'lat': 40.8387, 'lon': -73.9417},
        '10033': {'lat': 40.8502, 'lon': -73.9342}, '10034': {'lat': 40.8677, 'lon': -73.9212},
        '10035': {'lat': 40.7957, 'lon': -73.9389}, '10036': {'lat': 40.7590, 'lon': -73.9845},
        '10037': {'lat': 40.8142, 'lon': -73.9370}, '10038': {'lat': 40.7086, 'lon': -74.0020},
        '10039': {'lat': 40.8267, 'lon': -73.9363}, '10040': {'lat': 40.8588, 'lon': -73.9302},
        
        # Brooklyn ZIP codes (sample - major ones)
        '11201': {'lat': 40.6945, 'lon': -73.9901}, '11203': {'lat': 40.6514, 'lon': -73.9342},
        '11204': {'lat': 40.6189, 'lon': -73.9842}, '11205': {'lat': 40.6945, 'lon': -73.9665},
        '11206': {'lat': 40.7022, 'lon': -73.9421}, '11207': {'lat': 40.6720, 'lon': -73.8946},
        '11208': {'lat': 40.6591, 'lon': -73.8736}, '11209': {'lat': 40.6226, 'lon': -74.0305},
        '11210': {'lat': 40.6282, 'lon': -73.9473}, '11211': {'lat': 40.7115, 'lon': -73.9535},
        '11212': {'lat': 40.6627, 'lon': -73.9063}, '11213': {'lat': 40.6711, 'lon': -73.9363},
        '11214': {'lat': 40.5993, 'lon': -73.9942}, '11215': {'lat': 40.6628, 'lon': -73.9865},
        '11216': {'lat': 40.6808, 'lon': -73.9419}, '11217': {'lat': 40.6806, 'lon': -73.9779},
        '11218': {'lat': 40.6434, 'lon': -73.9773}, '11219': {'lat': 40.6323, 'lon': -73.9963},
        '11220': {'lat': 40.6412, 'lon': -74.0170}, '11221': {'lat': 40.6911, 'lon': -73.9275},
        '11222': {'lat': 40.7284, 'lon': -73.9474}, '11223': {'lat': 40.5969, 'lon': -73.9732},
        '11224': {'lat': 40.5775, 'lon': -73.9874}, '11225': {'lat': 40.6622, 'lon': -73.9541},
        '11226': {'lat': 40.6465, 'lon': -73.9563}, '11228': {'lat': 40.6166, 'lon': -74.0120},
        '11229': {'lat': 40.6008, 'lon': -73.9442}, '11230': {'lat': 40.6226, 'lon': -73.9652},
        '11231': {'lat': 40.6782, 'lon': -74.0067}, '11232': {'lat': 40.6569, 'lon': -74.0090},
        '11233': {'lat': 40.6783, 'lon': -73.9196}, '11234': {'lat': 40.5992, 'lon': -73.9192},
        '11235': {'lat': 40.5847, 'lon': -73.9484}, '11236': {'lat': 40.6396, 'lon': -73.9014},
        '11237': {'lat': 40.7040, 'lon': -73.8811}, '11238': {'lat': 40.6795, 'lon': -73.9646},
        '11239': {'lat': 40.6471, 'lon': -73.8705}, '11249': {'lat': 40.7208, 'lon': -73.9425},
        '11251': {'lat': 40.6901, 'lon': -73.9901}, '11252': {'lat': 40.6901, 'lon': -73.9901},
        
        # Queens ZIP codes (sample - major ones)
        '11004': {'lat': 40.7450, 'lon': -73.7713}, '11005': {'lat': 40.7480, 'lon': -73.7713},
        '11101': {'lat': 40.7359, 'lon': -73.9392}, '11102': {'lat': 40.7734, 'lon': -73.9196},
        '11103': {'lat': 40.7634, 'lon': -73.9118}, '11104': {'lat': 40.7443, 'lon': -73.9196},
        '11105': {'lat': 40.7789, 'lon': -73.9067}, '11106': {'lat': 40.7628, 'lon': -73.9302},
        '11354': {'lat': 40.7687, 'lon': -73.8370}, '11355': {'lat': 40.7498, 'lon': -73.8201},
        '11356': {'lat': 40.7848, 'lon': -73.8468}, '11357': {'lat': 40.7858, 'lon': -73.8269},
        '11358': {'lat': 40.7608, 'lon': -73.7958}, '11360': {'lat': 40.7828, 'lon': -73.7784},
        '11361': {'lat': 40.7638, 'lon': -73.7738}, '11362': {'lat': 40.7578, 'lon': -73.7678},
        '11363': {'lat': 40.7718, 'lon': -73.7535}, '11364': {'lat': 40.7448, 'lon': -73.7735},
        '11365': {'lat': 40.7407, 'lon': -73.7949}, '11366': {'lat': 40.7288, 'lon': -73.7949},
        '11367': {'lat': 40.7318, 'lon': -73.8249}, '11368': {'lat': 40.7508, 'lon': -73.8549},
        '11369': {'lat': 40.7628, 'lon': -73.8649}, '11370': {'lat': 40.7648, 'lon': -73.8949},
        '11372': {'lat': 40.7548, 'lon': -73.8749}, '11373': {'lat': 40.7408, 'lon': -73.8749},
        '11374': {'lat': 40.7288, 'lon': -73.8549}, '11375': {'lat': 40.7198, 'lon': -73.8349},
        '11377': {'lat': 40.7437, 'lon': -73.9049}, '11378': {'lat': 40.7167, 'lon': -73.8949},
        '11379': {'lat': 40.7217, 'lon': -73.8749}, '11385': {'lat': 40.7017, 'lon': -73.8749},
        '11411': {'lat': 40.6917, 'lon': -73.7449}, '11412': {'lat': 40.6997, 'lon': -73.7649},
        '11413': {'lat': 40.6717, 'lon': -73.7649}, '11414': {'lat': 40.6577, 'lon': -73.8449},
        '11415': {'lat': 40.7067, 'lon': -73.8249}, '11416': {'lat': 40.6837, 'lon': -73.8449},
        '11417': {'lat': 40.6777, 'lon': -73.8349}, '11418': {'lat': 40.6977, 'lon': -73.8349},
        '11419': {'lat': 40.6917, 'lon': -73.8149}, '11420': {'lat': 40.6677, 'lon': -73.7649},
        '11421': {'lat': 40.6937, 'lon': -73.8649}, '11422': {'lat': 40.6597, 'lon': -73.7349},
        '11423': {'lat': 40.7097, 'lon': -73.7649}, '11426': {'lat': 40.7377, 'lon': -73.7049},
        '11427': {'lat': 40.7297, 'lon': -73.7249}, '11428': {'lat': 40.7177, 'lon': -73.7449},
        '11429': {'lat': 40.7087, 'lon': -73.7349}, '11432': {'lat': 40.7147, 'lon': -73.7949},
        '11433': {'lat': 40.6987, 'lon': -73.7949}, '11434': {'lat': 40.6747, 'lon': -73.7749},
        '11435': {'lat': 40.7007, 'lon': -73.8049}, '11436': {'lat': 40.6857, 'lon': -73.7749},
        
        # Bronx ZIP codes (sample - major ones)
        '10451': {'lat': 40.8204, 'lon': -73.9252}, '10452': {'lat': 40.8407, 'lon': -73.9240},
        '10453': {'lat': 40.8518, 'lon': -73.9123}, '10454': {'lat': 40.8088, 'lon': -73.9187},
        '10455': {'lat': 40.8142, 'lon': -73.9089}, '10456': {'lat': 40.8278, 'lon': -73.9098},
        '10457': {'lat': 40.8476, 'lon': -73.9009}, '10458': {'lat': 40.8618, 'lon': -73.8883},
        '10459': {'lat': 40.8238, 'lon': -73.8942}, '10460': {'lat': 40.8418, 'lon': -73.8783},
        '10461': {'lat': 40.8478, 'lon': -73.8353}, '10462': {'lat': 40.8418, 'lon': -73.8604},
        '10463': {'lat': 40.8795, 'lon': -73.9073}, '10464': {'lat': 40.8445, 'lon': -73.7854},
        '10465': {'lat': 40.8265, 'lon': -73.8254}, '10466': {'lat': 40.8895, 'lon': -73.8504},
        '10467': {'lat': 40.8735, 'lon': -73.8783}, '10468': {'lat': 40.8678, 'lon': -73.9004},
        '10469': {'lat': 40.8678, 'lon': -73.8504}, '10470': {'lat': 40.8895, 'lon': -73.8354},
        '10471': {'lat': 40.9045, 'lon': -73.8984}, '10472': {'lat': 40.8298, 'lon': -73.8704},
        '10473': {'lat': 40.8198, 'lon': -73.8504}, '10474': {'lat': 40.8098, 'lon': -73.8904},
        '10475': {'lat': 40.8795, 'lon': -73.8254},
        
        # Staten Island ZIP codes
        '10301': {'lat': 40.6348, 'lon': -74.0776}, '10302': {'lat': 40.6278, 'lon': -74.0987},
        '10303': {'lat': 40.6348, 'lon': -74.0987}, '10304': {'lat': 40.6098, 'lon': -74.0865},
        '10305': {'lat': 40.5898, 'lon': -74.0754}, '10306': {'lat': 40.5698, 'lon': -74.1243},
        '10307': {'lat': 40.5098, 'lon': -74.2443}, '10308': {'lat': 40.5548, 'lon': -74.1654},
        '10309': {'lat': 40.5298, 'lon': -74.2054}, '10310': {'lat': 40.6298, 'lon': -74.1154},
        '10311': {'lat': 40.6098, 'lon': -74.1654}, '10312': {'lat': 40.5548, 'lon': -74.1954},
        '10313': {'lat': 40.5798, 'lon': -74.2054}, '10314': {'lat': 40.5998, 'lon': -74.1654}
    }

def get_zip_coordinates(zip_code):
    """
    Get latitude and longitude coordinates for a given ZIP code
    Args:
        zip_code (str): ZIP code to get coordinates for
    Returns:
        dict: Dictionary with 'lat' and 'lon' keys, or None if not found
    """
    clean_zip = str(zip_code).split('.')[0].split('-')[0].strip()
    return zip_coords.get(clean_zip)

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

def create_dual_zipcode_heatmap(df_para, df_teacher, output_file):
    """
    Create a dual ZIP code heatmap for substitute paraprofessionals and teachers with toggle buttons.
    Args:
        df_para (pd.DataFrame): Paraprofessional data with ZIP codes
        df_teacher (pd.DataFrame): Teacher data with ZIP codes
        output_file (str): Path to save the HTML file
    Returns:
        str: Path to generated HTML file
    """
    import plotly.graph_objects as go
    import plotly.offline as pyo

    # --- Prepare para data ---
    para_zip_counts = df_para['Postal'].value_counts()
    para_lats, para_lons, para_counts, para_zip_codes, para_hover = [], [], [], [], []
    for zip_code, count in para_zip_counts.items():
        coords = get_zip_coordinates(zip_code)
        if coords:
            para_lats.append(coords['lat'])
            para_lons.append(coords['lon'])
            para_counts.append(count)
            para_zip_codes.append(zip_code)
            para_hover.append(f"<b>ZIP Code: {zip_code}</b><br>Paraprofessionals: {count:,}")

    # --- Prepare teacher data ---
    teacher_zip_counts = df_teacher['Postal'].value_counts()
    teacher_lats, teacher_lons, teacher_counts, teacher_zip_codes, teacher_hover = [], [], [], [], []
    for zip_code, count in teacher_zip_counts.items():
        coords = get_zip_coordinates(zip_code)
        if coords:
            teacher_lats.append(coords['lat'])
            teacher_lons.append(coords['lon'])
            teacher_counts.append(count)
            teacher_zip_codes.append(zip_code)
            teacher_hover.append(f"<b>ZIP Code: {zip_code}</b><br>Teachers: {count:,}")

    # --- Create traces ---
    max_para = max(para_counts) if para_counts else 1
    max_teacher = max(teacher_counts) if teacher_counts else 1
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
        text=para_hover,
        hovertemplate='%{text}<extra></extra>',
        visible=True,
        name='Paraprofessionals'
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
        text=teacher_hover,
        hovertemplate='%{text}<extra></extra>',
        visible=False,
        name='Teachers'
    )
    fig = go.Figure(data=[trace_para, trace_teacher])
    fig.update_layout(
        title=dict(
            text="NYC Substitute Distribution by ZIP Code (Heatmap)",
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
        margin=dict(l=0, r=0, t=60, b=0),
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
                # Robustly convert ZIPs to 5-digit strings
                if pd.isna(zip_code):
                    continue
                try:
                    zip_str = str(int(float(zip_code))).zfill(5)
                except Exception:
                    zip_str = str(zip_code).split('.')[0].split('-')[0].strip().zfill(5)
                if zip_str not in ['Unknown', 'nan', 'None', '']:
                    zip_counts[zip_str] = count
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
            else:
                # Optionally, print or log missing ZIPs for debugging
                print(f"[WARN] No coordinates for ZIP: {zip_code}")
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

def create_para_zipcode_heatmap(df_para, output_dir):
    """
    Deprecated: Use create_dual_zipcode_heatmap instead.
    """
    raise NotImplementedError("Use create_dual_zipcode_heatmap for dual heatmap functionality.")

def create_teacher_zipcode_heatmap(df_teacher, output_dir):
    """
    Deprecated: Use create_dual_zipcode_heatmap instead.
    """
    raise NotImplementedError("Use create_dual_zipcode_heatmap for dual heatmap functionality.")

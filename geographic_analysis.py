"""
Geographic Analysis Module for NYC Public Schools Substitute Renewal Analytics
Handles ZIP code mapping, borough analysis, and geographic data processing
"""

import pandas as pd
from geo_data import NYC_ZIP_TO_BOROUGH, ZIP_COORDINATES, AREA_COORDINATES

def map_zip_to_borough(postal_code):
    """
    Map a ZIP code to its corresponding NYC borough or neighboring county
    
    Args:
        postal_code (str): ZIP code
        
    Returns:
        str: Borough/county name or 'Unknown' if not found
    """
    if pd.isna(postal_code) or postal_code in ['nan', 'None', '']:
        return 'Unknown'
    
    # Clean the postal code - convert to string and strip whitespace
    postal_str = str(postal_code).strip().upper()
    
    # Handle common variations
    if postal_str in ['NAN', 'NONE', '', '0', '0.0']:
        return 'Unknown'
    
    # Handle ZIP+4 format (e.g., "10001-1234")
    if '-' in postal_str:
        postal_str = postal_str.split('-')[0]
    
    # Handle decimal format (e.g., "10001.0")
    if '.' in postal_str:
        postal_str = postal_str.split('.')[0]
    
    # Pad with zeros if needed (e.g., "1001" -> "01001")
    if len(postal_str) == 4 and postal_str.isdigit():
        postal_str = '0' + postal_str
    
    if len(postal_str) > 5:
        postal_str = postal_str[:5]
    
    # Only process if it's a valid 5-digit number
    if not (postal_str.isdigit() and len(postal_str) == 5):
        return 'Unknown'
    
    return NYC_ZIP_TO_BOROUGH.get(postal_str, 'Unknown')

def analyze_substitute_data_by_borough(df_para, df_teacher):
    """
    Analyze substitute data by NYC borough and neighboring counties
    
    Args:
        df_para (pd.DataFrame): Paraprofessional data with Borough column
        df_teacher (pd.DataFrame): Teacher data with Borough column
        
    Returns:
        dict: Borough analysis results
    """
    borough_data = {}
    
    # Initialize borough data structure
    boroughs = [
        'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island',
        'Westchester County', 'Nassau County', 'Suffolk County',
        'Bergen County, NJ', 'Hudson County, NJ', 'Union County, NJ',
        'Essex County, NJ', 'Rockland County, NY', 'Fairfield County, CT',
        # Newly added counties/regions
        'Orange County, NY', 'Putnam County, NY', 'Dutchess County, NY', 'Ulster County, NY',
        'Morris County, NJ', 'Passaic County, NJ', 'Somerset County, NJ', 'Middlesex County, NJ',
        'Monmouth County, NJ', 'Ocean County, NJ', 'New Haven County, CT',
        'Pennsylvania',
        'Unknown'
    ]
    
    for borough in boroughs:
        borough_data[borough] = {
            'para_total': 0,
            'para_eligible': 0,
            'para_complete': 0,
            'para_outstanding': 0,
            'teacher_total': 0,
            'teacher_eligible': 0,
            'teacher_complete': 0,
            'teacher_outstanding': 0,
            'para_completion_rate': 0,
            'teacher_completion_rate': 0
        }
    
    # Process paraprofessional data
    if df_para is not None and not df_para.empty:
        print(f"Processing {len(df_para)} paraprofessional records for geographic analysis...")
        
        # Get total counts by borough from ALL data
        para_total_by_borough = df_para.groupby('Borough').size().to_dict()
        print(f"Para totals by area: {para_total_by_borough}")
        
        # Only filter by Status for borough analysis - much simpler
        df_para_eligible = df_para[df_para['Status'].notna()].copy()
        
        print(f"Para records with status: {len(df_para_eligible)}")
        
        # Calculate completion status - just check if Status is 'COMP' vs 'OUT'
        df_para_eligible['Complete'] = (df_para_eligible['Status'] == 'COMP')
        
        # Group by borough
        para_borough_stats = df_para_eligible.groupby('Borough').agg({
            'Empl ID': 'count',
            'Complete': 'sum'
        }).reset_index()
        
        para_borough_stats.columns = ['Borough', 'Total_Eligible', 'Total_Complete']
        para_borough_stats['Total_Outstanding'] = para_borough_stats['Total_Eligible'] - para_borough_stats['Total_Complete']
        
        print(f"Para area stats:\n{para_borough_stats}")
        
        # Update borough data
        for _, row in para_borough_stats.iterrows():
            borough = row['Borough']
            if borough in borough_data:
                borough_data[borough]['para_total'] = para_total_by_borough.get(borough, 0)
                borough_data[borough]['para_eligible'] = row['Total_Eligible']
                borough_data[borough]['para_complete'] = row['Total_Complete']
                borough_data[borough]['para_outstanding'] = row['Total_Outstanding']
                borough_data[borough]['para_completion_rate'] = (
                    row['Total_Complete'] / row['Total_Eligible'] * 100
                    if row['Total_Eligible'] > 0 else 0
                )
    
    # Process teacher data
    if df_teacher is not None and not df_teacher.empty:
        print(f"Processing {len(df_teacher)} teacher records for geographic analysis...")
        
        # Get total counts by borough from ALL data
        teacher_total_by_borough = df_teacher.groupby('Borough').size().to_dict()
        print(f"Teacher totals by area: {teacher_total_by_borough}")
        
        # Only filter by Status for borough analysis - much simpler
        df_teacher_eligible = df_teacher[df_teacher['Status'].notna()].copy()
        
        print(f"Teacher records with status: {len(df_teacher_eligible)}")
        
        # Calculate completion status - just check if Status is 'COMP' vs 'OUT'
        df_teacher_eligible['Complete'] = (df_teacher_eligible['Status'] == 'COMP')
        
        # Group by borough
        teacher_borough_stats = df_teacher_eligible.groupby('Borough').agg({
            'Empl ID': 'count',
            'Complete': 'sum'
        }).reset_index()
        
        teacher_borough_stats.columns = ['Borough', 'Total_Eligible', 'Total_Complete']
        teacher_borough_stats['Total_Outstanding'] = teacher_borough_stats['Total_Eligible'] - teacher_borough_stats['Total_Complete']
        
        print(f"Teacher area stats:\n{teacher_borough_stats}")
        
        # Update borough data
        for _, row in teacher_borough_stats.iterrows():
            borough = row['Borough']
            if borough in borough_data:
                borough_data[borough]['teacher_total'] = teacher_total_by_borough.get(borough, 0)
                borough_data[borough]['teacher_eligible'] = row['Total_Eligible']
                borough_data[borough]['teacher_complete'] = row['Total_Complete']
                borough_data[borough]['teacher_outstanding'] = row['Total_Outstanding']
                borough_data[borough]['teacher_completion_rate'] = (
                    row['Total_Complete'] / row['Total_Eligible'] * 100
                    if row['Total_Eligible'] > 0 else 0
                )
    
    return borough_data

def get_zip_coordinates(zip_code):
    """
    Get latitude and longitude coordinates for a given ZIP code
    
    Args:
        zip_code (str): ZIP code to get coordinates for
        
    Returns:
        dict: Dictionary with 'lat' and 'lon' keys, or None if not found
    """
    # Clean the ZIP code input
    clean_zip = str(zip_code).split('.')[0].split('-')[0].strip()
    
    # Return coordinates if found
    return ZIP_COORDINATES.get(clean_zip)

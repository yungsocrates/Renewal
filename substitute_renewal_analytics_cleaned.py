#!/usr/bin/env python3
"""
NYC Public Schools Substitute Renewal Analytics Dashboard
=========================================================

Comprehensive analytics tool for analyzing substitute teacher and paraprofessional renewal data.
Processes CSV data to generate detailed reports on renewal status, requirements completion,
and eligibility metrics.

Author: HR School Support Analysis Team
Date: July 2025
"""

import pandas as pd
import numpy as np
import os
import re
import time
from datetime import datetime
import warnings

# Plotly imports (temporarily needed for functions not yet moved to modules)
import plotly.offline as pyo
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import geopandas as gpd
from shapely.geometry import shape
from shapely import wkt

# Import our modular components
from data_processing import (
    load_csv_data, 
    analyze_substitute_paraprofessionals,
    analyze_substitute_teachers,
    calculate_differences,
    calculate_percentage_differences,
    calculate_teacher_percentage_differences,
    format_number,
    format_percentage,
    safe_int_conversion
)
from geographic_analysis import (
    map_zip_to_borough,
    get_zip_coordinates,
    analyze_substitute_data_by_borough
)
from visualizations import (
    create_visualization_charts,
    create_nyc_borough_map,
    create_dual_zipcode_heatmap,
    create_zipcode_choropleth_map_dual,
    generate_zipcode_choropleth,
)
from report_generation import (
    generate_html_report,
    generate_comparison_report,
    copy_logo_to_output,
    get_header_html,
    get_professional_footer
)
warnings.filterwarnings('ignore')

# === GLOBAL CONSTANTS ===
RENEWAL_WORKSPACE = r"c:\Users\OFerreira3\Documents\Renewal"
OUTPUT_DIR = os.path.join(RENEWAL_WORKSPACE, "renewal_reports")

# Column mappings based on actual CSV structure
PARA_REQUIREMENTS_COLS = {
    'days_worked': 'Days Wrkd in School Year',
    'reasonable_assurance': 'Reasonable Assurance',
    'status': 'Status',
    'autism_workshop': 'Autism Workshop',
    'suspension_code': 'Suspension Reason Code',
    'child_abuse_workshop': 'Child Abuse Workshop',
    'violence_prevention': 'Violence Prevention Workshop',
    'dasa_workshop': 'DASA Workshop',
    'subhub_training': 'SubHub Training',
    'processing_fee': 'Processing Fee',
    'state_exam': 'State Exam'
}

TEACHER_REQUIREMENTS_COLS = {
    'days_worked': 'Days Wrkd in School Year',
    'reasonable_assurance': 'Reasonable Assurance',
    'status': 'Status',
    'autism_workshop': 'Autism Workshop',
    'suspension_code': 'Suspension Reason Code',
    'certified': 'Certified',
    'child_abuse_workshop': 'Child Abuse Workshop',
    'violence_prevention': 'Violence Prevention Workshop',
    'dasa_workshop': 'DASA Workshop',
    'subhub_training': 'SubHub Training',
    'processing_fee': 'Processing Fee',
    'state_exam': 'State Exam',
    'teach_profile': 'TEACH Profile',
    'bachelor_degree': 'Bachelor Degree',
    'high_school_diploma': 'High School Diploma'
}

def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("NYC Public Schools Substitute Renewal Analytics Dashboard")
    print("=" * 60)
    
    # Set up paths for current (new) data
    para_csv_path = os.path.join(RENEWAL_WORKSPACE, "substitute_paraprofessionals.csv")
    teacher_csv_path = os.path.join(RENEWAL_WORKSPACE, "substitute_teachers.csv")
    
    # Set up paths for old data (with "_old" suffix)
    para_old_csv_path = os.path.join(RENEWAL_WORKSPACE, "substitute_paraprofessionals_old.csv")
    teacher_old_csv_path = os.path.join(RENEWAL_WORKSPACE, "substitute_teachers_old.csv")
    
    try:
        # Create output directory and copy logo
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        copy_logo_to_output(OUTPUT_DIR)
        
        # Check if CSV files exist
        if not os.path.exists(para_csv_path):
            print(f"Warning: Paraprofessional CSV not found at {para_csv_path}")
            print("Please place the substitute paraprofessional CSV file in the Renewal directory")
            
        if not os.path.exists(teacher_csv_path):
            print(f"Warning: Teacher CSV not found at {teacher_csv_path}")
            print("Please place the substitute teacher CSV file in the Renewal directory")
            
        # Check for old data files
        has_old_para = os.path.exists(para_old_csv_path)
        has_old_teacher = os.path.exists(teacher_old_csv_path)
        
        if has_old_para or has_old_teacher:
            print(f"\n📊 Comparison Mode: Old data files detected")
            print(f"  Para Old Data: {'✓' if has_old_para else '❌'}")
            print(f"  Teacher Old Data: {'✓' if has_old_teacher else '❌'}")
        else:
            print(f"\n📊 Standard Mode: No old data files found for comparison")
        
        # Initialize results dictionaries
        para_results = {}
        teacher_results = {}
        para_old_results = {}
        teacher_old_results = {}
        
        # Load and analyze current paraprofessional data
        if os.path.exists(para_csv_path):
            print("\nAnalyzing Current Substitute Paraprofessional Data...")
            df_para = load_csv_data(para_csv_path, "para (current)")
            # Ensure Postal column is string type before mapping
            df_para['Postal'] = df_para['Postal'].astype(str)
            
            # Debug ZIP code analysis
            print(f"DEBUG: Sample ZIP codes from para data:")
            print(f"  First 10 ZIP codes: {df_para['Postal'].head(10).tolist()}")
            print(f"  ZIP code value counts (top 10): {df_para['Postal'].value_counts().head(10).to_dict()}")
            print(f"  Unique ZIP codes: {len(df_para['Postal'].unique())}")
            
            # Add Borough column based on ZIP code mapping
            df_para['Borough'] = df_para['Postal'].apply(map_zip_to_borough)
            
            # Debug borough mapping
            borough_counts = df_para['Borough'].value_counts()
            print(f"  Borough distribution: {borough_counts.to_dict()}")
            
            print(f"✓ Added Borough mapping to {len(df_para)} paraprofessional records")
            para_results = analyze_substitute_paraprofessionals(df_para)
            print("✓ Current paraprofessional analysis completed")
        else:
            print("⚠ Skipping current paraprofessional analysis - CSV file not found")
            df_para = None
            # Initialize with default values
            para_results = {key: 0 for key in [
                'total_eligible', 'total_complete', 'total_outstanding', 'ra_not_complete',
                'ra_complete_other_outstanding', 'days_worked_only', 'atas_only',
                'child_abuse_workshop_only', 'days_and_other_requirements', 'total_suspended_2ss',
                'total_suspended_2sr'
            ]}
        
        # Load and analyze old paraprofessional data if available
        if has_old_para:
            print("\nAnalyzing Old Substitute Paraprofessional Data...")
            df_para_old = load_csv_data(para_old_csv_path, "para (old)")
            para_old_results = analyze_substitute_paraprofessionals(df_para_old)
            print("✓ Old paraprofessional analysis completed")
        else:
            print("⚠ No old paraprofessional data available for comparison")
            para_old_results = {key: 0 for key in para_results.keys()}
        
        # Load and analyze current teacher data
        if os.path.exists(teacher_csv_path):
            print("\nAnalyzing Current Substitute Teacher Data...")
            df_teacher = load_csv_data(teacher_csv_path, "teacher (current)")
            # Ensure Postal column is string type before mapping
            df_teacher['Postal'] = df_teacher['Postal'].astype(str)
            
            # Debug ZIP code analysis
            print(f"DEBUG: Sample ZIP codes from teacher data:")
            print(f"  First 10 ZIP codes: {df_teacher['Postal'].head(10).tolist()}")
            print(f"  ZIP code value counts (top 10): {df_teacher['Postal'].value_counts().head(10).to_dict()}")
            print(f"  Unique ZIP codes: {len(df_teacher['Postal'].unique())}")
            
            # Add Borough column based on ZIP code mapping
            df_teacher['Borough'] = df_teacher['Postal'].apply(map_zip_to_borough)
            
            # Debug borough mapping
            borough_counts = df_teacher['Borough'].value_counts()
            print(f"  Borough distribution: {borough_counts.to_dict()}")
            
            print(f"✓ Added Borough mapping to {len(df_teacher)} teacher records")
            teacher_results = analyze_substitute_teachers(df_teacher)
            print("✓ Current teacher analysis completed")
        else:
            print("⚠ Skipping current teacher analysis - CSV file not found")
            df_teacher = None
            # Initialize with default values
            teacher_results = {key: 0 for key in [
                'total_eligible', 'total_prc_pru_eligible', 'total_prc_pru_complete',
                'total_prc_pru_outstanding', 'prc_pru_ra_not_complete', 'prc_pru_met_ra_other_outstanding',
                'prc_pru_days_worked_only', 'prc_pru_child_abuse_workshop_only', 'prc_pru_other_requirements_only',
                'prc_pru_days_and_other_requirements', 'total_teachers_on_leave', 'total_retirees',
                'total_prr_complete', 'total_prr_outstanding', 'total_suspended_2ss', 'total_suspended_2sr'
            ]}
        
        # Load and analyze old teacher data if available
        if has_old_teacher:
            print("\nAnalyzing Old Substitute Teacher Data...")
            df_teacher_old = load_csv_data(teacher_old_csv_path, "teacher (old)")
            teacher_old_results = analyze_substitute_teachers(df_teacher_old)
            print("✓ Old teacher analysis completed")
        else:
            print("⚠ No old teacher data available for comparison")
            teacher_old_results = {key: 0 for key in teacher_results.keys()}
        
        # Calculate differences
        para_differences = calculate_differences(para_results, para_old_results)
        teacher_differences = calculate_differences(teacher_results, teacher_old_results)
        
        # Calculate percentage differences for completion rates
        para_percentage_differences = calculate_percentage_differences(para_results, para_old_results)
        teacher_percentage_differences = calculate_teacher_percentage_differences(teacher_results, teacher_old_results)
        
        # Create visualizations
        print("\nGenerating Visualizations...")
        chart_files = create_visualization_charts(para_results, teacher_results, OUTPUT_DIR)
        print("✓ Visualization charts created")
        
        # Generate borough analysis and map
        print("\nGenerating Borough Analysis...")
        borough_data = analyze_substitute_data_by_borough(df_para, df_teacher)
        try:
            borough_map_file = create_nyc_borough_map(borough_data, OUTPUT_DIR)
            print(f"✓ Borough map generated: {borough_map_file}")
        except Exception as e:
            print(f"⚠ Borough map generation failed: {str(e)}")
            borough_map_file = None
        
        # Generate ZIP code choropleth map
        print("\nGenerating ZIP Code Choropleth Map...")
        try:
            generate_zipcode_choropleth()
        except Exception as e:
            print(f"⚠ ZIP Code Choropleth Map generation failed: {str(e)}")
        
        # Generate HTML report with differences
        print("\nGenerating HTML Report...")
        has_comparison_data = (has_old_para or has_old_teacher)
        report_file = generate_html_report(
            para_results, teacher_results, 
            para_differences, teacher_differences,
            para_percentage_differences, teacher_percentage_differences,
            chart_files, OUTPUT_DIR,
            has_comparison=has_comparison_data,
            para_old_results=para_old_results, 
            teacher_old_results=teacher_old_results
        )
        print(f"✓ HTML report generated: {report_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Substitute Paraprofessionals:")
        print(f"  • Total Eligible: {format_number(para_results.get('total_eligible', 0))}" + 
              (f" ({para_differences.get('total_eligible', '0')})" if has_comparison_data and para_differences.get('total_eligible', '0') != '0' else ""))
        print(f"  • Completed: {format_number(para_results.get('total_complete', 0))}" + 
              (f" ({para_differences.get('total_complete', '0')})" if has_comparison_data and para_differences.get('total_complete', '0') != '0' else ""))
        print(f"  • Outstanding: {format_number(para_results.get('total_outstanding', 0))}" + 
              (f" ({para_differences.get('total_outstanding', '0')})" if has_comparison_data and para_differences.get('total_outstanding', '0') != '0' else ""))
        
        # Calculate and display completion rate
        para_completion_rate = (para_results.get('total_complete', 0) / max(para_results.get('total_eligible', 1), 1) * 100)
        completion_rate_text = f"  • Completion Rate: {format_percentage(para_completion_rate)}"
        if has_comparison_data and para_percentage_differences.get('spa_completion_rate', '0%') != '0%':
            completion_rate_text += f" ({para_percentage_differences.get('spa_completion_rate', '0%')})"
        print(completion_rate_text)
        
        print(f"\nSubstitute Teachers:")
        print(f"  • Total Eligible: {format_number(teacher_results.get('total_eligible', 0))}" + 
              (f" ({teacher_differences.get('total_eligible', '0')})" if has_comparison_data and teacher_differences.get('total_eligible', '0') != '0' else ""))
        print(f"  • PRC/PRU Eligible: {format_number(teacher_results.get('total_prc_pru_eligible', 0))}" + 
              (f" ({teacher_differences.get('total_prc_pru_eligible', '0')})" if has_comparison_data and teacher_differences.get('total_prc_pru_eligible', '0') != '0' else ""))
        print(f"  • PRC/PRU Completed: {format_number(teacher_results.get('total_prc_pru_complete', 0))}" + 
              (f" ({teacher_differences.get('total_prc_pru_complete', '0')})" if has_comparison_data and teacher_differences.get('total_prc_pru_complete', '0') != '0' else ""))
        
        # Calculate and display completion rate
        teacher_completion_rate = (teacher_results.get('total_prc_pru_complete', 0) / max(teacher_results.get('total_prc_pru_eligible', 1), 1) * 100)
        teacher_completion_rate_text = f"  • PRC/PRU Completion Rate: {format_percentage(teacher_completion_rate)}"
        if has_comparison_data and teacher_percentage_differences.get('ste_completion_rate', '0%') != '0%':
            teacher_completion_rate_text += f" ({teacher_percentage_differences.get('ste_completion_rate', '0%')})"
        print(teacher_completion_rate_text)
        
        if has_comparison_data:
            print(f"\n📊 Comparison Summary:")
            print(f"  • Old data files processed for comparison analysis")
            print(f"  • Differences shown with +/- indicators in report and summary")
        
        print(f"\nOutput Files:")
        print(f"  • Main Report: {report_file}")
        print(f"  • Charts Directory: {OUTPUT_DIR}")
        print(f"  • Charts: {', '.join([os.path.basename(f) for f in chart_files])}")
        if borough_map_file:
            print(f"  • Borough Map: {borough_map_file}")
        
        # Print borough summary
        print(f"\n🗺️  Geographic Distribution Summary:")
        total_para_eligible = sum(borough_data[b]['para_eligible'] for b in borough_data if b != 'Unknown')
        total_teacher_eligible = sum(borough_data[b]['teacher_eligible'] for b in borough_data if b != 'Unknown')
        
        # NYC Boroughs first
        print(f"  NYC Boroughs:")
        for borough in ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']:
            if borough in borough_data:
                data = borough_data[borough]
                if data['para_eligible'] > 0 or data['teacher_eligible'] > 0:
                    print(f"    • {borough}:")
                    if data['para_eligible'] > 0:
                        print(f"      - Paras: {data['para_eligible']:,} eligible ({data['para_completion_rate']:.1f}% complete)")
                    if data['teacher_eligible'] > 0:
                        print(f"      - Teachers: {data['teacher_eligible']:,} eligible ({data['teacher_completion_rate']:.1f}% complete)")
        
        # Neighboring Counties
        neighboring_counties = ['Westchester County', 'Nassau County', 'Suffolk County', 
                               'Bergen County, NJ', 'Hudson County, NJ', 'Union County, NJ', 
                               'Essex County, NJ', 'Rockland County, NY', 'Fairfield County, CT']
        
        counties_with_data = []
        for county in neighboring_counties:
            if county in borough_data:
                data = borough_data[county]
                if data['para_eligible'] > 0 or data['teacher_eligible'] > 0:
                    counties_with_data.append(county)
        
        if counties_with_data:
            print(f"  Neighboring Counties:")
            for county in counties_with_data:
                data = borough_data[county]
                print(f"    • {county}:")
                if data['para_eligible'] > 0:
                    print(f"      - Paras: {data['para_eligible']:,} eligible ({data['para_completion_rate']:.1f}% complete)")
                if data['teacher_eligible'] > 0:
                    print(f"      - Teachers: {data['teacher_eligible']:,} eligible ({data['teacher_completion_rate']:.1f}% complete)")
        
        if borough_data.get('Unknown', {}).get('para_eligible', 0) > 0 or borough_data.get('Unknown', {}).get('teacher_eligible', 0) > 0:
            unknown_data = borough_data['Unknown']
            print(f"  Unknown/Other Areas:")
            if unknown_data['para_eligible'] > 0:
                print(f"    - Paras: {unknown_data['para_eligible']:,} eligible ({unknown_data['para_completion_rate']:.1f}% complete)")
            if unknown_data['teacher_eligible'] > 0:
                print(f"    - Teachers: {unknown_data['teacher_eligible']:,} eligible ({unknown_data['teacher_completion_rate']:.1f}% complete)")
        
        print("\n✓ Analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error occurred during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

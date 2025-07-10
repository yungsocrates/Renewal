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
    format_percentage
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
    create_zipcode_choropleth_map_dual
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

def format_number(x):
    """Format numbers with commas"""
    return f"{int(x):,}" if pd.notna(x) and isinstance(x, (int, float)) else str(x)

def format_percentage(x):
    """Format percentages"""
    return f"{x:.1f}%" if isinstance(x, (int, float)) else str(x)

def safe_int_conversion(value):
    """Safely convert values to integer"""
    try:
        if pd.isna(value):
            return 0
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def load_csv_data(csv_path, data_type="para"):
    """
    Load and validate CSV data
    
    Args:
        csv_path (str): Path to CSV file
        data_type (str): Either 'para' or 'teacher'
    
    Returns:
        pd.DataFrame: Processed DataFrame
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"Loading {data_type} data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Basic data validation
    print(f"Loaded {len(df)} records")
    print(f"Columns found: {list(df.columns)}")
    
    return df

def analyze_substitute_paraprofessionals(df_para):
    """
    Analyze substitute paraprofessional renewal data
    
    Args:
        df_para (pd.DataFrame): Paraprofessional data
        
    Returns:
        dict: Analysis results
    """
    results = {}
    
    # Print actual columns and some sample values to help with debugging
    print(f"=== RAW DATA DEBUG ===")
    print(f"Original CSV rows: {len(df_para)}")
    print(f"Available columns: {list(df_para.columns)}")
    
    # Check for empty/null rows
    null_status_count = df_para['Status'].isnull().sum()
    empty_status_count = (df_para['Status'] == '').sum()
    print(f"Null Status values: {null_status_count}")
    print(f"Empty Status values: {empty_status_count}")
    
    # Check actual data content
    print(f"\nSample Status values (including nulls): {df_para['Status'].value_counts(dropna=False)}")
    print(f"Sample RA values (including nulls): {df_para['Reasonable Assurance'].value_counts(dropna=False)}")
    
    # Check for completely empty rows
    completely_empty_rows = df_para.isnull().all(axis=1).sum()
    print(f"Completely empty rows: {completely_empty_rows}")
    
    # Check rows with meaningful data (non-null Status and at least one other field)
    meaningful_rows = df_para[df_para['Status'].notna() & (df_para['Status'] != '')].copy()
    print(f"Rows with non-null, non-empty Status: {len(meaningful_rows)}")
    
    # Check for the problematic statuses we want to exclude
    if 'Staffing Status' in df_para.columns:
        print(f"Staffing Status values: {df_para['Staffing Status'].value_counts()}")
        excluded_count = len(df_para[df_para['Staffing Status'].isin(['Pending Termination for FT', 'Active 5BA/5BP'])])
        print(f"Records to exclude based on Staffing Status: {excluded_count}")
    else:
        print("No 'Staffing Status' column found")
    
    # Check Status column for exclusions
    status_excluded_count = len(df_para[df_para['Status'].isin(['Pending Term for FT', 'Pending Termination for FT'])])
    print(f"Records to exclude based on Status: {status_excluded_count}")
    print(f"=== END RAW DATA DEBUG ===\n")
    
    # For paraprofessionals, we'll work with only meaningful records
    # First, filter out empty/null status rows and convert to uppercase
    df_para_clean = df_para.copy()
    
    # Remove rows with null, empty, or meaningless Status values
    df_para_clean = df_para_clean[
        (df_para_clean['Status'].notna()) & 
        (df_para_clean['Status'] != '') & 
        (df_para_clean['Status'].astype(str).str.strip() != '') &
        (df_para_clean['Status'].astype(str).str.strip().str.upper() != 'NAN')
    ].copy()
    
    print(f"After removing null/empty Status rows: {len(df_para_clean)} records")
    
    df_para_clean['Status'] = df_para_clean['Status'].astype(str).str.strip().str.upper()
    
    # Filter out terminated or inactive records and specific statuses
    # Remove "Pending Termination for FT" and "Active 5BA/5BP" if they exist in staffing status
    if 'Staffing Status' in df_para_clean.columns:
        excluded_statuses = ['Pending Termination for FT', 'Active 5BA/5BP']
        active_df = df_para_clean[
            ~df_para_clean['Staffing Status'].isin(excluded_statuses)
        ].copy()
    else:
        active_df = df_para_clean.copy()
    
    # Also exclude specific Status values
    excluded_status_values = ['Pending Term for FT', 'Pending Termination for FT']
    active_df = active_df[
        ~active_df['Status'].str.upper().isin([s.upper() for s in excluded_status_values])
    ].copy()
    
    print(f"After applying all filters: {len(active_df)} records")
    
    # Determine completion status based on Status column
    # Status column: Out = outstanding, COMPL = complete (based on actual data)
    def get_completion_status(row):
        """Get completion status from Status column"""
        status = str(row.get('Status', '')).strip()
        if status.upper() in ['COMPL', 'COMP', 'COMPLETE']:
            return 'Complete'
        elif status.upper() in ['OUT', 'OUTSTANDING']:
            return 'Outstanding'
        else:
            # For any other status, consider it outstanding by default
            return 'Outstanding'
    
    # Apply completion status based on Status column
    active_df = active_df.copy()
    active_df['computed_status'] = active_df.apply(get_completion_status, axis=1)
    
    # Basic counts - treating all records as eligible for renewal
    results['total_eligible'] = len(active_df)
    results['total_complete'] = len(active_df[active_df['computed_status'] == 'Complete'])
    results['total_outstanding'] = len(active_df[active_df['computed_status'] == 'Outstanding'])
    
    print(f"\nBasic counts - Eligible: {results['total_eligible']}, Complete: {results['total_complete']}, Outstanding: {results['total_outstanding']}")
    
    # Helper function to check if requirement is complete
    def is_requirement_complete(value):
        """Check if a requirement value indicates completion"""
        if pd.isna(value):
            return False
        value_str = str(value).strip().upper()
        completed_indicators = ['COMPLETE', 'PASSED', 'YES', 'PAID', 'PASSING', 'PASS', 'COMPL', 'Y', 'EXEMPT']
        return value_str in completed_indicators
    
    # Helper function to check if requirement is incomplete/outstanding
    def is_requirement_outstanding(value):
        """Check if a requirement value indicates it's outstanding"""
        if pd.isna(value):
            return True
        value_str = str(value).strip().upper()
        outstanding_indicators = ['NOT COMPLETE', 'NOT REQUIRED', 'REGISTERED', 'NO', 'OUTSTANDING', 'LETTER SENT', 'OUT', 'N']
        return value_str in outstanding_indicators or value_str == ''
    
    # Reasonable Assurance Analysis - based on actual data values
    ra_not_complete = active_df[
        (active_df.get('Reasonable Assurance', '').astype(str).str.strip().str.upper() == 'LETTER SENT') |
        (active_df.get('Reasonable Assurance', '').astype(str).str.strip().str.upper() == 'NOT COMPLETE')
    ]
    results['ra_not_complete'] = len(ra_not_complete)
    
    # RA Complete group (those who have met RA requirement)
    # Include both "COMPLETE" and "Letter Not Sent" as complete values
    ra_complete_group = active_df[
        active_df.get('Reasonable Assurance', '').astype(str).str.strip().str.upper().isin(['COMPLETE', 'LETTER NOT SENT'])
    ].copy()
    
    outstanding_with_ra_complete = ra_complete_group[ra_complete_group['computed_status'] == 'Outstanding']
    results['ra_complete_other_outstanding'] = len(outstanding_with_ra_complete)
    
    print(f"RA Analysis - RA Not Complete: {results['ra_not_complete']}, RA Complete but Other Outstanding: {results['ra_complete_other_outstanding']}")
    
    # Days Worked Analysis
    if not ra_complete_group.empty:
        ra_complete_group.loc[:, 'days_worked_int'] = ra_complete_group.get('Days Wrkd in School Year', 0).apply(safe_int_conversion)
        
        # Days Worked Only (≤19 days, other requirements met)
        days_only_candidates = ra_complete_group[
            (ra_complete_group['days_worked_int'] <= 19) &
            (ra_complete_group['computed_status'] == 'Outstanding')
        ]
        
        # Check if most other requirements are complete for days-only candidates
        days_only_with_other_reqs_met = []
        for _, row in days_only_candidates.iterrows():
            # Check major requirements (excluding NOT REQUIRED ones)
            requirements_to_check = [
                ('Child Abuse Workshop', row.get('Child Abuse Workshop', '')),
                ('Violence Prevention Workshop', row.get('Violence Prevention Workshop', '')),
                ('DASA Workshop', row.get('DASA Workshop', '')),
                ('SubHub Training', row.get('SubHub Training', '')),
                ('State Exam', row.get('State Exam', '')),
                ('Autism Workshop', row.get('Autism Workshop', ''))
            ]
            
            # Count requirements that are actually required and complete
            required_and_complete = 0
            required_count = 0
            
            for req_name, req_value in requirements_to_check:
                req_str = str(req_value).strip().upper()
                if req_str != 'NOT REQUIRED':  # Only count actually required items
                    required_count += 1
                    if is_requirement_complete(req_value):
                        required_and_complete += 1
            
            # If most required items are complete, this is a "days only" case
            if required_count > 0 and (required_and_complete / required_count) >= 0.8:
                days_only_with_other_reqs_met.append(row)
        
        results['days_worked_only'] = len(days_only_with_other_reqs_met)
        
        # Child Abuse Workshop Only (≥20 days, only Child Abuse Workshop incomplete)
        child_abuse_only_candidates = ra_complete_group[
            (ra_complete_group['days_worked_int'] >= 20) &
            (ra_complete_group['computed_status'] == 'Outstanding')
        ]
        
        child_abuse_only_filtered = []
        for _, row in child_abuse_only_candidates.iterrows():
            child_abuse_incomplete = is_requirement_outstanding(row.get('Child Abuse Workshop', ''))
            
            # Check if other major requirements are complete
            other_reqs = [
                row.get('Violence Prevention Workshop', ''),
                row.get('DASA Workshop', ''),
                row.get('SubHub Training', ''),
                row.get('State Exam', ''),
                row.get('Autism Workshop', '')
            ]
            
            other_complete_count = sum(1 for req in other_reqs 
                                     if str(req).strip().upper() != 'NOT REQUIRED' and is_requirement_complete(req))
            other_required_count = sum(1 for req in other_reqs 
                                     if str(req).strip().upper() != 'NOT REQUIRED')
            
            # If child abuse is incomplete but most others are complete
            if child_abuse_incomplete and other_required_count > 0 and (other_complete_count / other_required_count) >= 0.8:
                child_abuse_only_filtered.append(row)
        
        results['child_abuse_workshop_only'] = len(child_abuse_only_filtered)
        
        # State Exam as ATAS equivalent for paraprofessionals
        atas_only_candidates = ra_complete_group[
            (ra_complete_group['days_worked_int'] >= 20) &
            (ra_complete_group['computed_status'] == 'Outstanding')
        ]
        
        atas_only_filtered = []
        for _, row in atas_only_candidates.iterrows():
            state_exam_incomplete = is_requirement_outstanding(row.get('State Exam', ''))
            
            # Check if other major requirements are complete
            other_reqs = [
                row.get('Child Abuse Workshop', ''),
                row.get('Violence Prevention Workshop', ''),
                row.get('DASA Workshop', ''),
                row.get('SubHub Training', ''),
                row.get('Autism Workshop', '')
            ]
            
            other_complete_count = sum(1 for req in other_reqs 
                                     if str(req).strip().upper() != 'NOT REQUIRED' and is_requirement_complete(req))
            other_required_count = sum(1 for req in other_reqs 
                                     if str(req).strip().upper() != 'NOT REQUIRED')
            
            # If state exam is incomplete but most others are complete
            if state_exam_incomplete and other_required_count > 0 and (other_complete_count / other_required_count) >= 0.8:
                atas_only_filtered.append(row)
        
        results['atas_only'] = len(atas_only_filtered)
        
        # Days & Other Requirements (≤19 days, multiple requirements not complete)
        days_and_others = ra_complete_group[
            (ra_complete_group['days_worked_int'] <= 19) &
            (ra_complete_group['computed_status'] == 'Outstanding')
        ]
        
        # Filter for those with multiple incomplete requirements
        days_and_multiple_incomplete = []
        for _, row in days_and_others.iterrows():
            requirements_to_check = [
                row.get('Child Abuse Workshop', ''),
                row.get('Violence Prevention Workshop', ''),
                row.get('DASA Workshop', ''),
                row.get('SubHub Training', ''),
                row.get('State Exam', ''),
                row.get('Autism Workshop', '')
            ]
            
            incomplete_count = 0
            required_count = 0
            
            for req in requirements_to_check:
                req_str = str(req).strip().upper()
                if req_str != 'NOT REQUIRED':  # Only count actually required items
                    required_count += 1
                    if is_requirement_outstanding(req):
                        incomplete_count += 1
            
            # If multiple requirements are incomplete
            if incomplete_count >= 2:
                days_and_multiple_incomplete.append(row)
        
        results['days_and_other_requirements'] = len(days_and_multiple_incomplete)
    else:
        results.update({
            'days_worked_only': 0,
            'atas_only': 0,
            'child_abuse_workshop_only': 0,
            'days_and_other_requirements': 0
        })
    
    print(f"Detailed Analysis - Days Only: {results['days_worked_only']}, Child Abuse Only: {results['child_abuse_workshop_only']}, ATAS Only: {results['atas_only']}, Days & Others: {results['days_and_other_requirements']}")
    
    # Suspension Analysis - using the same filtered dataset as other calculations
    results['total_suspended_2ss'] = len(active_df[active_df.get('Suspension Reason Code', '').astype(str).str.strip() == '2SS'])
    results['total_suspended_2sr'] = len(active_df[active_df.get('Suspension Reason Code', '').astype(str).str.strip() == '2SR'])
    
    print(f"Suspension Analysis - 2SS: {results['total_suspended_2ss']}, 2SR: {results['total_suspended_2sr']}")
    print(f"Final count verification - Total rows in filtered dataset: {len(active_df)}, Total eligible reported: {results['total_eligible']}")
    
    return results

def analyze_substitute_teachers(df_teacher):
    """
    Analyze substitute teacher renewal data
    
    Args:
        df_teacher (pd.DataFrame): Teacher data
        
    Returns:
        dict: Analysis results
    """
    results = {}
    
    # Print actual columns to help with debugging
    print(f"Available teacher columns: {list(df_teacher.columns)}")
    
    # Filter out specific statuses including "Pending Termination for FT" and "Active 5BA/5BP"
    excluded_statuses = ['Pending Term for FT', 'Pending Termination for FT']
    df_filtered = df_teacher[~df_teacher.get('Status', '').isin(excluded_statuses)].copy()
    
    # Also filter by Staffing Status if column exists
    if 'Staffing Status' in df_teacher.columns:
        excluded_staffing_statuses = ['Pending Termination for FT', 'Active 5BA/5BP']
        df_filtered = df_filtered[~df_filtered.get('Staffing Status', '').isin(excluded_staffing_statuses)].copy()
    
    # For teachers, we'll work with all active records
    eligible_df = df_filtered[df_filtered['Status'].notna()].copy()
    
    # Determine completion status based on Status column
    # Status column: Out = outstanding, COMPL = complete (based on actual data)
    def get_teacher_completion_status(row):
        """Get completion status from Status column"""
        status = str(row.get('Status', '')).strip()
        if status.upper() in ['COMPL', 'COMP', 'COMPLETE']:
            return 'Complete'
        elif status.upper() in ['OUT', 'OUTSTANDING']:
            return 'Outstanding'
        else:
            # For any other status, consider it outstanding by default
            return 'Outstanding'
    
    # Apply completion status based on Status column
    eligible_df = eligible_df.copy()
    eligible_df['computed_status'] = eligible_df.apply(get_teacher_completion_status, axis=1)
    
    results['total_eligible'] = len(eligible_df)
    
    # PRC & PRU Analysis - using Certified column
    # PRC = Certified column is 'Y' (Yes, certified teachers)
    # PRU = Certified column is 'N' (No, uncertified teachers)
    # Exclude special categories like 'Retiree' and 'On Leave' from this analysis
    prc_teachers = eligible_df[
        (eligible_df.get('Certified', '') == 'Y') &
        (~eligible_df.get('Renewal Classification', '').isin(['Retiree', 'On Leave']))
    ].copy()
    
    pru_teachers = eligible_df[
        (eligible_df.get('Certified', '') == 'N') &
        (~eligible_df.get('Renewal Classification', '').isin(['Retiree', 'On Leave']))
    ].copy()
    
    prc_pru_eligible = pd.concat([prc_teachers, pru_teachers], ignore_index=True)
    
    results['total_prc_pru_eligible'] = len(prc_pru_eligible)
    results['total_prc_pru_complete'] = len(
        prc_pru_eligible[prc_pru_eligible['computed_status'] == 'Complete']
    )
    results['total_prc_pru_outstanding'] = len(
        prc_pru_eligible[prc_pru_eligible['computed_status'] == 'Outstanding']
    )
    
    # PRC & PRU - RA Analysis
    prc_pru_ra_not_complete = prc_pru_eligible[
        (prc_pru_eligible.get('Reasonable Assurance', '').astype(str).str.contains('Letter Sent', na=False)) |
        (prc_pru_eligible.get('Reasonable Assurance', '').astype(str).str.strip().str.upper() == 'NOT COMPLETE')
    ]
    results['prc_pru_ra_not_complete'] = len(prc_pru_ra_not_complete)
    
    # PRC & PRU - Met RA, Other Requirements Outstanding
    prc_pru_ra_complete = prc_pru_eligible[
        prc_pru_eligible.get('Reasonable Assurance', '').isin(['COMPLETE', 'Letter Not Sent', 'PASSED'])
    ].copy()
    results['prc_pru_met_ra_other_outstanding'] = len(
        prc_pru_ra_complete[prc_pru_ra_complete['computed_status'] == 'Outstanding']
    )
    
    # Days and requirements analysis for PRC & PRU
    if not prc_pru_ra_complete.empty:
        prc_pru_ra_complete.loc[:, 'days_worked_int'] = prc_pru_ra_complete.get('Days Wrkd in School Year', 0).apply(safe_int_conversion)
        
        # Days Worked Only (≤19 days, other requirements passing)
        days_only = prc_pru_ra_complete[
            (prc_pru_ra_complete['days_worked_int'] <= 19) &
            (prc_pru_ra_complete['computed_status'] == 'Outstanding')
        ]
        
        # Check if other requirements are mostly complete
        days_only_filtered = []
        for _, row in days_only.iterrows():
            other_reqs = [
                row.get('Child Abuse Workshop', ''),
                row.get('Violence Prevention Workshop', ''),
                row.get('DASA Workshop', ''),
                row.get('SubHub Training', ''),
                row.get('TEACH Profile', ''),
                row.get('Bachelor Degree', ''),
                row.get('Autism Workshop', '')
            ]
            
            # Count actually required and completed items
            completed_count = 0
            required_count = 0
            
            for req in other_reqs:
                req_str = str(req).strip().upper()
                if req_str not in ['NOT REQUIRED', 'NAN', '']:  # Only count actually required items
                    required_count += 1
                    if req_str in ['COMPLETE', 'PASSED', 'EXEMPT', 'Y']:
                        completed_count += 1
            
            # If most requirements are complete (80% or more)
            if required_count > 0 and (completed_count / required_count) >= 0.8:
                days_only_filtered.append(row)
        
        results['prc_pru_days_worked_only'] = len(days_only_filtered)
        
        # Child Abuse Workshop Only (≥20 days, Child Abuse Workshop not complete)
        child_abuse_only = prc_pru_ra_complete[
            (prc_pru_ra_complete['days_worked_int'] >= 20) &
            (prc_pru_ra_complete.get('Child Abuse Workshop', '').astype(str).str.strip().str.upper() == 'NOT COMPLETE') &
            (prc_pru_ra_complete['computed_status'] == 'Outstanding')
        ]
        results['prc_pru_child_abuse_workshop_only'] = len(child_abuse_only)
        
        # Other Requirements Only (≥20 days, other requirements not complete)
        other_requirements_only = prc_pru_ra_complete[
            (prc_pru_ra_complete['days_worked_int'] >= 20) &
            (prc_pru_ra_complete['computed_status'] == 'Outstanding')
        ]
        
        # Filter for those with other incomplete requirements (not just Autism)
        other_only_filtered = []
        for _, row in other_requirements_only.iterrows():
            autism_complete = str(row.get('Autism Workshop', '')).strip().upper() == 'COMPLETE'
            
            if autism_complete:  # Autism is complete, check others
                other_reqs = [
                    row.get('Child Abuse Workshop', ''),
                    row.get('Violence Prevention Workshop', ''),
                    row.get('DASA Workshop', ''),
                    row.get('SubHub Training', ''),
                    row.get('TEACH Profile', ''),
                    row.get('Bachelor Degree', '')
                ]
                
                incomplete_count = 0
                for req in other_reqs:
                    req_str = str(req).strip().upper()
                    if req_str not in ['COMPLETE', 'PASSED', 'EXEMPT', 'Y', 'NOT REQUIRED', 'NAN', '']:
                        incomplete_count += 1
                
                if incomplete_count >= 1:
                    other_only_filtered.append(row)
        
        results['prc_pru_other_requirements_only'] = len(other_only_filtered)
        
        # Days & Other Requirements (≤19 days, multiple requirements not complete)
        days_and_others = prc_pru_ra_complete[
            (prc_pru_ra_complete['days_worked_int'] <= 19) &
            (prc_pru_ra_complete['computed_status'] == 'Outstanding')
        ]
        
        days_and_others_filtered = []
        for _, row in days_and_others.iterrows():
            incomplete_reqs = [
                row.get('Child Abuse Workshop', ''),
                row.get('Violence Prevention Workshop', ''),
                row.get('DASA Workshop', ''),
                row.get('SubHub Training', ''),
                row.get('Autism Workshop', ''),
                row.get('TEACH Profile', ''),
                row.get('Bachelor Degree', '')
            ]
            
            incomplete_count = 0
            for req in incomplete_reqs:
                req_str = str(req).strip().upper()
                if req_str not in ['COMPLETE', 'PASSED', 'EXEMPT', 'Y', 'NOT REQUIRED', 'NAN', '']:
                    incomplete_count += 1
            
            if incomplete_count >= 2:
                days_and_others_filtered.append(row)
        
        results['prc_pru_days_and_other_requirements'] = len(days_and_others_filtered)
    else:
        results.update({
            'prc_pru_days_worked_only': 0,
            'prc_pru_child_abuse_workshop_only': 0,
            'prc_pru_other_requirements_only': 0,
            'prc_pru_days_and_other_requirements': 0
        })
    
    # For Teachers On Leave and Retirees, we can use the Renewal Classification column
    # Based on actual data: 'Retiree', 'On Leave'
    teachers_on_leave = eligible_df[eligible_df.get('Renewal Classification', '') == 'On Leave']
    retirees = eligible_df[eligible_df.get('Renewal Classification', '') == 'Retiree']
    
    results['total_teachers_on_leave'] = len(teachers_on_leave)
    results['total_retirees'] = len(retirees)
    results['total_prr_complete'] = len(retirees[retirees['computed_status'] == 'Complete'])
    results['total_prr_outstanding'] = len(retirees[retirees['computed_status'] == 'Outstanding'])
    
    # Suspension Analysis
    results['total_suspended_2ss'] = len(df_filtered[df_filtered.get('Suspension Reason Code', '') == '2SS'])
    results['total_suspended_2sr'] = len(df_filtered[df_filtered.get('Suspension Reason Code', '') == '2SR'])
    
    return results

# create_visualization_charts function has been moved to visualizations.py module
    
# create_visualization_charts function has been moved to visualizations.py module

def generate_html_report(para_results, teacher_results, para_differences, teacher_differences, 
                        para_percentage_differences, teacher_percentage_differences, 
                        chart_files, output_dir, has_comparison=False, 
                        para_old_results=None, teacher_old_results=None):
    """
    Generate comprehensive HTML report with difference indicators
    
    Args:
        para_results (dict): Paraprofessional analysis results
        teacher_results (dict): Teacher analysis results
        para_differences (dict): Paraprofessional differences from old data
        teacher_differences (dict): Teacher differences from old data
        chart_files (list): List of chart file paths
        output_dir (str): Output directory
        has_comparison (bool): Whether comparison data is available
        para_old_results (dict): Old paraprofessional results for percentage calculations
        teacher_old_results (dict): Old teacher results for percentage calculations
    """
    # Calculate completion rates for current data
    para_completion_rate = (para_results.get('total_complete', 0) / 
                           max(para_results.get('total_eligible', 1), 1) * 100)
    
    teacher_completion_rate = (teacher_results.get('total_prc_pru_complete', 0) / 
                              max(teacher_results.get('total_prc_pru_eligible', 1), 1) * 100)
    
    # Calculate completion rates for old data (for percentage differences)
    para_old_completion_rate = 0
    teacher_old_completion_rate = 0
    
    if has_comparison and para_old_results and teacher_old_results:
        # Calculate old completion rates using the original old results
        para_old_completion_rate = (para_old_results.get('total_complete', 0) / 
                                   max(para_old_results.get('total_eligible', 1), 1) * 100)
        
        teacher_old_completion_rate = (teacher_old_results.get('total_prc_pru_complete', 0) / 
                                      max(teacher_old_results.get('total_prc_pru_eligible', 1), 1) * 100)
    
    # Function to format metric with difference
    def format_metric_with_diff(value, diff_value, show_diff=True):
        """Format a metric value with optional difference indicator"""
        formatted_value = format_number(value)
        if not show_diff or not has_comparison or diff_value == "0":
            return formatted_value
        
        # Determine color and style based on difference
        if diff_value.startswith('+'):
            color = "#ff8c00"  # Orange for positive
            icon = "▲"
        elif diff_value.startswith('-'):
            color = "#ff8c00"  # Orange for negative
            icon = "▼"
        else:
            return formatted_value
        
        return f'{formatted_value}<br><small style="color: {color}; font-weight: bold;">{icon} {diff_value}</small>'
    
    # Function to format percentage with difference
    def format_percentage_with_diff(value, diff_value, show_diff=True):
        """Format a percentage value with optional difference indicator"""
        formatted_value = format_percentage(value)
        if not show_diff or not has_comparison or diff_value == "0%" or not diff_value:
            return formatted_value
        
        # Determine color and style based on difference
        if diff_value.startswith('+'):
            color = "#ff8c00"  # Orange for positive (neutral)
            icon = "▲"
        elif diff_value.startswith('-'):
            color = "#ff8c00"  # Orange for negative (neutral)
            icon = "▼"
        else:
            return formatted_value
        
        return f'{formatted_value}<br><small style="color: {color}; font-weight: bold;">{icon} {diff_value}</small>'
    
    # Comparison header text
    comparison_text = ""
    if has_comparison:
        comparison_text = "Changes from previous data shown with ▲/▼ indicators"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NYC Public Schools Substitute Renewal Analytics Dashboard</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 0; 
                background-color: #f5f5f5;
            }}
            .header {{ 
                background: linear-gradient(135deg, #2C5282, #1A365D);
                color: white; 
                padding: 20px;
                margin: 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            .header-text {{
                flex: 1;
                text-align: left;
                margin-right: 30px;
            }}
            .header-text h1 {{
                margin: 0;
                font-size: 2.2em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                line-height: 1.2;
            }}
            .header-text h2 {{
                margin: 8px 0;
                font-size: 1.2em;
                font-weight: 600;
                opacity: 0.9;
                line-height: 1.3;
            }}
            .header-text .date-info {{
                margin: 8px 0 0 0;
                font-size: 1.0em;
                opacity: 0.8;
            }}
            .header-logo {{
                flex-shrink: 0;
                display: flex;
                align-items: center;
            }}
            .logo {{
                height: 80px;
                width: auto;
                filter: brightness(1.1);
                margin-left: 20px;
            }}
            .content {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            .section {{ 
                background: white;
                margin: 20px 0; 
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section h2 {{ 
                color: #2C5282; 
                border-bottom: 3px solid #2C5282; 
                padding-bottom: 10px;
                font-weight: 700;
                margin-top: 0;
            }}
            .section h3 {{
                color: #2C5282;
                font-weight: 600;
            }}
            .metrics-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .metric-card {{ 
                background: #f8f9fa; 
                padding: 20px; 
                border-left: 5px solid #2C5282;
                border-radius: 5px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            .metric-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            .metric-value {{ 
                font-size: 2em; 
                font-weight: bold; 
                color: #2C5282; 
            }}
            .metric-label {{ 
                color: #666; 
                margin-top: 5px; 
                font-weight: 500;
            }}
            .chart-container {{ 
                margin: 20px 0; 
                text-align: center; 
            }}
            .summary-box {{ 
                background: #e3f2fd; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 5px solid #1976d2;
            }}
            .alert {{ 
                background: #fff3cd; 
                border: 1px solid #ffeaa7; 
                color: #856404; 
                padding: 15px; 
                border-radius: 5px; 
                margin: 15px 0; 
            }}
            .success {{ 
                background: #d4edda; 
                border: 1px solid #c3e6cb; 
                color: #155724; 
            }}
            .warning {{ 
                background: #f8d7da; 
                border: 1px solid #f5c6cb; 
                color: #721c24; 
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0; 
            }}
            th, td {{ 
                border: 1px solid #ddd; 
                padding: 12px; 
                text-align: left; 
            }}
            th {{ 
                background-color: #2C5282; 
                color: white;
                font-weight: 600;
            }}
            .footer {{
                background-color: #2C5282;
                color: white;
                text-align: center;
                padding: 30px 20px;
                margin-top: 40px;
                font-size: 1.1em;
            }}
            .footer p {{
                margin: 8px 0;
            }}
            .footer a {{
                color: #e3f2fd;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            .progress-container {{
                width: 100%;
                background-color: #e0e0e0;
                border-radius: 25px;
                margin: 10px 0;
                height: 20px;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
            }}
            .progress-bar {{
                height: 100%;
                border-radius: 25px;
                background: linear-gradient(45deg, #1e3a8a, #3b82f6, #60a5fa);
                transition: width 1.5s ease-in-out;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(30, 58, 138, 0.3);
            }}
            .progress-bar::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                bottom: 0;
                right: 0;
                background-image: linear-gradient(
                    45deg,
                    rgba(255, 255, 255, 0.3) 25%,
                    transparent 25%,
                    transparent 50%,
                    rgba(255, 255, 255, 0.3) 50%,
                    rgba(255, 255, 255, 0.3) 75%,
                    transparent 75%,
                    transparent
                );
                background-size: 30px 30px;
                animation: chevronMove 1.5s linear infinite;
            }}
            @keyframes chevronMove {{
                0% {{
                    background-position: -30px 0;
                }}
                100% {{
                    background-position: 30px 0;
                }}
            }}
            .progress-text {{
                text-align: center;
                font-weight: bold;
                color: #2C5282;
                margin-top: 5px;
                font-size: 0.9em;
            }}
            .metric-card-with-progress {{
                background: #f8f9fa; 
                padding: 20px; 
                border-left: 5px solid #2C5282;
                border-radius: 5px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                position: relative;
            }}
            .metric-card-with-progress:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
        </style>
    </head>
    <body>
        {get_header_html("Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Renewal Analytics Dashboard", 
                        "Comprehensive Analysis of Substitute Teacher and Paraprofessional Renewal Data", 
                        f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}{' | ' + comparison_text if comparison_text else ''}")}

        <div class="content">
            <div class="section">
            <h2>Executive Summary</h2>
            <div class="summary-box">
                <h3>Key Performance Indicators</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{format_metric_with_diff(para_results.get('total_eligible', 0), para_differences.get('total_eligible', '0'), has_comparison)}</div>
                        <div class="metric-label">Total SPAs Eligible for Renewal</div>
                    </div>
                    <div class="metric-card-with-progress">
                        <div class="metric-value">{format_percentage_with_diff(para_completion_rate, para_percentage_differences.get('spa_completion_rate', '0%'), has_comparison)}</div>
                        <div class="metric-label">SPA Completion Rate</div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {para_completion_rate:.1f}%;"></div>
                        </div>
                        <div class="progress-text">{para_results.get('total_complete', 0):,} of {para_results.get('total_eligible', 0):,} completed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prc_pru_eligible', 0), teacher_differences.get('total_prc_pru_eligible', '0'), has_comparison)}</div>
                        <div class="metric-label">Total STEs (PRC/PRU) Eligible</div>
                    </div>
                    <div class="metric-card-with-progress">
                        <div class="metric-value">{format_percentage_with_diff(teacher_completion_rate, teacher_percentage_differences.get('ste_completion_rate', '0%'), has_comparison)}</div>
                        <div class="metric-label">STE Completion Rate</div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {teacher_completion_rate:.1f}%;"></div>
                        </div>
                        <div class="progress-text">{teacher_results.get('total_prc_pru_complete', 0):,} of {teacher_results.get('total_prc_pru_eligible', 0):,} completed</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Substitute Paraprofessionals (SPA) Analysis</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('total_eligible', 0), para_differences.get('total_eligible', '0'), has_comparison)}</div>
                    <div class="metric-label">Total SPAs Eligible for Renewal</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('total_complete', 0), para_differences.get('total_complete', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Completed Renewal</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('total_outstanding', 0), para_differences.get('total_outstanding', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Outstanding</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('ra_not_complete', 0), para_differences.get('ra_not_complete', '0'), has_comparison)}</div>
                    <div class="metric-label">RA NOT Complete</div>
                </div>
            </div>
            
            <h3>Requirements Analysis</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('ra_complete_other_outstanding', 0), para_differences.get('ra_complete_other_outstanding', '0'), has_comparison)}</div>
                    <div class="metric-label">RA Complete, Other Requirements Outstanding</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('days_worked_only', 0), para_differences.get('days_worked_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Days Worked Only</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('atas_only', 0), para_differences.get('atas_only', '0'), has_comparison)}</div>
                    <div class="metric-label">ATAS Only</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('child_abuse_workshop_only', 0), para_differences.get('child_abuse_workshop_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Child Abuse Workshop Only</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('days_and_other_requirements', 0), para_differences.get('days_and_other_requirements', '0'), has_comparison)}</div>
                    <div class="metric-label">Days & ATAS/Child Abuse/Other Requirements</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('total_suspended_2ss', 0), para_differences.get('total_suspended_2ss', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Suspended 2SS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('total_suspended_2sr', 0), para_differences.get('total_suspended_2sr', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Suspended 2SR</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Substitute Teachers (STE) Analysis</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_eligible', 0), teacher_differences.get('total_eligible', '0'), has_comparison)}</div>
                    <div class="metric-label">Total STEs Eligible for Renewal</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prc_pru_eligible', 0), teacher_differences.get('total_prc_pru_eligible', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Certified (PRC) and Uncertified (PRU) Eligible</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prc_pru_complete', 0), teacher_differences.get('total_prc_pru_complete', '0'), has_comparison)}</div>
                    <div class="metric-label">Total PRC & PRU Completed Renewal</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prc_pru_outstanding', 0), teacher_differences.get('total_prc_pru_outstanding', '0'), has_comparison)}</div>
                    <div class="metric-label">Total PRC & PRU Outstanding</div>
                </div>
            </div>
            
            <h3>PRC & PRU Requirements Analysis</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_ra_not_complete', 0), teacher_differences.get('prc_pru_ra_not_complete', '0'), has_comparison)}</div>
                    <div class="metric-label">PRC & PRU - RA Not Complete</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_met_ra_other_outstanding', 0), teacher_differences.get('prc_pru_met_ra_other_outstanding', '0'), has_comparison)}</div>
                    <div class="metric-label">PRC & PRU - Met RA, Other Requirements Outstanding</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_days_worked_only', 0), teacher_differences.get('prc_pru_days_worked_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Days Worked Only</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_child_abuse_workshop_only', 0), teacher_differences.get('prc_pru_child_abuse_workshop_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Child Abuse Workshop Only</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_other_requirements_only', 0), teacher_differences.get('prc_pru_other_requirements_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Other Requirements Only</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_days_and_other_requirements', 0), teacher_differences.get('prc_pru_days_and_other_requirements', '0'), has_comparison)}</div>
                    <div class="metric-label">Days & Other Requirements</div>
                </div>
            </div>
            
            <h3>Special Categories</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_teachers_on_leave', 0), teacher_differences.get('total_teachers_on_leave', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Teachers On Leave (PRL)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_retirees', 0), teacher_differences.get('total_retirees', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Retirees (PRR)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prr_complete', 0), teacher_differences.get('total_prr_complete', '0'), has_comparison)}</div>
                    <div class="metric-label">Total PRR Completed Renewal</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prr_outstanding', 0), teacher_differences.get('total_prr_outstanding', '0'), has_comparison)}</div>
                    <div class="metric-label">Total PRR Outstanding</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_suspended_2ss', 0), teacher_differences.get('total_suspended_2ss', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Suspended 2SS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_suspended_2sr', 0), teacher_differences.get('total_suspended_2sr', '0'), has_comparison)}</div>
                    <div class="metric-label">Total Suspended 2SR</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Interactive Visualizations</h2>
            <div class="chart-container">
                <h3>Geographic Distribution by Borough & County</h3>
                <p style="color: #666; text-align: center; margin-bottom: 20px;">
                    Interactive map showing substitute distribution and renewal completion rates across NYC boroughs and neighboring counties (Westchester, Nassau, Suffolk, Bergen, Hudson, Union, Essex, Rockland, Fairfield)
                </p>
                <iframe src="nyc_borough_map.html" width="1250" height="850" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>ZIP Code Choropleth Map - Substitute Paras & Teachers</h3>
                <p style="color: #666; text-align: center; margin-bottom: 20px;">
                    Interactive choropleth map showing substitute paraprofessional and teacher counts by actual ZIP code boundaries. Use the toggle above the map to switch between groups.
                </p>
                <iframe src="nyc_zipcode_choropleth.html" width="1250" height="850" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>Renewal Status Breakdown by Group</h3>
                <p style="color: #666; text-align: center; margin-bottom: 20px;">
                    Each bar shows the complete breakdown of renewal statuses within each substitute group
                </p>
                <iframe src="combined_overview.html" width="950" height="620" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>Renewal Status Breakdown</h3>
                <iframe src="combined_comparison.html" width="1300" height="550" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>Detailed SPA Analysis</h3>
                <iframe src="paraprofessional_overview.html" width="1300" height="550" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>Detailed STE Analysis</h3>
                <iframe src="teacher_overview.html" width="1300" height="550" frameborder="0"></iframe>
            </div>
        </div>
        </div>
        
        {get_professional_footer(['subparajobs@schools.nyc.gov', 'subteacherjobs@schools.nyc.gov'])}
    </body>
    </html>
    """
    
    report_file = os.path.join(output_dir, 'renewal_analytics_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file

def copy_logo_to_output(output_dir):
    """
    Copy the NYC Public Schools logo to the output directory for deployment
    
    Args:
        output_dir (str): Output directory path
    """
    import shutil
    logo_source = os.path.join(RENEWAL_WORKSPACE, "Horizontal_logo_White_PublicSchools.png")
    logo_dest = os.path.join(output_dir, "Horizontal_logo_White_PublicSchools.png")
    
    if os.path.exists(logo_source):
        shutil.copy2(logo_source, logo_dest)
        print(f"✓ Logo copied to output directory: {logo_dest}")
    else:
        print(f"⚠ Warning: Logo not found at {logo_source}")

def get_header_html(logo_path, main_title, subtitle, date_info):
    """
    Generate standardized header HTML with NYC Public Schools branding
    
    Args:
        logo_path (str): Path to the logo file
        main_title (str): Main title text
        subtitle (str): Subtitle text
        date_info (str): Date information text
        
    Returns:
        str: HTML content for the header
    """
    return f"""
    <div class="header">
        <div class="header-content">
            <div class="header-text">
                <h1>{main_title}</h1>
                <h2>{subtitle}</h2>
                <p class="date-info">{date_info}</p>
            </div>
            <div class="header-logo">
                <img src="{logo_path}" alt="NYC Public Schools" class="logo">
            </div>
        </div>
    </div>"""

def get_professional_footer(contact_emails=None):
    """
    Generate standardized footer HTML with NYC Public Schools branding
    
    Args:
        contact_emails (list): List of contact email addresses
        
    Returns:
        str: HTML content for the footer
    """
    contact_info = ""
    if contact_emails:
        contact_links = " | ".join([f'<a href="mailto:{email}" style="color: #e3f2fd;">{email}</a>' for email in contact_emails])
        contact_info = f"<p>Contact: {contact_links}</p>"
    
    return f"""
    <div class="footer">
        <p>Property of the New York City Department of Education</p>
        {contact_info}
        <p>HR School Support Analysis Team | {datetime.now().strftime('%Y')}</p>
    </div>"""

def calculate_differences(new_results, old_results):
    """
    Calculate differences between new and old results
    
    Args:
        new_results (dict): New analysis results
        old_results (dict): Old analysis results
        
    Returns:
        dict: Differences with + or - indicators
    """
    differences = {}
    
    for key in new_results:
        new_val = new_results.get(key, 0)
        old_val = old_results.get(key, 0)
        diff = new_val - old_val
        
        if diff > 0:
            differences[key] = f"+{diff:,}"
        elif diff < 0:
            differences[key] = f"{diff:,}"
        else:
            differences[key] = "0"
    
    return differences

def calculate_percentage_differences(new_results, old_results):
    """
    Calculate percentage differences for completion rates
    
    Args:
        new_results (dict): New analysis results
        old_results (dict): Old analysis results
        
    Returns:
        dict: Percentage differences with + or - indicators
    """
    differences = {}
    
    # Calculate SPA completion rate difference
    new_spa_rate = (new_results.get('total_complete', 0) / 
                   max(new_results.get('total_eligible', 1), 1) * 100)
    old_spa_rate = (old_results.get('total_complete', 0) / 
                   max(old_results.get('total_eligible', 1), 1) * 100)
    spa_diff = new_spa_rate - old_spa_rate
    
    if spa_diff > 0:
        differences['spa_completion_rate'] = f"+{spa_diff:.1f}%"
    elif spa_diff < 0:
        differences['spa_completion_rate'] = f"{spa_diff:.1f}%"
    else:
        differences['spa_completion_rate'] = "0%"
    
    return differences

def calculate_teacher_percentage_differences(new_results, old_results):
    """
    Calculate teacher percentage differences for completion rates
    
    Args:
        new_results (dict): New teacher analysis results
        old_results (dict): Old teacher analysis results
        
    Returns:
        dict: Teacher percentage differences with + or - indicators
    """
    differences = {}
    
    # Calculate STE completion rate difference
    new_ste_rate = (new_results.get('total_prc_pru_complete', 0) / 
                   max(new_results.get('total_prc_pru_eligible', 1), 1) * 100)
    old_ste_rate = (old_results.get('total_prc_pru_complete', 0) / 
                   max(old_results.get('total_prc_pru_eligible', 1), 1) * 100)
    ste_diff = new_ste_rate - old_ste_rate
    
    if ste_diff > 0:
        differences['ste_completion_rate'] = f"+{ste_diff:.1f}%"
    elif ste_diff < 0:
        differences['ste_completion_rate'] = f"{ste_diff:.1f}%"
    else:
        differences['ste_completion_rate'] = "0%"
    
    return differences

# === GEOGRAPHIC ANALYSIS FUNCTIONS ===

def get_nyc_zip_borough_mapping():
    """
    Returns a dictionary mapping NYC ZIP codes and neighboring counties to boroughs/areas
    Based on official NYC ZIP code boundaries and surrounding counties
    """
    zip_to_borough = {}
    
    # Manhattan: 10001-10282
    for zip_code in range(10001, 10283):
        zip_to_borough[str(zip_code)] = 'Manhattan'
    
    # Brooklyn: 11201-11256
    for zip_code in range(11201, 11257):
        zip_to_borough[str(zip_code)] = 'Brooklyn'
    
    # Queens: 11004-11005, 11101-11109, 11351-11697
    for zip_code in range(11004, 11006):
        zip_to_borough[str(zip_code)] = 'Queens'
    for zip_code in range(11101, 11110):
        zip_to_borough[str(zip_code)] = 'Queens'
    for zip_code in range(11351, 11698):
        zip_to_borough[str(zip_code)] = 'Queens'
    
    # Bronx: 10451-10475
    for zip_code in range(10451, 10476):
        zip_to_borough[str(zip_code)] = 'Bronx'
    
    # Staten Island: 10301-10314
    for zip_code in range(10301, 10315):
        zip_to_borough[str(zip_code)] = 'Staten Island'
    
    # === NEIGHBORING COUNTIES ===
    
    # Westchester County (North of NYC)
    westchester_zips = [
        10501, 10502, 10504, 10505, 10506, 10507, 10508, 10509, 10510, 10511,
        10512, 10514, 10516, 10517, 10518, 10519, 10520, 10521, 10522, 10523,
        10524, 10526, 10527, 10528, 10530, 10532, 10533, 10535, 10536, 10537,
        10538, 10540, 10541, 10542, 10543, 10545, 10546, 10547, 10548, 10549,
        10550, 10551, 10552, 10553, 10560, 10562, 10566, 10567, 10570, 10571,
        10572, 10573, 10576, 10577, 10578, 10579, 10580, 10583, 10587, 10588,
        10589, 10590, 10591, 10594, 10595, 10596, 10597, 10598, 10601, 10602,
        10603, 10604, 10605, 10606, 10607, 10608, 10609, 10610, 10701, 10702,
        10703, 10704, 10705, 10706, 10707, 10708, 10709, 10710, 10801, 10802,
        10803, 10804, 10805
    ]
    for zip_code in westchester_zips:
        zip_to_borough[str(zip_code)] = 'Westchester County'
    
    # Nassau County (Long Island - West)
    nassau_zips = [
        11001, 11002, 11003, 11010, 11020, 11021, 11022, 11023, 11024, 11025,
        11026, 11027, 11030, 11040, 11042, 11043, 11044, 11050, 11051, 11052,
        11053, 11054, 11055, 11096, 11501, 11507, 11509, 11510, 11514, 11516,
        11518, 11520, 11530, 11531, 11535, 11536, 11542, 11545, 11547, 11548,
        11549, 11550, 11551, 11552, 11553, 11554, 11555, 11556, 11557, 11558,
        11559, 11560, 11561, 11562, 11563, 11564, 11565, 11566, 11568, 11569,
        11570, 11571, 11572, 11575, 11576, 11577, 11579, 11580, 11581, 11582,
        11590, 11592, 11594, 11595, 11596, 11597, 11598, 11599
    ]
    for zip_code in nassau_zips:
        zip_to_borough[str(zip_code)] = 'Nassau County'
    
    # Suffolk County (Long Island - East)
    suffolk_zips = [
        11701, 11702, 11703, 11704, 11705, 11706, 11707, 11708, 11709, 11710,
        11713, 11714, 11715, 11716, 11717, 11718, 11719, 11720, 11721, 11722,
        11724, 11725, 11726, 11727, 11729, 11730, 11731, 11732, 11733, 11734,
        11735, 11736, 11737, 11738, 11739, 11740, 11741, 11742, 11743, 11746,
        11747, 11749, 11751, 11752, 11753, 11754, 11755, 11756, 11757, 11758,
        11760, 11762, 11763, 11764, 11766, 11767, 11768, 11769, 11770, 11771,
        11772, 11773, 11775, 11776, 11777, 11778, 11779, 11780, 11782, 11783,
        11784, 11786, 11787, 11788, 11789, 11790, 11792, 11794, 11795, 11796,
        11797, 11798, 11901, 11930, 11931, 11932, 11933, 11934, 11935, 11937,
        11939, 11940, 11941, 11942, 11944, 11946, 11947, 11948, 11949, 11950,
        11951, 11952, 11953, 11954, 11955, 11956, 11957, 11958, 11959, 11960,
        11961, 11962, 11963, 11964, 11965, 11967, 11968, 11969, 11970, 11971,
        11972, 11973, 11975, 11976, 11977, 11978, 11980
    ]
    for zip_code in suffolk_zips:
        zip_to_borough[str(zip_code)] = 'Suffolk County'
    
    # Bergen County, NJ (Northeast NJ)
    bergen_zips = [
        '07010', '07020', '07024', '07026', '07027', '07028', '07030', '07031', '07032', '07047',
        '07055', '07057', '07070', '07071', '07072', '07073', '07074', '07075', '07076', '07094',
        '07401', '07410', '07423', '07424', '07430', '07436', '07450', '07452', '07456', '07457',
        '07458', '07463', '07465', '07481', '07495', '07601', '07602', '07603', '07604', '07605',
        '07606', '07607', '07608', '07621', '07624', '07626', '07627', '07628', '07630', '07631',
        '07632', '07640', '07641', '07642', '07643', '07644', '07645', '07646', '07647', '07648',
        '07649', '07650', '07652', '07653', '07654', '07656', '07657', '07660', '07661', '07662',
        '07663', '07666', '07670', '07675', '07676', '07677'
    ]
    for zip_code in bergen_zips:
        zip_to_borough[zip_code] = 'Bergen County, NJ'
    
    # Hudson County, NJ (Adjacent to NYC)
    hudson_zips = [
        '07030', '07086', '07087', '07093', '07097', '07201', '07302', '07303', '07304', '07305',
        '07306', '07307', '07308', '07310', '07311', '07399', '07047', '07086', '07087', '07093',
        '07097', '07201', '07302', '07303', '07304', '07305', '07306', '07307', '07308', '07310',
        '07311', '07399'
    ]
    for zip_code in hudson_zips:
        zip_to_borough[zip_code] = 'Hudson County, NJ'
    
    # Union County, NJ 
    union_zips = [
        '07016', '07023', '07033', '07036', '07060', '07062', '07063', '07064', '07065', '07066',
        '07067', '07076', '07080', '07081', '07083', '07088', '07090', '07091', '07092', '07095',
        '07201', '07202', '07203', '07204', '07206', '07208', '07922', '07923', '07924', '07933',
        '07974', '07980', '08812', '08820', '08827', '08832', '08840', '08863', '08873', '08901',
        '08902', '08906', '08922'
    ]
    for zip_code in union_zips:
        zip_to_borough[zip_code] = 'Union County, NJ'
    
    # Essex County, NJ
    essex_zips = [
        '07003', '07006', '07009', '07017', '07018', '07019', '07028', '07042', '07044', '07050',
        '07052', '07079', '07102', '07103', '07104', '07105', '07106', '07107', '07108', '07109',
        '07110', '07111', '07112', '07114', '07175', '07188', '07189', '07191', '07192', '07193',
        '07195', '07198', '07199', '07936', '07940', '07950', '07960', '07961', '07962', '07963',
        '07970', '07976', '07977', '07978', '07979', '07981', '07999'
    ]
    for zip_code in essex_zips:
        zip_to_borough[zip_code] = 'Essex County, NJ'
    
    # Rockland County, NY (North of NYC, across Hudson River)
    rockland_zips = [
        '10901', '10913', '10914', '10920', '10923', '10924', '10925', '10926', '10927', '10928',
        '10931', '10932', '10940', '10941', '10952', '10954', '10956', '10960', '10962', '10965',
        '10968', '10970', '10974', '10975', '10976', '10977', '10980', '10982', '10983', '10984',
        '10986', '10987', '10989', '10993', '10994', '10996', '10997', '10998'
    ]
    for zip_code in rockland_zips:
        zip_to_borough[zip_code] = 'Rockland County, NY'
    
    # Fairfield County, CT (Northeast)
    fairfield_zips = [
        '06807', '06810', '06820', '06824', '06825', '06830', '06831', '06840', '06850', '06851',
        '06853', '06854', '06855', '06856', '06870', '06877', '06878', '06880', '06883', '06888',
        '06890', '06896', '06897', '06901', '06902', '06903', '06904', '06905', '06906', '06907',
        '06910', '06911', '06912', '06913', '06914', '06920', '06921', '06926', '06927', '06928',
        '06929', '06930', '06460', '06470', '06475', '06477', '06478', '06483', '06484', '06485',
        '06489', '06490', '06492', '06497', '06498', '06610', '06611', '06612', '06614', '06615',
        '06628', '06673', '06702', '06703', '06704', '06705', '06706', '06708', '06710', '06712',
        '06713', '06716', '06770', '06776', '06801', '06804', '06810', '06811', '06812', '06813',
        '06814', '06816', '06817', '06818', '06820', '06824', '06825', '06830', '06831', '06840',
        '06850', '06851', '06853', '06854', '06855', '06856', '06870', '06877', '06878', '06880',
        '06883', '06888', '06890', '06896', '06897'
    ]
    for zip_code in fairfield_zips:
        zip_to_borough[zip_code] = 'Fairfield County, CT'
    
    return zip_to_borough

def map_zip_to_borough(postal_code):
    """
    Map a ZIP code to its corresponding NYC borough
    
    Args:
        postal_code (str): ZIP code
        
    Returns:
        str: Borough name or 'Unknown' if not found
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
    
    # Only process if it's a valid 5-digit number
    if not (postal_str.isdigit() and len(postal_str) == 5):
        return 'Unknown'
    
    zip_to_borough = get_nyc_zip_borough_mapping()
    return zip_to_borough.get(postal_str, 'Unknown')

def get_zip_coordinates(zip_code):
    """
    Get latitude and longitude coordinates for a given ZIP code
    
    Args:
        zip_code (str): ZIP code to get coordinates for
        
    Returns:
        dict: Dictionary with 'lat' and 'lon' keys, or None if not found
    """
    # Comprehensive NYC area ZIP code coordinates
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
    
    # Clean the ZIP code input
    clean_zip = str(zip_code).split('.')[0].split('-')[0].strip()
    
    # Return coordinates if found
    return zip_coords.get(clean_zip)
    
def analyze_substitute_data_by_borough(df_para, df_teacher):
    """
    Analyze substitute data by NYC borough and neighboring counties using Borough column
    
    Args:
        df_para (pd.DataFrame): Paraprofessional data with Borough column
        df_teacher (pd.DataFrame): Teacher data with Borough column
        
    Returns:
        dict: Borough/county analysis results
    """
    borough_data = {}
    
    # Initialize borough and county data structure
    areas = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island', 
             'Westchester County', 'Nassau County', 'Suffolk County', 
             'Bergen County, NJ', 'Hudson County, NJ', 'Union County, NJ', 
             'Essex County, NJ', 'Rockland County, NY', 'Fairfield County, CT', 'Unknown']
    
    for area in areas:
        borough_data[area] = {
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
        
        # Get total counts by area from ALL data
        para_total_by_area = df_para.groupby('Borough').size().to_dict()
        print(f"Para totals by area: {para_total_by_area}")
        
        # Only filter by Status for analysis - much simpler
        df_para_eligible = df_para[df_para['Status'].notna()].copy()
        
        print(f"Para records with status: {len(df_para_eligible)}")
        
        # Calculate completion status - just check if Status is 'COMP' vs 'OUT'
        df_para_eligible['Complete'] = (df_para_eligible['Status'] == 'COMP')
        
        # Group by area
        para_area_stats = df_para_eligible.groupby('Borough').agg({
            'Empl ID': 'count',
            'Complete': 'sum'
        }).reset_index()
        
        para_area_stats.columns = ['Borough', 'Total_Eligible', 'Total_Complete']
        para_area_stats['Total_Outstanding'] = para_area_stats['Total_Eligible'] - para_area_stats['Total_Complete']
        
        print(f"Para area stats:\n{para_area_stats}")
        
        # Update borough data
        for _, row in para_area_stats.iterrows():
            area = row['Borough']
            if area in borough_data:
                borough_data[area]['para_total'] = para_total_by_area.get(area, 0)
                borough_data[area]['para_eligible'] = row['Total_Eligible']
                borough_data[area]['para_complete'] = row['Total_Complete']
                borough_data[area]['para_outstanding'] = row['Total_Outstanding']
                borough_data[area]['para_completion_rate'] = (
                    row['Total_Complete'] / row['Total_Eligible'] * 100
                    if row['Total_Eligible'] > 0 else 0
                )
    
    # Process teacher data
    if df_teacher is not None and not df_teacher.empty:
        print(f"Processing {len(df_teacher)} teacher records for geographic analysis...")
        
        # Get total counts by area from ALL data
        teacher_total_by_area = df_teacher.groupby('Borough').size().to_dict()
        print(f"Teacher totals by area: {teacher_total_by_area}")
        
        # Only filter by Status for analysis
        df_teacher_eligible = df_teacher[df_teacher['Status'].notna()].copy()
        
        print(f"Teacher records with status: {len(df_teacher_eligible)}")
        
        # Calculate completion status - just check if Status is 'COMP' vs 'OUT'
        df_teacher_eligible['Complete'] = (df_teacher_eligible['Status'] == 'COMP')
        
        # Group by area
        teacher_area_stats = df_teacher_eligible.groupby('Borough').agg({
            'Empl ID': 'count',
            'Complete': 'sum'
        }).reset_index()
        
        teacher_area_stats.columns = ['Borough', 'Total_Eligible', 'Total_Complete']
        teacher_area_stats['Total_Outstanding'] = teacher_area_stats['Total_Eligible'] - teacher_area_stats['Total_Complete']
        
        print(f"Teacher area stats:\n{teacher_area_stats}")
        
        # Update borough data
        for _, row in teacher_area_stats.iterrows():
            area = row['Borough']
            if area in borough_data:
                borough_data[area]['teacher_total'] = teacher_total_by_area.get(area, 0)
                borough_data[area]['teacher_eligible'] = row['Total_Eligible']
                borough_data[area]['teacher_complete'] = row['Total_Complete']
                borough_data[area]['teacher_outstanding'] = row['Total_Outstanding']
                borough_data[area]['teacher_completion_rate'] = (
                    row['Total_Complete'] / row['Total_Eligible'] * 100
                    if row['Total_Eligible'] > 0 else 0
                )
    
    return borough_data

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
            style='carto-positron',
            center=dict(lat=40.7589, lon=-73.7004),  # Centered between NYC and surrounding areas
            zoom=8.5  # Zoomed out to show neighboring counties
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

def generate_zipcode_choropleth():
    import pandas as pd
    # Load boundary data
    boundary_csv = os.path.join(RENEWAL_WORKSPACE, 'Modified_Zip_Code_Tabulation_Areas__MODZCTA__20250709.csv')
    df_boundaries = pd.read_csv(boundary_csv)

    # Load para and teacher data
    para_csv = os.path.join(RENEWAL_WORKSPACE, 'substitute_paraprofessionals.csv')
    teacher_csv = os.path.join(RENEWAL_WORKSPACE, 'substitute_teachers.csv')
    df_para = pd.read_csv(para_csv)
    df_teacher = pd.read_csv(teacher_csv)

    # --- Clean and aggregate ZIP codes for paras ---
    para_zip_counts = (
        df_para['Postal']
        .astype(str)
        .str.replace('.0', '', regex=False)
        .str.strip()
        .str.zfill(5)
    )
    para_zip_counts = para_zip_counts[~para_zip_counts.isin(['Unknown', 'nan', 'None', '', '00000'])]
    para_zip_counts = para_zip_counts.value_counts().reset_index()
    para_zip_counts.columns = ['zip_code', 'count']

    # --- Clean and aggregate ZIP codes for teachers (match heatmap logic) ---
    teacher_zip = (
        df_teacher['Postal']
        .astype(str)
        .str.replace('.0', '', regex=False)
        .str.strip()
        .str.zfill(5)
    )
    teacher_zip = teacher_zip[~teacher_zip.isin(['Unknown', 'nan', 'None', '', '00000'])]
    teacher_zip_counts = teacher_zip.value_counts().reset_index()
    teacher_zip_counts.columns = ['zip_code', 'count']

    # Output file path
    output_file = os.path.join(OUTPUT_DIR, 'nyc_zipcode_choropleth.html')

    # Generate the map
    create_zipcode_choropleth_map_dual(
        para_zip_counts,
        teacher_zip_counts,
        df_boundaries,
        output_file,
        para_col='count',
        teacher_col='count',
        zip_col='zip_code',
        boundary_zip_col='MODZCTA'
    )
    print(f"Choropleth map saved to: {output_file}")

    # Generate ZIP code density heatmap (dual)
    output_heatmap_file = os.path.join(OUTPUT_DIR, 'nyc_zipcode_density_heatmap.html')
    create_dual_zipcode_heatmap(
        df_para,
        df_teacher,
        output_heatmap_file
    )
    print(f"Density heatmap saved to: {output_heatmap_file}")

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

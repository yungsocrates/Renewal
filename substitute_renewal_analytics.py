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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import numpy as np
import os
import re
import time
from datetime import datetime
import warnings
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
    print(f"Available columns: {list(df_para.columns)}")
    print(f"\nSample Status values: {df_para['Status'].value_counts()}")
    print(f"Sample RA values: {df_para['Reasonable Assurance'].value_counts()}")
    
    # For paraprofessionals, we'll work with all active records
    # Convert Status to uppercase for consistent comparison
    df_para_clean = df_para.copy()
    df_para_clean['Status'] = df_para_clean['Status'].astype(str).str.strip().str.upper()
    
    # Filter out terminated or inactive records if needed
    active_df = df_para_clean[df_para_clean['Status'].notna()].copy()
    
    # Determine completion status based on Status column
    # Status column: Out = outstanding, COMPL = complete (based on actual data)
    def get_completion_status(row):
        """Get completion status from Status column"""
        status = str(row.get('Status', '')).strip()
        if status.upper() in ['COMPL', 'COMPLETE']:
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
    ra_complete_group = active_df[
        active_df.get('Reasonable Assurance', '').astype(str).str.strip().str.upper().isin(['COMPLETE'])
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
        
        # Autism Workshop Only (≥20 days, only Autism Workshop incomplete)
        autism_only_candidates = ra_complete_group[
            (ra_complete_group['days_worked_int'] >= 20) &
            (ra_complete_group['computed_status'] == 'Outstanding')
        ]
        
        autism_only_filtered = []
        for _, row in autism_only_candidates.iterrows():
            autism_incomplete = is_requirement_outstanding(row.get('Autism Workshop', ''))
            
            # Check if other major requirements are complete
            other_reqs = [
                row.get('Child Abuse Workshop', ''),
                row.get('Violence Prevention Workshop', ''),
                row.get('DASA Workshop', ''),
                row.get('SubHub Training', ''),
                row.get('State Exam', '')
            ]
            
            other_complete_count = sum(1 for req in other_reqs 
                                     if str(req).strip().upper() != 'NOT REQUIRED' and is_requirement_complete(req))
            other_required_count = sum(1 for req in other_reqs 
                                     if str(req).strip().upper() != 'NOT REQUIRED')
            
            # If autism is incomplete but most others are complete
            if autism_incomplete and other_required_count > 0 and (other_complete_count / other_required_count) >= 0.8:
                autism_only_filtered.append(row)
        
        results['autism_workshop_only'] = len(autism_only_filtered)
        
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
            'autism_workshop_only': 0,
            'days_and_other_requirements': 0
        })
    
    print(f"Detailed Analysis - Days Only: {results['days_worked_only']}, Autism Only: {results['autism_workshop_only']}, ATAS Only: {results['atas_only']}, Days & Others: {results['days_and_other_requirements']}")
    
    # Suspension Analysis
    results['total_suspended_2ss'] = len(df_para_clean[df_para_clean.get('Suspension Reason Code', '').astype(str).str.strip() == '2SS'])
    results['total_suspended_2sr'] = len(df_para_clean[df_para_clean.get('Suspension Reason Code', '').astype(str).str.strip() == '2SR'])
    
    print(f"Suspension Analysis - 2SS: {results['total_suspended_2ss']}, 2SR: {results['total_suspended_2sr']}")
    
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
    
    # Exclude "Pending Term for FT" if this status exists
    df_filtered = df_teacher[df_teacher.get('Status', '') != 'Pending Term for FT'].copy()
    
    # For teachers, we'll work with all active records
    eligible_df = df_filtered[df_filtered['Status'].notna()].copy()
    
    # Determine completion status based on Status column
    # Status column: Out = outstanding, COMPL = complete (based on actual data)
    def get_teacher_completion_status(row):
        """Get completion status from Status column"""
        status = str(row.get('Status', '')).strip()
        if status.upper() in ['COMPL', 'COMPLETE']:
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
                row.get('State Exam', ''),
                row.get('Ed Credits', ''),
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
        
        # Autism Workshop Only (≥20 days, Autism Workshop not complete)
        autism_only = prc_pru_ra_complete[
            (prc_pru_ra_complete['days_worked_int'] >= 20) &
            (prc_pru_ra_complete.get('Autism Workshop', '').astype(str).str.strip().str.upper() == 'NOT COMPLETE') &
            (prc_pru_ra_complete['computed_status'] == 'Outstanding')
        ]
        results['prc_pru_autism_workshop_only'] = len(autism_only)
        
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
                    row.get('State Exam', ''),
                    row.get('Ed Credits', ''),
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
                row.get('State Exam', ''),
                row.get('Ed Credits', ''),
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
            'prc_pru_autism_workshop_only': 0,
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

def create_visualization_charts(para_results, teacher_results, output_dir):
    """
    Create interactive visualization charts
    
    Args:
        para_results (dict): Paraprofessional analysis results
        teacher_results (dict): Teacher analysis results
        output_dir (str): Output directory for charts
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Paraprofessional Overview Chart
    para_labels = ['Total Eligible', 'Completed', 'Outstanding', 'RA Not Complete', 
                   'Days Only', 'ATAS Only', 'Autism Only']
    para_values = [
        para_results.get('total_eligible', 0),
        para_results.get('total_complete', 0),
        para_results.get('total_outstanding', 0),
        para_results.get('ra_not_complete', 0),
        para_results.get('days_worked_only', 0),
        para_results.get('atas_only', 0),
        para_results.get('autism_workshop_only', 0)
    ]
    
    fig_para = go.Figure(data=[
        go.Bar(
            x=para_labels,
            y=para_values,
            marker_color=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', 
                         '#9467bd', '#8c564b', '#e377c2'],
            text=[format_number(v) for v in para_values],
            textposition='auto'
        )
    ])
    
    fig_para.update_layout(
        title='Substitute Paraprofessional Renewal Overview',
        xaxis_title='Categories',
        yaxis_title='Number of Substitutes',
        height=500,
        width=1200
    )
    
    para_chart_file = os.path.join(output_dir, 'paraprofessional_overview.html')
    pyo.plot(fig_para, filename=para_chart_file, auto_open=False)
    
    # Teacher Overview Chart
    teacher_labels = ['Total Eligible', 'PRC/PRU Eligible', 'PRC/PRU Complete', 
                     'PRC/PRU Outstanding', 'Teachers On Leave', 'Retirees']
    teacher_values = [
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
            y=teacher_values,
            marker_color=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', 
                         '#9467bd', '#8c564b'],
            text=[format_number(v) for v in teacher_values],
            textposition='auto'
        )
    ])
    
    fig_teacher.update_layout(
        title='Substitute Teacher Renewal Overview',
        xaxis_title='Categories',
        yaxis_title='Number of Substitutes',
        height=500,
        width=1200
    )
    
    teacher_chart_file = os.path.join(output_dir, 'teacher_overview.html')
    pyo.plot(fig_teacher, filename=teacher_chart_file, auto_open=False)
    
    # Combined Comparison Chart
    fig_combined = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Paraprofessionals', 'Teachers'),
        specs=[[{"type": "domain"}, {"type": "domain"}]]
    )
    
    # Paraprofessional pie chart
    fig_combined.add_trace(
        go.Pie(
            labels=['Completed', 'Outstanding'],
            values=[para_results.get('total_complete', 0), 
                   para_results.get('total_outstanding', 0)],
            name="Paraprofessionals",
            hole=0.3,
            marker_colors=['#2ca02c', '#ff7f0e']
        ),
        row=1, col=1
    )
    
    # Teacher pie chart
    fig_combined.add_trace(
        go.Pie(
            labels=['PRC/PRU Complete', 'PRC/PRU Outstanding', 'On Leave', 'Retirees'],
            values=[teacher_results.get('total_prc_pru_complete', 0),
                   teacher_results.get('total_prc_pru_outstanding', 0),
                   teacher_results.get('total_teachers_on_leave', 0),
                   teacher_results.get('total_retirees', 0)],
            name="Teachers",
            hole=0.3,
            marker_colors=['#2ca02c', '#ff7f0e', '#9467bd', '#8c564b']
        ),
        row=1, col=2
    )
    
    fig_combined.update_layout(
        title_text="Renewal Status Comparison: Paraprofessionals vs Teachers",
        height=500,
        width=1200
    )
    
    combined_chart_file = os.path.join(output_dir, 'combined_comparison.html')
    pyo.plot(fig_combined, filename=combined_chart_file, auto_open=False)
    
    return [para_chart_file, teacher_chart_file, combined_chart_file]

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
            color = "#28a745"  # Green for positive
            icon = "▲"
        elif diff_value.startswith('-'):
            color = "#dc3545"  # Red for negative
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
            color = "#28a745"  # Green for positive
            icon = "▲"
        elif diff_value.startswith('-'):
            color = "#dc3545"  # Red for negative
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
                    <div class="metric-card">
                        <div class="metric-value">{format_percentage_with_diff(para_completion_rate, para_percentage_differences.get('spa_completion_rate', '0%'), has_comparison)}</div>
                        <div class="metric-label">SPA Completion Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{format_metric_with_diff(teacher_results.get('total_prc_pru_eligible', 0), teacher_differences.get('total_prc_pru_eligible', '0'), has_comparison)}</div>
                        <div class="metric-label">Total STEs (PRC/PRU) Eligible</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{format_percentage_with_diff(teacher_completion_rate, teacher_percentage_differences.get('ste_completion_rate', '0%'), has_comparison)}</div>
                        <div class="metric-label">STE Completion Rate</div>
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
                    <div class="metric-value">{format_metric_with_diff(para_results.get('autism_workshop_only', 0), para_differences.get('autism_workshop_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Autism Workshop Only</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_metric_with_diff(para_results.get('days_and_other_requirements', 0), para_differences.get('days_and_other_requirements', '0'), has_comparison)}</div>
                    <div class="metric-label">Days & ATAS/Autism/Other Requirements</div>
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
                    <div class="metric-value">{format_metric_with_diff(teacher_results.get('prc_pru_autism_workshop_only', 0), teacher_differences.get('prc_pru_autism_workshop_only', '0'), has_comparison)}</div>
                    <div class="metric-label">Autism Workshop Only</div>
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
                <h3>Paraprofessional Overview</h3>
                <iframe src="paraprofessional_overview.html" width="1200" height="520" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>Teacher Overview</h3>
                <iframe src="teacher_overview.html" width="1200" height="520" frameborder="0"></iframe>
            </div>
            
            <div class="chart-container">
                <h3>Comparison Analysis</h3>
                <iframe src="combined_comparison.html" width="1200" height="520" frameborder="0"></iframe>
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
            para_results = analyze_substitute_paraprofessionals(df_para)
            print("✓ Current paraprofessional analysis completed")
        else:
            print("⚠ Skipping current paraprofessional analysis - CSV file not found")
            df_para = None
            # Initialize with default values
            para_results = {key: 0 for key in [
                'total_eligible', 'total_complete', 'total_outstanding', 'ra_not_complete',
                'ra_complete_other_outstanding', 'days_worked_only', 'atas_only',
                'autism_workshop_only', 'days_and_other_requirements', 'total_suspended_2ss',
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
            teacher_results = analyze_substitute_teachers(df_teacher)
            print("✓ Current teacher analysis completed")
        else:
            print("⚠ Skipping current teacher analysis - CSV file not found")
            df_teacher = None
            # Initialize with default values
            teacher_results = {key: 0 for key in [
                'total_eligible', 'total_prc_pru_eligible', 'total_prc_pru_complete',
                'total_prc_pru_outstanding', 'prc_pru_ra_not_complete', 'prc_pru_met_ra_other_outstanding',
                'prc_pru_days_worked_only', 'prc_pru_autism_workshop_only', 'prc_pru_other_requirements_only',
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
        
        print("\n✓ Analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error occurred during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

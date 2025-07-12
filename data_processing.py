"""
Data Processing Module for NYC Public Schools Substitute Renewal Analytics
Handles CSV loading, data cleaning, and basic analysis functions
"""

import pandas as pd
import os
from datetime import datetime
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === GLOBAL CONSTANTS ===
RENEWAL_WORKSPACE = r"c:\Users\OFerreira3\Documents\Renewal"

def load_csv_data(csv_path, data_type):
    """
    Load and validate CSV data with comprehensive error handling
    
    Args:
        csv_path (str): Path to the CSV file
        data_type (str): Type description for logging (e.g., "para", "teacher")
        
    Returns:
        pd.DataFrame: Loaded and validated DataFrame
    """
    try:
        print(f"Loading {data_type} data from: {csv_path}")
        
        # Read CSV with error handling
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Ensure Postal column is string type and clean float ZIP codes
        if 'Postal' in df.columns:
            df['Postal'] = df['Postal'].astype(str).str.replace('.0', '').str.strip()
        
        print(f"Loaded {len(df)} records")
        print(f"Columns found: {df.columns.tolist()}")
        
        return df
        
    except UnicodeDecodeError:
        # Try alternative encoding
        print(f"UTF-8 failed, trying latin-1 encoding...")
        df = pd.read_csv(csv_path, encoding='latin-1')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Ensure Postal column is string type and clean float ZIP codes
        if 'Postal' in df.columns:
            df['Postal'] = df['Postal'].astype(str).str.replace('.0', '').str.strip()
        
        print(f"Loaded {len(df)} records with latin-1 encoding")
        return df
        
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return pd.DataFrame()
        
    except Exception as e:
        print(f"Error loading {data_type} data: {str(e)}")
        return pd.DataFrame()

def format_number(num):
    """Format number with commas for thousands separation"""
    return f"{num:,}"

def format_percentage(num):
    """Format number as percentage with one decimal place"""
    return f"{num:.1f}%"

def safe_int_conversion(value):
    """Safely convert values to integer"""
    try:
        if pd.isna(value):
            return 0
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def format_metric_with_diff(current_value, diff_string, show_diff=True):
    """Format metric with optional difference indicator"""
    formatted_current = format_number(current_value)
    if show_diff and diff_string != '0':
        return f"{formatted_current} ({diff_string})"
    return formatted_current

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

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
    logger.info("=== RAW DATA DEBUG ===")
    logger.info(f"Original CSV rows: {len(df_para)}")
    
    if len(df_para) > 0:
        logger.info(f"All available columns: {list(df_para.columns)}")
        logger.info(f"Sample of first few rows:")
        for i, (idx, row) in enumerate(df_para.head(3).iterrows()):
            logger.info(f"  Row {i+1}: {dict(row)}")

    # Check if required columns exist
    required_columns = ['Clearance Date', 'TA1', 'TA2', 'CAW1', 'CAW2', 'WSA1']
    missing_columns = [col for col in required_columns if col not in df_para.columns]
    
    if missing_columns:
        logger.warning(f"Missing required columns for para analysis: {missing_columns}")
        # Return default values if columns are missing
        return {
            'total_eligible': len(df_para),
            'total_complete': 0,
            'total_outstanding': len(df_para),
            'ra_not_complete': 0,
            'ra_complete_other_outstanding': 0,
            'days_worked_only': 0,
            'atas_only': 0,
            'child_abuse_workshop_only': 0,
            'days_and_other_requirements': 0,
            'total_suspended_2ss': 0,
            'total_suspended_2sr': 0
        }

    # Filter out rows where Clearance Date is not empty (already cleared)
    total_eligible = len(df_para[df_para['Clearance Date'].isna() | (df_para['Clearance Date'] == '')])
    
    # Filter to only eligible records for detailed analysis
    df_eligible = df_para[df_para['Clearance Date'].isna() | (df_para['Clearance Date'] == '')]
    results['total_eligible'] = total_eligible

    logger.info(f"Total Eligible Paraprofessionals: {total_eligible}")

    if total_eligible == 0:
        logger.info("No eligible paraprofessionals found")
        return {key: 0 for key in [
            'total_eligible', 'total_complete', 'total_outstanding', 'ra_not_complete',
            'ra_complete_other_outstanding', 'days_worked_only', 'atas_only',
            'child_abuse_workshop_only', 'days_and_other_requirements', 'total_suspended_2ss',
            'total_suspended_2sr'
        ]}

    # Create completion status flags
    df_eligible = df_eligible.copy()
    
    # TA1 and TA2 (Teaching Assistant requirements)
    df_eligible['ta1_complete'] = ~df_eligible['TA1'].isna() & (df_eligible['TA1'] != '')
    df_eligible['ta2_complete'] = ~df_eligible['TA2'].isna() & (df_eligible['TA2'] != '')
    df_eligible['atas_complete'] = df_eligible['ta1_complete'] & df_eligible['ta2_complete']
    
    # CAW1 and CAW2 (Child Abuse Workshop)
    df_eligible['caw1_complete'] = ~df_eligible['CAW1'].isna() & (df_eligible['CAW1'] != '')
    df_eligible['caw2_complete'] = ~df_eligible['CAW2'].isna() & (df_eligible['CAW2'] != '')
    df_eligible['child_abuse_complete'] = df_eligible['caw1_complete'] & df_eligible['caw2_complete']
    
    # WSA1 (Work Study Agreement or Days Worked)
    df_eligible['days_worked_complete'] = ~df_eligible['WSA1'].isna() & (df_eligible['WSA1'] != '')

    # Overall completion status
    df_eligible['all_complete'] = (df_eligible['atas_complete'] & 
                                   df_eligible['child_abuse_complete'] & 
                                   df_eligible['days_worked_complete'])

    # Calculate totals
    results['total_complete'] = int(df_eligible['all_complete'].sum())
    results['total_outstanding'] = total_eligible - results['total_complete']

    # Detailed breakdown of outstanding requirements
    outstanding = df_eligible[~df_eligible['all_complete']]
    
    # RA (Renewal Application) not complete - missing both TA requirements
    results['ra_not_complete'] = int((~outstanding['atas_complete']).sum())
    
    # RA complete but other requirements outstanding
    results['ra_complete_other_outstanding'] = int((outstanding['atas_complete']).sum())
    
    # Only missing days worked (has TA and CAW)
    results['days_worked_only'] = int((outstanding['atas_complete'] & 
                                       outstanding['child_abuse_complete'] & 
                                       ~outstanding['days_worked_complete']).sum())
    
    # Only missing child abuse workshop (has TA and days)
    results['child_abuse_workshop_only'] = int((outstanding['atas_complete'] & 
                                                ~outstanding['child_abuse_complete'] & 
                                                outstanding['days_worked_complete']).sum())
    
    # Only missing TA requirements (has CAW and days)
    results['atas_only'] = int((~outstanding['atas_complete'] & 
                                outstanding['child_abuse_complete'] & 
                                outstanding['days_worked_complete']).sum())
    
    # Missing days worked and other requirements (has TA)
    results['days_and_other_requirements'] = int((outstanding['atas_complete'] & 
                                                  ~outstanding['child_abuse_complete'] & 
                                                  ~outstanding['days_worked_complete']).sum())

    # Suspended counts (if these columns exist)
    results['total_suspended_2ss'] = 0
    results['total_suspended_2sr'] = 0
    
    if '2SS' in df_para.columns:
        results['total_suspended_2ss'] = int((~df_para['2SS'].isna() & (df_para['2SS'] != '')).sum())
    
    if '2SR' in df_para.columns:
        results['total_suspended_2sr'] = int((~df_para['2SR'].isna() & (df_para['2SR'] != '')).sum())

    # Print results for debugging
    logger.info("=== PARAPROFESSIONAL ANALYSIS RESULTS ===")
    for key, value in results.items():
        logger.info(f"{key}: {value}")

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

    logger.info("=== SUBSTITUTE TEACHER ANALYSIS ===")
    logger.info(f"Total teacher records: {len(df_teacher)}")
    
    if len(df_teacher) > 0:
        logger.info(f"Available columns: {list(df_teacher.columns)}")

    # Check required columns
    required_columns = ['Clearance Date', 'TA1', 'TA2', 'CAW1', 'CAW2', 'WSA1']
    missing_columns = [col for col in required_columns if col not in df_teacher.columns]
    
    if missing_columns:
        logger.warning(f"Missing required columns for teacher analysis: {missing_columns}")
        return {
            'total_eligible': len(df_teacher),
            'total_prc_pru_eligible': 0,
            'total_prc_pru_complete': 0,
            'total_prc_pru_outstanding': len(df_teacher),
            'prc_pru_ra_not_complete': 0,
            'prc_pru_met_ra_other_outstanding': 0,
            'prc_pru_days_worked_only': 0,
            'prc_pru_child_abuse_workshop_only': 0,
            'prc_pru_other_requirements_only': 0,
            'prc_pru_days_and_other_requirements': 0,
            'total_teachers_on_leave': 0,
            'total_retirees': 0,
            'total_prr_complete': 0,
            'total_prr_outstanding': 0,
            'total_suspended_2ss': 0,
            'total_suspended_2sr': 0
        }

    # Total eligible (not yet cleared)
    total_eligible = len(df_teacher[df_teacher['Clearance Date'].isna() | (df_teacher['Clearance Date'] == '')])
    results['total_eligible'] = total_eligible

    # For teachers, we need to distinguish between PRC/PRU eligible and other categories
    df_eligible = df_teacher[df_teacher['Clearance Date'].isna() | (df_teacher['Clearance Date'] == '')]
    
    # PRC/PRU eligible (assuming this is a subset - you may need to adjust the filter)
    df_prc_pru = df_eligible.copy()  # For now, assume all eligible are PRC/PRU
    results['total_prc_pru_eligible'] = len(df_prc_pru)

    logger.info(f"Total Eligible Teachers: {total_eligible}")
    logger.info(f"PRC/PRU Eligible Teachers: {results['total_prc_pru_eligible']}")

    if len(df_prc_pru) == 0:
        logger.info("No PRC/PRU eligible teachers found")
        return {key: 0 for key in [
            'total_eligible', 'total_prc_pru_eligible', 'total_prc_pru_complete',
            'total_prc_pru_outstanding', 'prc_pru_ra_not_complete', 'prc_pru_met_ra_other_outstanding',
            'prc_pru_days_worked_only', 'prc_pru_child_abuse_workshop_only', 'prc_pru_other_requirements_only',
            'prc_pru_days_and_other_requirements', 'total_teachers_on_leave', 'total_retirees',
            'total_prr_complete', 'total_prr_outstanding', 'total_suspended_2ss', 'total_suspended_2sr'
        ]}

    # Create completion status flags
    df_prc_pru = df_prc_pru.copy()
    
    # TA1 and TA2 (Teaching Assistant requirements / Renewal Application)
    df_prc_pru['ta1_complete'] = ~df_prc_pru['TA1'].isna() & (df_prc_pru['TA1'] != '')
    df_prc_pru['ta2_complete'] = ~df_prc_pru['TA2'].isna() & (df_prc_pru['TA2'] != '')
    df_prc_pru['ra_complete'] = df_prc_pru['ta1_complete'] & df_prc_pru['ta2_complete']
    
    # CAW1 and CAW2 (Child Abuse Workshop)
    df_prc_pru['caw1_complete'] = ~df_prc_pru['CAW1'].isna() & (df_prc_pru['CAW1'] != '')
    df_prc_pru['caw2_complete'] = ~df_prc_pru['CAW2'].isna() & (df_prc_pru['CAW2'] != '')
    df_prc_pru['child_abuse_complete'] = df_prc_pru['caw1_complete'] & df_prc_pru['caw2_complete']
    
    # WSA1 (Work Study Agreement or Days Worked)
    df_prc_pru['days_worked_complete'] = ~df_prc_pru['WSA1'].isna() & (df_prc_pru['WSA1'] != '')

    # Overall PRC/PRU completion status
    df_prc_pru['prc_pru_complete'] = (df_prc_pru['ra_complete'] & 
                                      df_prc_pru['child_abuse_complete'] & 
                                      df_prc_pru['days_worked_complete'])

    # Calculate PRC/PRU totals
    results['total_prc_pru_complete'] = int(df_prc_pru['prc_pru_complete'].sum())
    results['total_prc_pru_outstanding'] = len(df_prc_pru) - results['total_prc_pru_complete']

    # Detailed breakdown of outstanding PRC/PRU requirements
    outstanding = df_prc_pru[~df_prc_pru['prc_pru_complete']]
    
    # RA not complete
    results['prc_pru_ra_not_complete'] = int((~outstanding['ra_complete']).sum())
    
    # Met RA but other requirements outstanding
    results['prc_pru_met_ra_other_outstanding'] = int((outstanding['ra_complete']).sum())
    
    # Only missing days worked (has RA and CAW)
    results['prc_pru_days_worked_only'] = int((outstanding['ra_complete'] & 
                                               outstanding['child_abuse_complete'] & 
                                               ~outstanding['days_worked_complete']).sum())
    
    # Only missing child abuse workshop (has RA and days)
    results['prc_pru_child_abuse_workshop_only'] = int((outstanding['ra_complete'] & 
                                                        ~outstanding['child_abuse_complete'] & 
                                                        outstanding['days_worked_complete']).sum())
    
    # Only missing other requirements (has RA but missing CAW and days)
    results['prc_pru_other_requirements_only'] = int((outstanding['ra_complete'] & 
                                                      ~outstanding['child_abuse_complete'] & 
                                                      ~outstanding['days_worked_complete']).sum())
    
    # Missing days worked and other requirements
    results['prc_pru_days_and_other_requirements'] = int((outstanding['ra_complete'] & 
                                                          ~outstanding['child_abuse_complete'] & 
                                                          ~outstanding['days_worked_complete']).sum())

    # Special teacher categories (these may need different column mappings)
    results['total_teachers_on_leave'] = 0  # Add logic if this data is available
    results['total_retirees'] = 0  # Add logic if this data is available
    results['total_prr_complete'] = 0  # Add logic for PRR (different from PRC/PRU)
    results['total_prr_outstanding'] = 0  # Add logic for PRR outstanding

    # Suspended counts
    results['total_suspended_2ss'] = 0
    results['total_suspended_2sr'] = 0
    
    if '2SS' in df_teacher.columns:
        results['total_suspended_2ss'] = int((~df_teacher['2SS'].isna() & (df_teacher['2SS'] != '')).sum())
    
    if '2SR' in df_teacher.columns:
        results['total_suspended_2sr'] = int((~df_teacher['2SR'].isna() & (df_teacher['2SR'] != '')).sum())

    # Print results for debugging
    logger.info("=== TEACHER ANALYSIS RESULTS ===")
    for key, value in results.items():
        logger.info(f"{key}: {value}")

    return results

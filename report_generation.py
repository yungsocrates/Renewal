#!/usr/bin/env python3
"""
NYC Public Schools Substitute Renewal Report Generation
======================================================

This module contains functions for generating HTML reports from substitute
teacher and paraprofessional renewal data analysis.

Author: HR School Support Analysis Team
Date: July 2025
"""

import os
import pandas as pd
from datetime import datetime
from data_processing import format_number, format_percentage


def generate_html_report(para_data, teacher_data, differences, borough_data, output_dir):
    """
    Generate comprehensive HTML report with all analysis results
    
    Args:
        para_data (dict): Paraprofessional analysis results
        teacher_data (dict): Teacher analysis results
        differences (dict): Comparison differences
        borough_data (dict): Borough/geographic analysis results
        output_dir (str): Output directory for HTML file
        
    Returns:
        str: Path to generated HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYC Substitute Staff Renewal Analytics Report</title>
        <link rel="stylesheet" href="static/css/styles.css">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="Horizontal_logo_White_PublicSchools.png" alt="NYC Public Schools" class="logo">
                <h1>Substitute Staff Renewal Analytics Report</h1>
                <p class="timestamp">Generated: {timestamp}</p>
            </div>
            
            <div class="content">
                {generate_executive_summary(para_data, teacher_data, differences)}
                {generate_paraprofessional_section(para_data)}
                {generate_teacher_section(teacher_data)}
                {generate_comparison_section(differences)}
                {generate_geographic_section(borough_data)}
            </div>
            
            <div class="footer">
                <p>© 2025 NYC Public Schools - HR School Support Analysis Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    output_path = os.path.join(output_dir, "combined_overview.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def generate_executive_summary(para_data, teacher_data, differences):
    """
    Generate executive summary section
    
    Args:
        para_data (dict): Paraprofessional analysis results
        teacher_data (dict): Teacher analysis results
        differences (dict): Comparison differences
        
    Returns:
        str: HTML content for executive summary
    """
    return f"""
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Substitute Paraprofessionals</h3>
                <div class="metric">
                    <span class="number">{format_number(para_data.get('total_eligible', 0))}</span>
                    <span class="label">Total Eligible</span>
                </div>
                <div class="metric">
                    <span class="number">{format_percentage(para_data.get('completion_rate', 0))}</span>
                    <span class="label">Completion Rate</span>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>Substitute Teachers</h3>
                <div class="metric">
                    <span class="number">{format_number(teacher_data.get('total_eligible', 0))}</span>
                    <span class="label">Total Eligible</span>
                </div>
                <div class="metric">
                    <span class="number">{format_percentage(teacher_data.get('completion_rate', 0))}</span>
                    <span class="label">Completion Rate</span>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>Key Changes</h3>
                <div class="metric">
                    <span class="number">{differences.get('para_eligible', 'N/A')}</span>
                    <span class="label">Para Eligible Change</span>
                </div>
                <div class="metric">
                    <span class="number">{differences.get('teacher_eligible', 'N/A')}</span>
                    <span class="label">Teacher Eligible Change</span>
                </div>
            </div>
        </div>
    </div>
    """


def generate_paraprofessional_section(para_data):
    """
    Generate paraprofessional analysis section
    
    Args:
        para_data (dict): Paraprofessional analysis results
        
    Returns:
        str: HTML content for paraprofessional section
    """
    return f"""
    <div class="section">
        <h2>Substitute Paraprofessionals Analysis</h2>
        <div class="data-grid">
            <div class="data-card">
                <h3>Renewal Status</h3>
                <table class="data-table">
                    <tr>
                        <td>Total Records</td>
                        <td>{format_number(para_data.get('total_records', 0))}</td>
                    </tr>
                    <tr>
                        <td>Eligible for Renewal</td>
                        <td>{format_number(para_data.get('total_eligible', 0))}</td>
                    </tr>
                    <tr>
                        <td>Completed</td>
                        <td>{format_number(para_data.get('completed', 0))}</td>
                    </tr>
                    <tr>
                        <td>Outstanding</td>
                        <td>{format_number(para_data.get('outstanding', 0))}</td>
                    </tr>
                    <tr class="highlight">
                        <td>Completion Rate</td>
                        <td>{format_percentage(para_data.get('completion_rate', 0))}</td>
                    </tr>
                </table>
            </div>
            
            <div class="data-card">
                <h3>Requirements Analysis</h3>
                <table class="data-table">
                    <tr>
                        <td>Fingerprinting Required</td>
                        <td>{format_number(para_data.get('fingerprinting_required', 0))}</td>
                    </tr>
                    <tr>
                        <td>Medical Clearance Required</td>
                        <td>{format_number(para_data.get('medical_required', 0))}</td>
                    </tr>
                    <tr>
                        <td>Multiple Requirements</td>
                        <td>{format_number(para_data.get('multiple_requirements', 0))}</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
    """


def generate_teacher_section(teacher_data):
    """
    Generate teacher analysis section
    
    Args:
        teacher_data (dict): Teacher analysis results
        
    Returns:
        str: HTML content for teacher section
    """
    return f"""
    <div class="section">
        <h2>Substitute Teachers Analysis</h2>
        <div class="data-grid">
            <div class="data-card">
                <h3>Renewal Status</h3>
                <table class="data-table">
                    <tr>
                        <td>Total Records</td>
                        <td>{format_number(teacher_data.get('total_records', 0))}</td>
                    </tr>
                    <tr>
                        <td>Eligible for Renewal</td>
                        <td>{format_number(teacher_data.get('total_eligible', 0))}</td>
                    </tr>
                    <tr>
                        <td>Completed</td>
                        <td>{format_number(teacher_data.get('completed', 0))}</td>
                    </tr>
                    <tr>
                        <td>Outstanding</td>
                        <td>{format_number(teacher_data.get('outstanding', 0))}</td>
                    </tr>
                    <tr class="highlight">
                        <td>Completion Rate</td>
                        <td>{format_percentage(teacher_data.get('completion_rate', 0))}</td>
                    </tr>
                </table>
            </div>
            
            <div class="data-card">
                <h3>Requirements Analysis</h3>
                <table class="data-table">
                    <tr>
                        <td>Fingerprinting Required</td>
                        <td>{format_number(teacher_data.get('fingerprinting_required', 0))}</td>
                    </tr>
                    <tr>
                        <td>Medical Clearance Required</td>
                        <td>{format_number(teacher_data.get('medical_required', 0))}</td>
                    </tr>
                    <tr>
                        <td>Multiple Requirements</td>
                        <td>{format_number(teacher_data.get('multiple_requirements', 0))}</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
    """


def generate_comparison_section(differences):
    """
    Generate comparison section
    
    Args:
        differences (dict): Comparison differences
        
    Returns:
        str: HTML content for comparison section
    """
    return f"""
    <div class="section">
        <h2>Period-over-Period Comparison</h2>
        <div class="data-grid">
            <div class="data-card">
                <h3>Paraprofessional Changes</h3>
                <table class="data-table">
                    <tr>
                        <td>Eligible Change</td>
                        <td>{differences.get('para_eligible', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Completed Change</td>
                        <td>{differences.get('para_completed', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Outstanding Change</td>
                        <td>{differences.get('para_outstanding', 'N/A')}</td>
                    </tr>
                    <tr class="highlight">
                        <td>Completion Rate Change</td>
                        <td>{differences.get('para_completion_rate', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div class="data-card">
                <h3>Teacher Changes</h3>
                <table class="data-table">
                    <tr>
                        <td>Eligible Change</td>
                        <td>{differences.get('teacher_eligible', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Completed Change</td>
                        <td>{differences.get('teacher_completed', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Outstanding Change</td>
                        <td>{differences.get('teacher_outstanding', 'N/A')}</td>
                    </tr>
                    <tr class="highlight">
                        <td>Completion Rate Change</td>
                        <td>{differences.get('teacher_completion_rate', 'N/A')}</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
    """


def generate_geographic_section(borough_data):
    """
    Generate geographic analysis section
    
    Args:
        borough_data (dict): Borough/geographic analysis results
        
    Returns:
        str: HTML content for geographic section
    """
    if not borough_data:
        return "<div class='section'><h2>Geographic Analysis</h2><p>No geographic data available.</p></div>"
    
    # Sort areas by total eligible count (para + teacher)
    sorted_areas = sorted(
        borough_data.items(),
        key=lambda x: x[1]['para_eligible'] + x[1]['teacher_eligible'],
        reverse=True
    )
    
    rows = []
    for area, data in sorted_areas:
        if data['para_eligible'] > 0 or data['teacher_eligible'] > 0:
            rows.append(f"""
                <tr>
                    <td>{area}</td>
                    <td>{format_number(data['para_eligible'])}</td>
                    <td>{format_number(data['para_completed'])}</td>
                    <td>{format_percentage(data['para_completion_rate'])}</td>
                    <td>{format_number(data['teacher_eligible'])}</td>
                    <td>{format_number(data['teacher_completed'])}</td>
                    <td>{format_percentage(data['teacher_completion_rate'])}</td>
                </tr>
            """)
    
    return f"""
    <div class="section">
        <h2>Geographic Analysis</h2>
        <div class="data-card full-width">
            <h3>Renewal Status by Borough/County</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Area</th>
                        <th>Para Eligible</th>
                        <th>Para Completed</th>
                        <th>Para Rate</th>
                        <th>Teacher Eligible</th>
                        <th>Teacher Completed</th>
                        <th>Teacher Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    </div>
    """


def generate_comparison_report(para_data, teacher_data, differences, output_dir):
    """
    Generate focused comparison report
    
    Args:
        para_data (dict): Paraprofessional analysis results
        teacher_data (dict): Teacher analysis results
        differences (dict): Comparison differences
        output_dir (str): Output directory for HTML file
        
    Returns:
        str: Path to generated HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYC Substitute Staff Renewal Comparison Report</title>
        <link rel="stylesheet" href="static/css/styles.css">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="Horizontal_logo_White_PublicSchools.png" alt="NYC Public Schools" class="logo">
                <h1>Substitute Staff Renewal Comparison Report</h1>
                <p class="timestamp">Generated: {timestamp}</p>
            </div>
            
            <div class="content">
                {generate_executive_summary(para_data, teacher_data, differences)}
                {generate_comparison_section(differences)}
            </div>
            
            <div class="footer">
                <p>© 2025 NYC Public Schools - HR School Support Analysis Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    output_path = os.path.join(output_dir, "combined_comparison.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

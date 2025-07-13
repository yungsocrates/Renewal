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
import shutil
import pandas as pd
from datetime import datetime
from data_processing import format_number, format_percentage


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
                <h3>Key Renewal Metrics</h3>
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
                    Interactive map showing substitute distribution and renewal completion rates across NYC boroughs and neighboring counties (Westchester, Nassau, Suffolk, Bergen, Hudson, Union, Essex, Rockland, Fairfield, Orange, Putnam, Dutchess, Ulster, Morris, Passaic, Somerset, Middlesex, Monmouth, Ocean, New Haven, Pennsylvania)
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
    RENEWAL_WORKSPACE = r"c:\Users\OFerreira3\Documents\Renewal"
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


def generate_comparison_report(para_data, teacher_data, differences, output_dir):
    """
    Generate a simplified comparison report focused on key metrics
    
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
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
            }}
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #2c3e50;
            }}
            .metric-label {{
                color: #7f8c8d;
                font-size: 0.9em;
                margin-top: 5px;
            }}
            .timestamp {{
                text-align: center;
                color: #7f8c8d;
                font-style: italic;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>NYC Substitute Staff Renewal Comparison Report</h1>
            
            <h2>Substitute Paraprofessionals (SPA)</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_number(para_data.get('total_eligible', 0))}</div>
                    <div class="metric-label">Total Eligible</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_number(para_data.get('total_complete', 0))}</div>
                    <div class="metric-label">Completed Renewal</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_number(para_data.get('total_outstanding', 0))}</div>
                    <div class="metric-label">Outstanding</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_percentage(para_data.get('total_complete', 0) / max(para_data.get('total_eligible', 1), 1) * 100)}</div>
                    <div class="metric-label">Completion Rate</div>
                </div>
            </div>
            
            <h2>Substitute Teachers (STE)</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_number(teacher_data.get('total_eligible', 0))}</div>
                    <div class="metric-label">Total Eligible</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_number(teacher_data.get('total_prc_pru_complete', 0))}</div>
                    <div class="metric-label">PRC & PRU Completed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_number(teacher_data.get('total_prc_pru_outstanding', 0))}</div>
                    <div class="metric-label">PRC & PRU Outstanding</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_percentage(teacher_data.get('total_prc_pru_complete', 0) / max(teacher_data.get('total_prc_pru_eligible', 1), 1) * 100)}</div>
                    <div class="metric-label">Completion Rate</div>
                </div>
            </div>
            
            <div class="timestamp">
                Generated on: {timestamp}
            </div>
        </div>
    </body>
    </html>
    """
    
    report_file = os.path.join(output_dir, 'comparison_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file
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

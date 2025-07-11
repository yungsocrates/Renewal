# NYC Public Schools Substitute Renewal Analytics Dashboard

A comprehensive, modular analytics tool for analyzing substitute teacher and paraprofessional renewal data for the New York City Department of Education. The application features a professional modular architecture with standardized NYC Publ## 📚 Function Referencec Schools branding and advanced geographic analysis ca## 📁 Project Structureabilities.

## 🏗️ Architecture Overview

This application follows a mo## 📊 Export Formatsular design pattern with clear separation of concerns:

### Core Modules

#### `substitute_renewal_analytics.py` - Main Application
**Purpose**: Main orchestration script that coordinates all analysis workflows
**Key Functions**:
- `main()` - Primary execution function that orchestrates entire analysis pipeline
- `generate_zipcode_choropleth()` - Creates ZIP code boundary visualization
- `copy_logo_to_output()` - Handles NYC Public Schools logo deployment
- `get_header_html()` - Generates standardized HTML headers with branding
- `get_professional_footer()` - Creates consistent footers with contact information

#### `data_processing.py` - Data Analysis Engine
**Purpose**: Core data loading, processing, and analysis functions
**Key Functions**:
- `load_csv_data(csv_path, data_type)` - Robust CSV loading with validation
- `analyze_substitute_paraprofessionals(df_para)` - Comprehensive SPA data analysis
- `analyze_substitute_teachers(df_teacher)` - Complete STE data analysis
- `calculate_differences(new_results, old_results)` - Period-over-period comparison
- `calculate_percentage_differences()` - Completion rate change analysis
- `calculate_teacher_percentage_differences()` - Teacher-specific rate analysis
- `format_number(num)` - Standardized number formatting for reports
- `format_percentage(num)` - Consistent percentage display formatting
- `format_metric_with_diff()` - Comparison display with change indicators

#### `geographic_analysis.py` - Geographic Intelligence
**Purpose**: ZIP code mapping, borough analysis, and geographic data processing
**Key Functions**:
- `map_zip_to_borough(postal_code)` - Maps ZIP codes to NYC boroughs/counties
- `get_zip_coordinates(zip_code)` - Returns lat/lon coordinates for ZIP codes
- `analyze_substitute_data_by_borough()` - Geographic distribution analysis

#### `geo_data.py` - Geographic Data Repository
**Purpose**: Centralized geographic data constants and mappings
**Key Data Structures**:
- `NYC_ZIP_TO_BOROUGH` - Comprehensive ZIP to borough/county mapping dictionary
- `ZIP_COORDINATES` - Latitude/longitude coordinates for all ZIP codes
- `AREA_COORDINATES` - Borough and county centroid coordinates for mapping
- Covers NYC (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
- Includes neighboring counties (Westchester, Nassau, Suffolk, Bergen, Hudson, Union, Essex, Rockland, Fairfield)

#### `visualizations.py` - Advanced Data Visualization
**Purpose**: Creates interactive charts, maps, and visual analytics
**Key Functions**:
- `create_visualization_charts()` - Generates comprehensive chart suite
- `create_nyc_borough_map()` - Interactive borough-level geographic visualization
- `create_dual_zipcode_heatmap()` - ZIP code density heatmaps for both groups
- `create_zipcode_choropleth_map_dual()` - Boundary-based choropleth visualization
- `create_zipcode_heatmap_dual()` - Dual-group heatmap generation
- `create_para_zipcode_heatmap()` - Paraprofessional-specific ZIP visualization
- `create_teacher_zipcode_heatmap()` - Teacher-specific ZIP visualization

#### `report_generation.py` - Professional Report Creation
**Purpose**: HTML report generation with professional styling and branding
**Key Functions**:
- `generate_html_report()` - Creates comprehensive HTML dashboard
- `generate_executive_summary()` - Executive-level summary section
- `generate_paraprofessional_section()` - Detailed SPA analysis section
- `generate_teacher_section()` - Comprehensive STE analysis section
- `generate_comparison_section()` - Period-over-period comparison display
- `generate_geographic_section()` - Geographic analysis reporting
- `generate_comparison_report()` - Focused comparison report generation

## 🚀 Key Features

### Geographic Capabilities
- **Advanced Borough Mapping**: Interactive NYC borough-level visualization covering all five boroughs
- **Tri-State Area Coverage**: Extends analysis to neighboring counties in NY, NJ, and CT
- **ZIP Code Intelligence**: Accurate ZIP code processing including ZIP+4 formats and decimal conversion
- **Choropleth Visualization**: Boundary-based ZIP code mapping with actual geographic boundaries
- **Dual-Group Analysis**: Simultaneous visualization of both teacher and paraprofessional data

### Data Processing Excellence
- **Modular Architecture**: Clean separation of data processing, visualization, and reporting
- **Robust Data Validation**: Comprehensive CSV loading with error handling and validation
- **Accurate Eligibility Counting**: Precise filtering excludes null, empty, and invalid Status values
- **Geographic Intelligence**: Centralized ZIP code to borough mapping with comprehensive coverage
- **Comparison Analytics**: Period-over-period analysis with automatic change detection

### Professional Reporting
- **Interactive Dashboard**: Modern, responsive HTML dashboard with NYC Public Schools branding
- **Animated Progress Bars**: Visual completion rate indicators with professional animations
- **Comprehensive Charts**: Plotly-powered visualizations with optimized sizing and professional styling
- **Executive Summary**: High-level metrics with key performance indicators
- **Geographic Reporting**: Borough and county-level breakdown with completion rates

### Advanced Visualizations
- **Stacked Bar Charts**: Revolutionary side-by-side comparison of SPA vs STE renewal status
- **Interactive Maps**: Plotly-powered geographic visualizations with hover details
- **Density Heatmaps**: ZIP code-based density analysis for both substitute groups
- **Choropleth Maps**: Boundary-accurate ZIP code visualization with toggle functionality
- **Professional Styling**: Consistent color schemes and responsive design

## 📊 Analysis Categories

### Substitute Paraprofessionals (SPA)
- **Eligibility Analysis**: Total eligible for renewal based on status criteria
- **Completion Tracking**: COMP vs OUT status breakdown with completion rates
- **Requirement Analysis**: Reasonable Assurance (RA) completion tracking
- **Specialized Requirements**: Days worked, ATAS, Child Abuse Workshop analysis
- **Multi-Requirement Tracking**: Combined requirement completion analysis
- **Suspension Analysis**: 2SS and 2SR suspension status tracking
- **Geographic Distribution**: Borough and county-level analysis

### Substitute Teachers (STE)
- **Category Analysis**: PRC (Certified) and PRU (Uncertified) breakdown
- **Completion Tracking**: Detailed requirement completion by category
- **Reasonable Assurance**: RA completion analysis for PRC/PRU groups
- **Special Categories**: PRL (On Leave) and PRR (Retirees) analysis
- **Requirements Breakdown**: Days worked, Child Abuse Workshop, other requirements
- **Suspension Tracking**: 2SS and 2SR suspension analysis
- **Geographic Distribution**: Borough and county-level completion rates

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Required packages (see `requirements.txt`)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nycdoe-substitute-renewal-analytics.git
   cd nycdoe-substitute-renewal-analytics
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place your CSV files in the project directory:
   - `substitute_paraprofessionals.csv` (current data)
   - `substitute_teachers.csv` (current data)
   - `substitute_paraprofessionals_old.csv` (optional - for comparison)
   - `substitute_teachers_old.csv` (optional - for comparison)

## 📈 Usage

### Standard Mode (Single Dataset Analysis)
```bash
python substitute_renewal_analytics.py
```

### Comparison Mode (Historical Data Comparison)
To enable comparison mode, place historical data files with "_old" suffix:
- `substitute_paraprofessionals_old.csv`
- `substitute_teachers_old.csv`

The script will automatically detect these files and:
- Calculate differences between current and historical data
- Display changes with ▲/▼ indicators in the HTML report
- Show percentage changes for completion rates
- Include comparison summaries in terminal output

### Programmatic Usage
```python
from substitute_renewal_analytics import main
from data_processing import analyze_substitute_paraprofessionals, analyze_substitute_teachers
from geographic_analysis import map_zip_to_borough, analyze_substitute_data_by_borough
from visualizations import create_visualization_charts, create_nyc_borough_map
from report_generation import generate_html_report

# Run full analysis
main()

# Or use individual modules
df_para = load_csv_data("substitute_paraprofessionals.csv", "para")
para_results = analyze_substitute_paraprofessionals(df_para)
```

## 📂 File Structure

```
├── substitute_renewal_analytics.py    # Main orchestration script
├── data_processing.py                 # Core data analysis functions
├── geographic_analysis.py             # ZIP code and borough analysis
├── geo_data.py                       # Geographic data constants
├── visualizations.py                 # Chart and map generation
├── report_generation.py              # HTML report creation
├── requirements.txt                  # Python dependencies
├── README.md                         # This documentation
├── DEPLOYMENT_GUIDE.md              # Deployment instructions
├── PROJECT_SUMMARY.md               # Project overview
├── CHANGELOG.md                     # Version history
└── renewal_reports/                 # Generated output directory
    ├── renewal_analytics_report.html
    ├── combined_overview.html
    ├── nyc_borough_map.html
    ├── nyc_zipcode_choropleth.html
    └── [additional chart files]
```

## 🗺️ Geographic Coverage

### NYC Boroughs (Complete Coverage)
- **Manhattan**: ZIP codes 10001-10282
- **Brooklyn**: ZIP codes 11201-11256  
- **Queens**: ZIP codes 11004-11005, 11101-11109, 11351-11697
- **Bronx**: ZIP codes 10451-10475
- **Staten Island**: ZIP codes 10301-10314

### Neighboring Counties
- **New York**: Westchester County, Nassau County, Suffolk County, Rockland County
- **New Jersey**: Bergen County, Hudson County, Union County, Essex County
- **Connecticut**: Fairfield County

## 📊 Output Reports

### Main Dashboard (`renewal_analytics_report.html`)
- Executive summary with key metrics
- Animated progress bars for completion rates
- Comprehensive analysis sections for both groups
- Interactive geographic visualizations
- Professional NYC Public Schools branding

### Geographic Visualizations
- **Borough Map**: Interactive map showing completion rates by area
- **ZIP Code Choropleth**: Boundary-accurate ZIP code visualization
- **Density Heatmaps**: ZIP code density analysis for both groups

### Analysis Charts
- **Combined Overview**: Side-by-side status comparison
- **Individual Group Charts**: Detailed breakdowns for SPA and STE
- **Comparison Charts**: Period-over-period analysis when historical data available

## 🔧 Configuration

### Data File Requirements
- CSV files must contain required columns (Status, Postal, etc.)
- ZIP codes can be in various formats (12345, 12345.0, 12345-6789)
- Geographic analysis requires valid US ZIP codes

### Customization Options
- Update `geo_data.py` to modify geographic mappings
- Modify `visualizations.py` for chart styling changes
- Customize HTML templates in `report_generation.py`
- Adjust analysis logic in `data_processing.py`
main()

# Or analyze individual datasets
import pandas as pd
df_para = pd.read_csv('substitute_paraprofessionals.csv')
para_results = analyze_substitute_paraprofessionals(df_para)
```

### Viewing Reports Locally
After running the analysis, open the generated HTML reports in your browser:

**Option 1: Direct File Opening**
- Navigate to the `renewal_reports` folder
- Double-click `renewal_analytics_report.html` to open in your default browser

**Option 2: Local Web Server (Recommended for embedded charts)**
For proper viewing of all embedded charts including the geographic map:
```bash
# Navigate to the reports directory
cd renewal_reports

# Start a local web server
python -m http.server 8000
```
Then visit `http://localhost:8000/renewal_analytics_report.html` in your browser.

## 🔄 Comparison Analytics

The tool supports historical data comparison to track changes over time:

### Key Features:
- **Automatic Detection**: Automatically detects "_old" CSV files for comparison
- **Change Indicators**: Visual indicators (▲ for increase, ▼ for decrease) in HTML reports
- **Completion Rate Tracking**: Percentage point changes in SPA and STE completion rates
- **Comprehensive Metrics**: Comparison across all analysis categories
- **Terminal Summary**: Quick overview of changes in command-line output

### Example Output:
```
📊 Comparison Mode: Old data files detected
  Para Old Data: ✓
  Teacher Old Data: ✓

Substitute Paraprofessionals:
  • Total Eligible: 15,234 (+234)
  • Completed: 12,567 (+189)
  • Completion Rate: 82.5% (+1.2%)
```

## 🗺️ ZIP Code Choropleth Map (NEW in v1.6.0)

- **Dual ZIP Code Choropleth**: Interactive map with true NYC ZIP code boundaries for both substitute paraprofessionals and teachers
- **Toggle Buttons**: Easily switch between para and teacher counts using top-right toggle buttons
- **Professional UI**: Title is left-aligned, buttons are top-right, and map is fully embedded in the HTML report
- **Accurate Boundaries**: Uses official NYC ZIP code boundary data (GeoPandas, Shapely, Plotly)
- **Seamless Integration**: Map is generated and embedded automatically in the analytics workflow and report
- **Improved Data Pipeline**: ZIP code aggregation logic matches heatmap logic for both groups
- **Modern Layout**: No overlap between title and buttons; map is visually clear and professional

## � Function Reference

### Core Data Processing Functions (`data_processing.py`)
- `load_substitute_data()`: Load and validate CSV files
- `calculate_completion_rates()`: Calculate renewal completion percentages
- `analyze_requirements()`: Analyze specific requirement compliance
- `generate_summary_statistics()`: Create statistical summaries
- `export_to_excel()`: Export data to Excel format
- `format_percentage()`: Format numbers as percentages
- `format_number()`: Format numbers with commas
- `safe_percentage()`: Calculate percentages with division by zero protection

### Geographic Analysis Functions (`geographic_analysis.py`)
- `map_zip_to_borough()`: Map ZIP codes to NYC boroughs
- `get_zip_coordinates()`: Get coordinates for ZIP codes
- `analyze_substitute_data_by_borough()`: Analyze data by borough
- `create_borough_summary()`: Create borough-level summaries
- `validate_zip_codes()`: Validate ZIP code format and existence
- `get_area_coordinates()`: Get coordinates for geographic areas

### Visualization Functions (`visualizations.py`)
- `create_completion_charts()`: Generate completion rate charts
- `create_heatmap()`: Create geographic heatmaps
- `create_comparison_charts()`: Generate comparison visualizations
- `create_trend_analysis()`: Create trend analysis charts
- `create_borough_map()`: Generate borough-level maps
- `create_zipcode_choropleth()`: Create ZIP code choropleth maps
- `style_plotly_chart()`: Apply consistent styling to charts
- `export_chart_as_image()`: Export charts as images

### Report Generation Functions (`report_generation.py`)
- `generate_html_report()`: Create comprehensive HTML reports
- `generate_executive_summary()`: Create executive summary sections
- `generate_detailed_analysis()`: Create detailed analysis sections
- `generate_comparison_section()`: Create comparison analysis sections
- `generate_geographic_section()`: Create geographic analysis sections
- `generate_recommendations()`: Create recommendations sections
- `embed_charts_in_html()`: Embed Plotly charts in HTML reports

### Geographic Data Repository (`geo_data.py`)
- `NYC_ZIP_TO_BOROUGH`: Dictionary mapping NYC ZIP codes to boroughs
- `ZIP_COORDINATES`: Dictionary with ZIP code coordinates
- `AREA_COORDINATES`: Dictionary with area/county coordinates

## 🚀 Advanced Usage

### Custom Analysis
```python
from data_processing import load_substitute_data, analyze_requirements
from geographic_analysis import analyze_substitute_data_by_borough
from visualizations import create_completion_charts

# Load your data
para_data = load_substitute_data('your_para_data.csv')
teacher_data = load_substitute_data('your_teacher_data.csv')

# Perform custom analysis
para_analysis = analyze_requirements(para_data, 'paraprofessional')
geographic_analysis = analyze_substitute_data_by_borough(para_data)

# Create custom visualizations
charts = create_completion_charts(para_analysis, 'Paraprofessionals')
```

### Custom Report Generation
```python
from report_generation import generate_html_report

# Generate custom report with specific sections
report_html = generate_html_report(
    para_data=para_data,
    teacher_data=teacher_data,
    include_comparison=True,
    include_geographic=True,
    output_file='custom_report.html'
)
```

## �📁 Project Structure

```
nycdoe-substitute-renewal-analytics/
├── substitute_renewal_analytics.py    # Main analysis script
├── requirements.txt                   # Python dependencies
├── README.md                         # This file
├── LICENSE                           # License file
├── .gitignore                        # Git ignore rules
├── netlify.toml                      # Netlify configuration
├── docs/                            # Documentation
│   ├── API.md                       # API documentation
│   └── examples/                    # Usage examples
├── static/                          # Static assets for web deployment
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   └── images/                     # Images and logos
└── renewal_reports/                 # Generated reports (auto-created)
    ├── renewal_analytics_report.html    # Main dashboard
    ├── paraprofessional_overview.html   # SPA visualizations
    ├── teacher_overview.html           # STE visualizations
    ├── combined_comparison.html        # Comparative analysis
    ├── nyc_borough_map.html           # Geographic borough map
    └── exports/                       # Exported files
        ├── *.pdf
        ├── *.xlsx
        └── *.csv
```

## 🌐 Web Deployment

This project is configured for easy deployment to Netlify:

1. **Fork/Clone** this repository to your GitHub account
2. **Connect** your GitHub repo to Netlify
3. **Deploy** - Netlify will automatically build and deploy your dashboard

The dashboard will be available at your Netlify URL and will automatically update when you push changes to your repository.

### Environment Variables (if needed)
- `PYTHON_VERSION`: Python version (default: 3.8)

## 📋 Data Requirements

### CSV File Structure

#### Substitute Paraprofessionals CSV
Required columns:
- `Status`: Completion status ('Out', 'COMPL')
- `Reasonable Assurance`: RA status
- `Days Wrkd in School Year`: Number of days worked
- `Address or School Zip`: ZIP code for geographic mapping
- Various workshop and requirement columns

#### Substitute Teachers CSV
Required columns:
- `Status`: Completion status ('Out', 'COMPL')
- `Certified`: Certification status ('Y', 'N')
- `Renewal Classification`: Category classification
- `Reasonable Assurance`: RA status
- `Address or School Zip`: ZIP code for geographic mapping
- Various requirement columns

## � Troubleshooting

### Common Issues and Solutions

#### "No module named 'plotly'" Error
```bash
pip install plotly
```
Or if using conda:
```bash
conda install -c plotly plotly
```

#### ZIP Code Not Found in Borough Mapping
- **Issue**: ZIP code not recognized in geographic analysis
- **Solution**: Check `geo_data.py` for supported ZIP codes. Add missing ZIP codes to `NYC_ZIP_TO_BOROUGH` dictionary if needed.

#### Empty or Corrupted CSV Files
- **Issue**: CSV files are empty or have formatting issues
- **Solution**: Verify CSV files have required columns and data. Check for special characters or encoding issues.

#### Memory Issues with Large Datasets
- **Issue**: Script runs out of memory with large CSV files
- **Solution**: Process data in chunks or increase system memory allocation.

#### Charts Not Displaying in HTML Report
- **Issue**: Plotly charts not rendering in HTML reports
- **Solution**: Check internet connection for CDN resources or use offline mode in Plotly configuration.

### Debug Mode
Enable debug mode in `substitute_renewal_analytics.py`:
```python
DEBUG = True  # Set to True for detailed logging
```

## �📊 Export Formats

The dashboard supports exporting data in multiple formats:
- **PDF**: Complete analytical report with charts
- **Excel**: Detailed data tables with multiple worksheets
- **CSV**: Raw data exports for further analysis
- **JSON**: Structured data for API integration

## 🔧 Configuration

Key configuration options in `substitute_renewal_analytics.py`:

```python
# Workspace and output directories
RENEWAL_WORKSPACE = r"path/to/your/data"
OUTPUT_DIR = "renewal_reports"

# Completion thresholds
COMPLETION_THRESHOLD = 0.8  # 80% of requirements must be complete
```

## 📈 Analytics Metrics

### Key Performance Indicators (KPIs)
- **Completion Rates**: Overall renewal completion percentages
- **Requirement Analysis**: Breakdown by specific requirements
- **Time-based Trends**: Historical completion patterns
- **Geographic Distribution**: Borough-level completion analysis with ZIP code mapping
- **Borough Insights**: NYC borough comparison with completion rates and eligible counts

### Business Rules
- **Days Worked Only**: ≤19 days worked, other requirements complete
- **Autism Workshop Only**: ≥20 days worked, only autism workshop incomplete
- **ATAS Only**: ≥20 days worked, only ATAS requirement incomplete
- **Multiple Requirements**: Multiple incomplete requirements

## 🏗️ Modular Architecture Benefits

The project uses a modular architecture with clear separation of concerns:

### Maintainability
- **Single Responsibility**: Each module has a specific purpose
- **Easy Updates**: Changes to one module don't affect others
- **Code Reusability**: Functions can be imported and used across different scripts

### Scalability
- **Easy Extension**: New analysis features can be added without modifying existing code
- **Performance**: Selective imports reduce memory usage
- **Testing**: Each module can be tested independently

### Development Efficiency
- **Parallel Development**: Multiple developers can work on different modules simultaneously
- **Debugging**: Issues can be isolated to specific modules
- **Documentation**: Each module is self-documented with clear function purposes

### Geographic Data Centralization
- **Consistent Mapping**: All ZIP code and geographic data centralized in `geo_data.py`
- **Easy Updates**: Geographic boundaries or new areas can be added in one place
- **Data Integrity**: Eliminates hardcoded geographic data scattered across files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **HR School Support Analysis Team** - *Initial work*

## 🙏 Acknowledgments

- NYC Department of Education
- HR School Support Team
- All contributors to this project

## 📞 Support

For questions or support, please contact:
- Email: hr-school-support@schools.nyc.gov
- Documentation: [GitHub Wiki](https://github.com/yourusername/nycdoe-substitute-renewal-analytics/wiki)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

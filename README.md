# NYC Public Schools Substitute Renewal Analytics Dashboard

A comprehensive analytics tool for analyzing substitute teacher and paraprofessional renewal data for the New York City Department of Education. Features modern, professional styling with standardized NYC Public Schools branding.

## 🚀 Features

- **Geographic Borough Map**: Interactive NYC borough-level visualization with accurate ZIP code mapping
  - Plotly-powered map showing all five NYC boroughs (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
  - Color-coded by completion rates with size indicating total eligible counts
  - Dual legends for both teachers and paraprofessionals positioned to avoid overlap
  - Standalone HTML file generation for local viewing and report embedding
  - Accurate ZIP code handling including ZIP+4 formats and decimal conversion
- **Advanced Stacked Bar Visualization**: Revolutionary side-by-side comparison of SPA vs STE renewal status
  - Single chart showing both substitute groups with detailed status breakdowns
  - Percentage labels within each bar segment for immediate insights
  - Professional total count annotations above each bar
  - Interactive hover tooltips with detailed breakdowns
- **Accurate Data Processing**: Precise eligibility counting with empty row filtering
  - Excludes null, empty, and meaningless Status values for accurate counts
  - Debug verification ensures reported totals match filtered datasets
  - Real-time count validation and filtering transparency
  - Enhanced ZIP code mapping with string conversion and format standardization
- **Comprehensive Data Analysis**: Analyzes substitute teacher and paraprofessional renewal data
- **Comparison Analytics**: Compare current data with historical data to track changes over time
- **Enhanced Visualizations**: Plotly-powered charts with optimized sizing and readability
  - Responsive chart containers (900px width) fit perfectly within report layout
  - Professional color schemes with distinct status categories
  - Improved text sizing and reduced chart width eliminates scrollbars
  - Optimized stacked bar chart dimensions for seamless HTML integration
- **Professional HTML Dashboard**: Modern, responsive dashboard with NYC Public Schools branding
- **Animated Progress Bars**: Visual completion rate indicators with animated progress bars in the executive summary
- **Completion Rate Tracking**: Monitor SPA and STE completion rate changes with percentage differences
- **Export Capabilities**: Export reports to PDF, Excel, and CSV formats
- **Automated Categorization**: Intelligently categorizes renewal requirements and completion status
- **Standardized Branding**: Official NYC Public Schools logo and consistent color scheme throughout
- **Enhanced Status Recognition**: Improved logic to handle both 'COMPL'/'COMP' as complete and 'OUT'/'Out' as outstanding

## 📊 Analysis Categories

### Substitute Paraprofessionals (SPA)
- Total eligible for renewal
- Completion status breakdown
- Reasonable Assurance (RA) analysis
- Days worked requirements
- ATAS and workshop requirements
- Suspension analysis

### Substitute Teachers (STE)
- PRC (Certified) and PRU (Uncertified) analysis
- Requirements completion tracking
- Special categories (On Leave, Retirees)
- Detailed requirement breakdown

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
from substitute_renewal_analytics import main, analyze_substitute_paraprofessionals, analyze_substitute_teachers

# Run full analysis
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

## 📁 Project Structure

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

## 📊 Export Formats

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

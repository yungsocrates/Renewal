# NYCDOE Substitute Renewal Analytics Dashboard

A comprehensive analytics tool for analyzing substitute teacher and paraprofessional renewal data for the New York City Department of Education.

## 🚀 Features

- **Comprehensive Data Analysis**: Analyzes substitute teacher and paraprofessional renewal data
- **Interactive Visualizations**: Plotly-powered charts and graphs
- **HTML Dashboard**: Professional, responsive dashboard with key metrics
- **Export Capabilities**: Export reports to PDF, Excel, and CSV formats
- **Automated Categorization**: Intelligently categorizes renewal requirements and completion status

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
   - `substitute_paraprofessionals.csv`
   - `substitute_teachers.csv`

## 📈 Usage

### Command Line
```bash
python substitute_renewal_analytics.py
```

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
    ├── renewal_analytics_report.html
    ├── paraprofessional_overview.html
    ├── teacher_overview.html
    ├── combined_comparison.html
    └── exports/                     # Exported files
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
- Various workshop and requirement columns

#### Substitute Teachers CSV
Required columns:
- `Status`: Completion status ('Out', 'COMPL')
- `Certified`: Certification status ('Y', 'N')
- `Renewal Classification`: Category classification
- `Reasonable Assurance`: RA status
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
- **Geographic Distribution**: Analysis by location/district

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

# Changelog

All notable changes to the NYCDOE Substitute Renewal Analytics Dashboard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-01-18

### Added
- **Standardized NYC Public Schools Branding**: Consistent header/footer styling with official white logo
- **Professional Header Layout**: Bolded headers with proper logo sizing and positioning  
- **Dual Contact Footer**: Added both subparajobs@schools.nyc.gov and subteacherjobs@schools.nyc.gov contact emails
- **DOE Property Statement**: Professional footer with department ownership acknowledgment

### Enhanced
- **Updated Report Titles**: Removed "NYCDOE" in favor of "NYC Public Schools" for official branding
- **Logo Integration**: Added copy_logo_to_output() function for consistent logo placement
- **Header HTML Generation**: Standardized get_header_html() function for uniform appearance
- **Professional Footer**: Enhanced get_professional_footer() with contact information and branding
- **Visual Design**: Improved header layout with proper spacing and proportional logo sizing

### Fixed
- Header width and alignment issues
- Logo size optimization (reduced to 80px for professional appearance)
- Removed duplicate and conflicting CSS rules
- Improved header container layout and positioning

## [1.1.0] - 2025-07-02

### Added
- **Historical Data Comparison**: Support for comparing current data with historical data
- **Automatic Old File Detection**: Automatically detects and processes "_old" CSV files
- **Change Indicators**: Visual ▲/▼ indicators in HTML reports showing increases/decreases
- **Completion Rate Tracking**: Percentage point changes for SPA and STE completion rates
- **Comparison Mode**: Terminal output shows changes with +/- indicators
- **Enhanced HTML Dashboard**: Updated dashboard with difference indicators and trend analysis
- **Comprehensive Metrics Comparison**: All analysis categories now support historical comparison

### Enhanced
- HTML report generation now includes historical comparison data
- Terminal summary output shows changes when historical data is available
- Error handling for missing old data files
- Documentation updated with comparison mode instructions

### Technical Improvements
- Added `calculate_differences()` function for numeric change calculations
- Added `calculate_percentage_differences()` functions for completion rate tracking
- Enhanced `generate_html_report()` to display comparison data
- Updated main analysis pipeline to support dual-dataset processing

## [1.0.0] - 2025-07-01

### Added
- Initial release of NYCDOE Substitute Renewal Analytics Dashboard
- Comprehensive analysis for substitute paraprofessionals (SPA) and substitute teachers (STE)
- Interactive Plotly visualizations with bar charts and pie charts
- HTML dashboard with responsive design
- Export functionality for multiple formats:
  - PDF reports with professional formatting
  - Excel workbooks with multiple worksheets
  - CSV files for data analysis
  - JSON files for API integration
- Automated categorization based on business rules:
  - Days worked requirements (≤19 vs ≥20 days)
  - Reasonable Assurance (RA) status tracking
  - Autism Workshop completion analysis
  - ATAS (State Exam) requirements
  - Suspension status (2SS, 2SR)
- PRC (Certified) and PRU (Uncertified) teacher classification
- Special categories for teachers on leave and retirees
- GitHub integration and Netlify deployment configuration
- Comprehensive documentation and README
- MIT License

### Features
- **Data Processing**: Intelligent parsing of CSV files with error handling
- **Business Logic**: Accurate implementation of NYCDOE renewal requirements
- **Visualizations**: Interactive charts showing completion rates and breakdowns
- **Responsive Design**: Mobile-friendly dashboard layout
- **Export Options**: Multiple output formats for different use cases
- **Web Deployment**: Ready for GitHub and Netlify deployment
- **Error Handling**: Graceful handling of missing data and dependencies

### Technical Details
- Python 3.7+ compatibility
- Pandas for data manipulation
- Plotly for interactive visualizations
- ReportLab for PDF generation
- OpenPyXL for Excel export
- Responsive CSS with print support
- Netlify configuration for automatic deployment

### Performance
- Handles datasets with 14,000+ records efficiently
- Optimized memory usage for large CSV files
- Fast chart generation with Plotly
- Minimal dependencies for easy deployment

### Security
- No sensitive data exposure in exports
- Safe file handling with proper validation
- Clean separation of data and presentation logic

## [Unreleased]

### Planned Features
- Database integration for live data updates
- Advanced filtering and search capabilities
- Historical trend analysis
- Email notification system for report generation
- API endpoints for programmatic access
- Advanced data visualization options
- User authentication and role-based access
- Automated scheduling for report generation

### Improvements Under Consideration
- Performance optimizations for very large datasets
- Additional export formats (PowerPoint, Word)
- Integration with NYCDOE systems
- Real-time dashboard updates
- Mobile app companion
- Advanced analytics and machine learning insights

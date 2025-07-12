# Changelog

All notable changes to the NYCDOE Substitute Renewal Analytics Dashboard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2025-07-09

### Added
- **Dual ZIP Code Choropleth Map**: Interactive map with true NYC ZIP code boundaries for both substitute paraprofessionals and teachers
  - Toggle buttons at top right to switch between para and teacher counts
  - Title is left-aligned, buttons are top-right, and map is fully embedded in the HTML report
  - Uses official NYC ZIP code boundary data (GeoPandas, Shapely, Plotly)
  - Seamless integration with analytics workflow and report
  - ZIP code aggregation logic matches heatmap logic for both groups
  - No overlap between title and buttons; map is visually clear and professional

### Enhanced
- Improved map UI/UX for all interactive geographic visualizations
- Documentation updated to reflect new map features and layout

## [1.5.0] - 2025-01-17

### Added
- **Interactive NYC Borough Map**: Geographic visualization of substitute renewal data
  - Plotly-powered interactive map showing all five NYC boroughs
  - Color-coded completion rates with size indicating total eligible counts
  - Dual data visualization for both teachers and paraprofessionals
  - Accurate ZIP code to borough mapping with enhanced format handling
  - Standalone HTML file generation (`nyc_borough_map.html`) for local viewing
  - Seamless integration with main dashboard via iframe embedding
- **Enhanced ZIP Code Processing**: Robust geographic data handling
  - Converts all postal codes to strings for consistent processing
  - Handles ZIP+4 format (e.g., "10001-1234") and decimal conversions
  - Standardized ZIP code mapping to NYC boroughs with debugging verification
  - Improved data accuracy with comprehensive format support

### Enhanced
- **Borough Analysis Accuracy**: Simplified and improved filtering logic
  - Consistent eligibility filtering using Status field only (COMP vs OUT)
  - Realistic distribution across all five NYC boroughs
  - Accurate completion counts and rates for geographic analysis
  - Enhanced data debugging and verification outputs
- **Visual Design Improvements**: Professional legend and colorbar positioning
  - Positioned colorbars on opposite sides of the map to prevent overlap
  - Vertical legend titles for better space utilization
  - Clear distinction between teacher and paraprofessional data
  - Enhanced map readability and professional presentation
- **Local Development Workflow**: Improved testing and viewing capabilities
  - Added local web server instructions for proper iframe viewing
  - Enhanced documentation for local development and testing
  - Better integration between standalone map and main dashboard

### Technical
- Implemented `create_nyc_borough_map()` function with Plotly Offline
- Added comprehensive ZIP code validation and mapping logic
- Enhanced borough assignment with debugging and verification
- Improved HTML generation with proper iframe integration
- Added geographic data processing with error handling

## [1.4.1] - 2025-07-08

### Enhanced
- **Chart Sizing Optimization**: Perfect fit within HTML layout
  - Reduced stacked bar chart width from 1500px to 900px for seamless integration
  - Adjusted iframe width to 1000px to eliminate horizontal scrollbars
  - Optimized chart dimensions maintain readability while fitting within white background
  - All visualizations now perfectly contained within report layout boundaries
- **Visual Integration**: Charts seamlessly integrate with report styling
  - No more overflow or scrolling issues in main dashboard
  - Professional presentation with charts fitting within design constraints
  - Maintained text readability and hover functionality at optimized size

### Technical
- Fine-tuned Plotly chart width parameters for optimal HTML integration
- Adjusted iframe dimensions to prevent layout overflow
- Verified chart responsiveness across different container sizes

## [1.4.0] - 2025-07-08

### Added
- **Advanced Stacked Bar Visualization**: Revolutionary SPA vs STE comparison chart
  - Single visualization showing both Substitute Paraprofessionals and Teachers
  - Each bar broken down by renewal status (Completed, Outstanding by category)
  - Percentage labels within each bar segment for immediate insight
  - Total eligible counts displayed above each bar with professional styling
  - Interactive hover tooltips with detailed breakdowns
- **Enhanced Chart Readability**: Improved text sizing and container dimensions
  - Larger text in stacked bar segments (size 12, Arial Black font)
  - Expanded chart containers (1500x850px) to eliminate scrollbars
  - Better spacing and positioning of total count annotations
  - Professional color scheme with distinct status categories

### Enhanced
- **Data Accuracy**: Fixed empty row filtering for precise eligibility counts
  - Properly excludes null, empty, and meaningless Status values
  - Accurate count verification: SPA shows 14,305 (not 14,311) after removing 6 empty rows
  - Debug logging shows exact filtering process and row counts
- **Visual Impact**: Combined overview chart replaces separate bar charts
  - Side-by-side comparison of SPA (14,305 eligible) vs STE (10,574 eligible)
  - Color-coded status categories for immediate pattern recognition
  - Professional legend positioning and chart spacing
- **User Experience**: Larger chart containers prevent scrolling issues
  - All visualizations now properly fit within browser viewports
  - Consistent sizing across main combined chart and detailed views
  - Professional annotations with bordered text boxes

### Technical
- Implemented advanced Plotly stacked bar charts with custom styling
- Added percentage calculation and display logic for each status segment
- Enhanced data filtering to exclude empty/null rows from eligibility counts
- Improved chart container sizing and responsive design
- Added professional annotation styling with background and borders

## [1.3.0] - 2025-07-08

### Added
- **Animated Progress Bars**: Interactive completion rate visualizations in executive summary
  - Visual progress bars showing SPA and STE completion percentages
  - Smooth animations with moving stripe effects
  - Real-time completion counts (e.g., "6,502 of 14,311 completed")
  - Professional gradient styling with green color scheme
- **Enhanced Status Recognition**: Improved completion status logic
  - Support for both 'COMPL' and 'COMP' as complete statuses
  - Support for both 'OUT' and 'Out' as outstanding statuses
  - More robust status detection across all data types

### Enhanced
- **Executive Summary Visual Appeal**: Progress bars make completion rates immediately visible
- **User Experience**: Interactive hover effects on progress bar cards
- **Professional Animation**: CSS keyframe animations for visual enhancement
- **Responsive Design**: Progress bars adapt to all screen sizes

### Technical
- Added CSS progress bar styling with gradient backgrounds
- Implemented keyframe animations for moving stripe effects
- Enhanced metric card layout with progress indicator support
- Improved status detection logic in analysis functions

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

### Refactor
- Major refactor: Full modularization of codebase for maintainability, clarity, and ease of extension.
    - All data processing and analysis logic moved to `data_processing.py`.
    - Geographic/borough analysis moved to `geographic_analysis.py`.
    - All chart/map generation moved to `visualizations.py`.
    - HTML report and asset generation moved to `report_generation.py`.
    - Main script (`substitute_renewal_analytics_cleaned.py`) now only contains workflow logic and `main()`.
- Modularization benefits:
    - Each module now has a single, clear responsibility (data processing, geographic analysis, visualization, or reporting).
    - Easier to test, maintain, and extend each part of the codebase independently.
    - New features or business rules can be added by updating only the relevant module.
    - Documentation and onboarding are simpler for new developers.
- Updated documentation to reflect new modular structure and provide detailed usage and developer notes.

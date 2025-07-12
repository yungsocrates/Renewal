# NYC Public Schools Substitute Renewal Analytics Dashboard

## Overview
This project provides a comprehensive analytics and reporting solution for substitute teacher and paraprofessional renewal data in NYC Public Schools. The codebase is fully modularized for maintainability, clarity, and ease of extension.

## Project Structure

- **substitute_renewal_analytics_cleaned.py**: Main orchestration script. Handles workflow, data loading, and calls all modularized functions. Contains only the `main()` function and top-level logic. No analysis or visualization logic is present here.
- **data_processing.py**: Responsible for all data loading, cleaning, and core analysis logic for paraprofessionals and teachers. Includes utility functions for formatting and calculations. This is where all business rules and eligibility logic are implemented.
- **geographic_analysis.py**: Handles all geographic and borough/county-based analysis, including ZIP-to-borough mapping, aggregation, and summary statistics by area. Designed for easy extension to new geographies or grouping schemes.
- **visualizations.py**: Contains all chart and map generation functions, including borough maps, ZIP code choropleths, and stacked bar/overview charts. Uses Plotly for interactive, offline HTML output. No data processing logic is present here.
- **report_generation.py**: Handles HTML report and asset generation, including professional NYC DOE branding, header/footer creation, and copying static assets (logos, CSS). All report layout and export logic is here.

## Key Modules and Functions

### data_processing.py
- `load_csv_data(path, label)`: Loads and cleans CSV data for a given group.
- `analyze_substitute_paraprofessionals(df)`: Analyzes paraprofessional renewal status, requirements, and eligibility.
- `analyze_substitute_teachers(df)`: Analyzes teacher renewal status, requirements, and eligibility.
- `calculate_differences(new, old)`, `calculate_percentage_differences(new, old)`, `calculate_teacher_percentage_differences(new, old)`: Calculate differences and percentage changes between datasets.
- Utility: `format_number`, `format_percentage`, `safe_int_conversion`.

### geographic_analysis.py
- `map_zip_to_borough(zip)`: Maps ZIP codes to NYC boroughs.
- `get_zip_coordinates(zip)`: Returns coordinates for a given ZIP code.
- `analyze_substitute_data_by_borough(df_para, df_teacher)`: Aggregates and summarizes data by borough/county.

### visualizations.py
- `create_visualization_charts(para_results, teacher_results, output_dir)`: Generates all summary and breakdown charts.
- `create_nyc_borough_map(borough_data, output_dir)`: Generates interactive borough-level map.
- `create_dual_zipcode_heatmap(...)`, `create_zipcode_choropleth_map_dual(...)`, `generate_zipcode_choropleth()`: Advanced geographic visualizations.

### report_generation.py
- `generate_html_report(...)`: Creates the main HTML dashboard report, embedding all charts and maps.
- `generate_comparison_report(...)`: (If present) Generates a comparison-focused report.
- `copy_logo_to_output(output_dir)`: Copies branding assets to output directory.
- `get_header_html(...)`, `get_professional_footer(...)`: Generates standardized header/footer HTML.

## Usage

1. Place your latest CSV data files in the project directory:
   - `substitute_paraprofessionals.csv`
   - `substitute_teachers.csv`
   - (Optional) `substitute_paraprofessionals_old.csv`, `substitute_teachers_old.csv` for comparison mode
2. Run the main script:
   ```bash
   python substitute_renewal_analytics_cleaned.py
   ```
3. Output will be generated in the `renewal_reports/` directory, including:
   - `renewal_analytics_report.html` (main dashboard)
   - All charts and maps as standalone HTML files
   - Copied branding assets

## Developer Notes
- **Modularization:** All logic is separated by concern. Add new analysis or visualizations by extending the appropriate module.
- **Extensibility:** To add new requirements, business rules, or visualizations, update only the relevant module.
- **Testing:** Each module can be tested independently. The main script is responsible only for orchestration.
- **Deployment:** See `DEPLOYMENT_GUIDE.md` for GitHub/Netlify deployment instructions.

## License
MIT License. See `LICENSE` for details.

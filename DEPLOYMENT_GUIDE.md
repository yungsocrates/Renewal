# GitHub and Netlify Deployment Guide

This guide will help you deploy the NYC Public Schools Substitute Renewal Analytics Dashboard to GitHub and then publish it to Netlify for web access.

## 🚀 Quick Start

### Step 1: Prepare Your Repository

1. **Initialize Git repository**:
   ```bash
   cd c:\Users\OFerreira3\Documents\Renewal
   git init
   git add .
   git commit -m "Initial commit: NYC Public Schools Substitute Renewal Analytics Dashboard"
   ```

2. **Create GitHub repository**:
   - Go to [GitHub.com](https://github.com) and create a new repository
   - Name it: `nyc-public-schools-substitute-renewal-analytics`
   - Make it public for Netlify deployment
   - Don't initialize with README (we already have one)

3. **Connect local repository to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/nyc-public-schools-substitute-renewal-analytics.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Netlify

1. **Go to [Netlify.com](https://netlify.com)** and sign up/login
2. **Click "New site from Git"**
3. **Connect to GitHub** and select your repository
4. **Configure build settings**:
   - Build command: `python substitute_renewal_analytics.py`
   - Publish directory: `renewal_reports`
   - Environment variables: `PYTHON_VERSION=3.8`

5. **Deploy!** - Netlify will automatically build and deploy your dashboard

## 📁 Project Structure Overview

```
nyc-public-schools-substitute-renewal-analytics/
├── substitute_renewal_analytics.py    # Main analytics script
├── requirements.txt                   # Python dependencies
├── README.md                         # Project documentation
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
├── netlify.toml                      # Netlify configuration
├── package.json                      # Project metadata
├── CHANGELOG.md                      # Version history
├── static/                           # Static web assets
│   └── css/
│       └── styles.css               # Additional CSS styles
└── renewal_reports/                 # Generated reports (auto-created)
    ├── renewal_analytics_report.html # Main dashboard
    ├── *.html                       # Chart files
    └── exports/                     # Exported data files
        ├── *.pdf                    # PDF reports
        ├── *.xlsx                   # Excel files
        ├── *.csv                    # CSV exports
        └── *.json                   # JSON data
```

## 🔧 Configuration Files Explained

### `netlify.toml`
```toml
[build]
  publish = "renewal_reports"          # Directory to publish
  command = "python substitute_renewal_analytics.py"  # Build command

[build.environment]
  PYTHON_VERSION = "3.8"              # Python version for build

[[redirects]]
  from = "/*"
  to = "/renewal_analytics_report.html"  # Default page
  status = 200
```

### `requirements.txt`
Core dependencies for the analytics dashboard:
- `pandas` - Data manipulation
- `plotly` - Interactive visualizations  
- `numpy` - Numerical computing
- `openpyxl` - Excel export (optional)
- `reportlab` - PDF export (optional)

### `.gitignore`
Excludes sensitive and generated files:
- CSV data files (contains PII)
- Generated reports
- Python cache files
- Environment files

## 🌐 Web Deployment Features

### Automatic Updates
- Push changes to GitHub → Netlify automatically rebuilds
- No manual deployment steps required
- Version history preserved in Git

### Export Capabilities
The dashboard includes multiple export formats:

1. **PDF Reports** - Professional formatted reports
2. **Excel Workbooks** - Multi-sheet data analysis
3. **CSV Files** - Raw data for further analysis
4. **JSON Data** - API-ready structured data

### Responsive Design
- Mobile-friendly dashboard
- Print-optimized layouts
- Accessibility features included

## 📊 Data Management

### Security Considerations
- **Never commit CSV files** containing PII to GitHub
- Use environment variables for sensitive configuration
- The `.gitignore` file protects sensitive data

### Data Updates
To update with new data:
1. Replace CSV files locally
2. Run the script: `python substitute_renewal_analytics.py`
3. Commit and push changes
4. Netlify automatically rebuilds with new data

## 🔍 Monitoring and Maintenance

### Build Logs
- Check Netlify build logs for any issues
- Python errors will be visible in deployment logs
- Build time typically 2-5 minutes

### Performance Optimization
- Large datasets (>50k records) may need optimization
- Consider data sampling for very large files
- Use CSV chunking for massive datasets

### Dependencies Management
Keep dependencies updated:
```bash
pip install --upgrade pandas plotly numpy
pip freeze > requirements.txt
```

## 🆘 Troubleshooting

### Common Issues

1. **Build Fails - Python Version**
   - Ensure Python 3.7+ specified in `netlify.toml`
   - Check `requirements.txt` for version conflicts

2. **Missing Dependencies**
   - Add missing packages to `requirements.txt`
   - Test locally before deploying

3. **CSV File Not Found**
   - Ensure CSV files are in correct location
   - Check file names match exactly
   - Verify `.gitignore` isn't excluding needed files

4. **Charts Not Displaying**
   - Check Plotly version compatibility
   - Verify output directory permissions
   - Ensure all HTML files are generated

### Getting Help

- **GitHub Issues**: Report bugs and feature requests
- **Netlify Support**: For deployment-specific issues
- **Documentation**: Check README.md for detailed usage

## 🎯 Next Steps

### Enhancements You Can Add

1. **Database Integration**
   - Connect to live data sources
   - Real-time updates

2. **Advanced Analytics**
   - Trend analysis over time
   - Predictive modeling

3. **User Authentication**
   - Role-based access control
   - Secure data handling

4. **API Integration**
   - REST API for data access
   - Webhook notifications

5. **Advanced Visualizations**
   - Geographic mapping
   - Interactive filtering
   - Custom date ranges

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request
5. Deploy via Netlify preview

## 📈 Success Metrics

Your deployed dashboard will provide:
- **Real-time access** to renewal analytics
- **Professional reports** for stakeholders
- **Data export capabilities** for further analysis
- **Mobile accessibility** for field staff
- **Version control** for all changes
- **Automatic backups** via Git history

## 🎉 Congratulations!

Your NYCDOE Substitute Renewal Analytics Dashboard is now ready for GitHub and Netlify deployment. This professional-grade analytics tool will provide valuable insights into substitute teacher and paraprofessional renewal data.

**Live URL**: After deployment, your dashboard will be available at:
`https://YOUR_SITE_NAME.netlify.app`

Happy analyzing! 📊✨

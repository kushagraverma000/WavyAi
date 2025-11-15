# 🌊 Real ARGO Data Setup Guide

Your WavyAI system now has **automated data fetching** from official ARGO sources! This guide will help you set up real oceanographic data to power your AI assistant.

## 🚀 Quick Start (Recommended)

### Option 1: Automated Setup Script
```bash
# Run the automated setup script
python setup_real_data.py
```

This script will:
- ✅ Download recent ARGO data from official sources
- ✅ Load data into your database
- ✅ Make your system ready with real ocean data

### Option 2: Web Interface Setup
1. **Start your application:**
   ```bash
   docker-compose up -d
   cd frontend && npm run dev
   ```

2. **Open the setup page:** http://localhost:3000/setup

3. **Choose your data source:**
   - **"Fetch Real Data"** - Downloads from official ARGO sources
   - **"Initialize Sample Data"** - Creates realistic test data

## 📊 What Data Gets Loaded

### Real ARGO Data Sources:
- **GDAC (Global Data Assembly Centre)**: https://data-argo.ifremer.fr
- **AOML (Atlantic Oceanographic)**: https://www.aoml.noaa.gov/ftp/pub/phod/argo
- **USGODAE**: https://usgodae.org/pub/outgoing/argo

### Data Coverage:
- 🌍 **Global ocean coverage**
- 📅 **Last 30 days of data** (configurable)
- 🌡️ **Temperature profiles**
- 🧂 **Salinity measurements**
- 📏 **Pressure/depth data**
- 🧪 **Biogeochemical data** (oxygen, chlorophyll, nitrate, pH)
- 🏷️ **Quality control flags**

## 🔧 Manual Setup (Advanced)

### Install Dependencies
```bash
cd backend
pip install xarray==2023.12.0 netcdf4==1.6.5 pandas==2.1.4 google-generativeai==0.3.2
```

### Run Data Fetcher
```bash
cd backend
python scripts/fetch_and_load_argo_data.py --days 30 --max-files 50 --init-db
```

### Parameters:
- `--days`: Days back to fetch (default: 30)
- `--max-files`: Maximum files to download (default: 50)
- `--init-db`: Initialize database tables

## 🎯 Using Your Real Data

Once data is loaded, your AI assistant can answer questions like:

### 🤖 **AI-Powered Queries**
```
"Show me temperature profiles in the North Atlantic from this month"
"What are the oxygen levels in the Pacific Ocean?"
"Find ARGO floats with recent biogeochemical data"
"Compare salinity between different ocean basins"
```

### 🗺️ **Interactive Maps**
- View real ARGO float locations worldwide
- Click markers for detailed float information
- See data source locations from your queries

### 📊 **Data Visualizations**
- Temperature-salinity diagrams
- Depth profiles with real measurements
- Time series plots
- Biogeochemical parameter charts

### 📋 **Data Tables**
- Browse all loaded floats and profiles
- Filter by location, date, parameters
- Sort and search functionality
- Real-time data updates

### 💾 **Data Export**
- **CSV format**: For spreadsheet analysis
- **ARGO NetCDF format**: Scientific standard format
- **Filtered exports**: Download only relevant data
- **Batch processing**: Multiple profiles/floats

## 📈 Data Statistics

After setup, you'll have access to:
- **50+ ARGO floats** (with real data)
- **Hundreds of profiles** (recent measurements)
- **Thousands of data points** (T, S, P measurements)
- **Global coverage** (all ocean basins)
- **Quality-controlled data** (ARGO standards)

## 🔍 Monitoring Your Data

### Check Data Status:
```bash
# Via API
curl http://localhost:8000/api/v1/data-management/data-status

# Via Web Interface
# Visit: http://localhost:3000/setup
```

### View Data Summary:
- Total floats and profiles loaded
- Data size and date range
- Last update timestamp
- System readiness status

## 🛠️ Troubleshooting

### Common Issues:

1. **"No data loaded yet"**
   - Run the setup script or use web interface
   - Check internet connection
   - Verify database is running

2. **"Data fetch failed"**
   - Check ARGO data source availability
   - Verify network connectivity
   - Try with fewer files (`--max-files 10`)

3. **"Database connection error"**
   - Ensure PostgreSQL is running: `docker-compose up -d postgres`
   - Check database credentials in `.env`

4. **"Import errors"**
   - Install required dependencies: `pip install -r backend/requirements.txt`
   - Check Python path and virtual environment

### Debug Commands:
```bash
# Check services
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs postgres

# Test database connection
python -c "from backend.app.core.database import SessionLocal; print('DB OK')"

# Check data directory
ls -la data/raw/
```

## 🔄 Updating Data

### Automatic Updates:
The system can be configured to automatically fetch new data:

```bash
# Set up a cron job (Linux/Mac)
# Add to crontab: 0 6 * * * /path/to/your/setup_real_data.py

# Or run periodically
python setup_real_data.py
```

### Manual Updates:
Use the web interface or run the fetch script again to get the latest data.

## 🎉 Success Verification

Your setup is successful when:

1. ✅ **Data Status**: Shows "Ready for queries"
2. ✅ **Float Count**: > 0 floats loaded
3. ✅ **Profile Count**: > 0 profiles loaded
4. ✅ **AI Responses**: Detailed answers with real data
5. ✅ **Maps**: Show actual float locations
6. ✅ **Charts**: Display real measurements
7. ✅ **Tables**: Show loaded data
8. ✅ **Exports**: Download real data files

## 🌟 Next Steps

With real data loaded:

1. **🤖 Ask Complex Questions**: Your AI now has real oceanographic knowledge
2. **🗺️ Explore Global Data**: See actual float distributions
3. **📊 Analyze Trends**: Use real measurements for research
4. **💾 Export Results**: Download data for external analysis
5. **🔄 Keep Updated**: Regularly fetch new data

---

**🌊 Congratulations! Your WavyAI system is now powered by real ARGO oceanographic data! 🌊**

The AI assistant can now provide accurate, data-driven insights about ocean conditions worldwide using the latest measurements from the global ARGO float network.

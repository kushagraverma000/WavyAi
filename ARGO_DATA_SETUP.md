# ARGO NetCDF Data Setup Guide

This guide will help you load your ARGO NetCDF files into the WavyAI database.

## Prerequisites

1. **Environment Setup**: Ensure you have the `.env.example` files (now created)
2. **Database**: PostgreSQL with PostGIS and TimescaleDB extensions
3. **Python Dependencies**: All required packages are in `backend/requirements.txt`

## Directory Structure

Your ARGO data should be organized as:
```
/path/to/argo/data/
├── 2004/
│   ├── 01/
│   │   ├── 01/
│   │   │   ├── file1.nc
│   │   │   ├── file2.nc
│   │   │   └── ...
│   │   ├── 02/
│   │   └── ...
│   └── ...
├── 2005/
└── ...
```

## Setup Steps

### 1. Fix the .env.example Error

The missing `.env.example` files have been created. Now copy them:

```bash
# Backend environment
cp backend/.env.example backend/.env

# Frontend environment  
cp frontend/.env.example frontend/.env
```

### 2. Configure Environment Variables

Edit `backend/.env` and set:
```env
# Update this with your actual ARGO data path
ARGO_DATA_PATH=/path/to/your/argo/data

# Database connection (update if needed)
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai

# Add your API keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
```

### 3. Validate Your Data Structure

```bash
cd backend
python scripts/setup_argo_data.py /path/to/your/argo/data --validate-only
```

### 4. Test Loading a Single File

```bash
python scripts/setup_argo_data.py /path/to/your/argo/data --test-load
```

### 5. Initialize Database

```bash
# Start services (if using Docker)
docker-compose up -d

# Initialize database
python scripts/init_db.py
```

## Loading Data

### Load Specific Date
```bash
python scripts/load_argo_netcdf.py /path/to/your/argo/data --year 2023 --month 1 --day 1
```

### Load Specific Month
```bash
python scripts/load_argo_netcdf.py /path/to/your/argo/data --year 2023 --month 1
```

### Load Specific Year
```bash
python scripts/load_argo_netcdf.py /path/to/your/argo/data --year 2023
```

### Load Limited Number of Files (for testing)
```bash
python scripts/load_argo_netcdf.py /path/to/your/argo/data --max-files 10
```

### Load All Data (⚠️ Use with caution for large datasets)
```bash
python scripts/load_argo_netcdf.py /path/to/your/argo/data
```

## Data Processing Features

The ARGO NetCDF loader supports:

- **Core Measurements**: Temperature, Salinity, Pressure
- **BGC Data**: Oxygen, Chlorophyll, Nitrate, pH
- **Quality Control**: QC flags for all measurements
- **Metadata**: Float information, deployment details
- **Automatic Depth Calculation**: From pressure when not available
- **Duplicate Prevention**: Skips already loaded profiles

## Supported NetCDF Variables

### Core Variables
- `PRES` → Pressure
- `TEMP` → Temperature  
- `PSAL` → Salinity
- `LATITUDE` → Latitude
- `LONGITUDE` → Longitude
- `JULD` → Julian Date
- `CYCLE_NUMBER` → Profile Number

### BGC Variables
- `DOXY` → Dissolved Oxygen
- `CHLA` → Chlorophyll-a
- `NITRATE` → Nitrate
- `PH_IN_SITU_TOTAL` → pH

### Quality Control
- All variables support corresponding `_QC` flags

## Database Schema

Data is loaded into these tables:

1. **argo_floats**: Float metadata and deployment info
2. **profiles**: Individual profile data with location/time
3. **measurements**: Core T/S/P measurements by depth level
4. **bgc_data**: Biogeochemical measurements by depth level

## Troubleshooting

### Common Issues

1. **Missing .env.example files**: ✅ Fixed - files created
2. **NetCDF4 not installed**: Install with `pip install netcdf4`
3. **Database connection**: Check PostgreSQL is running and credentials are correct
4. **Large datasets**: Use `--max-files` to limit processing for testing

### Performance Tips

- Start with a small subset using `--year`, `--month`, `--day` filters
- Use `--max-files` for initial testing
- Monitor database size and performance
- Consider loading data in batches for very large datasets

### Logging

The loader provides detailed logging:
- INFO: General progress and statistics
- DEBUG: Detailed processing information  
- ERROR: Failed files and error details

## Example Workflow

```bash
# 1. Validate your data structure
python scripts/setup_argo_data.py /path/to/argo/data --validate-only

# 2. Test with a single file
python scripts/setup_argo_data.py /path/to/argo/data --test-load

# 3. Load a small subset for testing
python scripts/load_argo_netcdf.py /path/to/argo/data --year 2023 --month 1 --max-files 5

# 4. Load progressively larger datasets
python scripts/load_argo_netcdf.py /path/to/argo/data --year 2023 --month 1
python scripts/load_argo_netcdf.py /path/to/argo/data --year 2023

# 5. Eventually load all data
python scripts/load_argo_netcdf.py /path/to/argo/data
```

## Next Steps

After loading your data:

1. **Start the application**: `docker-compose up -d`
2. **Access the frontend**: http://localhost:3000
3. **Test queries**: Try natural language queries about your oceanographic data
4. **Monitor performance**: Check database size and query performance

## Support

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your NetCDF file format matches ARGO standards
3. Test with a small subset first
4. Check database connectivity and permissions

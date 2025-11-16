# 🚀 WavyAI Local Setup Guide

**Fast setup using minimal Docker + local processing**

This approach uses Docker only for databases and runs heavy processing locally for better performance.

## 🎯 Quick Start (3 Steps)

### Step 1: Start Minimal Services
```bash
# Start only databases in Docker (lightweight)
python start_services.py --setup
```

### Step 2: Create Sample Data
```bash
# Create and load sample ARGO data locally (fast)
python setup_local_data.py
```

### Step 3: Start Application
```bash
# Terminal 1: Start backend locally
python start_services.py --backend

# Terminal 2: Start frontend locally  
python start_services.py --frontend
```

**🎉 Done! Visit: http://localhost:3000**

## 📋 What This Setup Does

### ✅ **Minimal Docker Usage**
- **PostgreSQL**: Database only
- **Redis**: Caching only  
- **Qdrant**: Vector search only
- **No heavy containers** or file processing in Docker

### ✅ **Local Processing**
- **Backend server**: Runs locally with Python
- **Frontend dev server**: Runs locally with Node.js
- **Data processing**: Fast local file operations
- **AI responses**: Direct API calls (no container overhead)

### ✅ **Sample Data Created**
- **35 ARGO floats** with realistic metadata
- **35 profiles** with temperature, salinity, pressure data
- **BGC data**: Oxygen, chlorophyll measurements
- **Global coverage**: Atlantic, Pacific, Indian Ocean data
- **Recent dates**: Last 7 days of sample data

## 🔧 Manual Commands (Alternative)

If the scripts don't work, run manually:

### Start Databases Only
```bash
docker-compose -f docker-compose.minimal.yml up -d
```

### Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd frontend
npm install
```

### Start Servers
```bash
# Backend (Terminal 1)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

## 🌊 Test Your Setup

Once running, try these queries:

```
"Show me temperature profiles from the Atlantic Ocean"
"What are the salinity levels in recent data?"
"Find ARGO floats with biogeochemical measurements"
"Display oxygen levels at different depths"
```

## 🎯 Features Available

### 🤖 **AI Assistant**
- **Google Gemini powered** responses
- **Context-aware** answers about ocean data
- **User-type adaptation** (researcher/student/manager)

### 🗺️ **Interactive Maps**
- **Google Maps** with float locations
- **Click markers** for detailed information
- **Real-time data** visualization

### 📊 **Data Visualizations**
- **Temperature-salinity diagrams**
- **Depth profiles**
- **Time series plots**
- **Interactive charts**

### 📋 **Data Tables**
- **Browse floats and profiles**
- **Filter and search** functionality
- **Sort by any column**
- **Pagination** for large datasets

### 💾 **Data Export**
- **CSV format** for spreadsheet analysis
- **NetCDF format** for scientific tools
- **Filtered exports** based on search criteria

## 🔍 Troubleshooting

### Common Issues:

1. **"Database connection failed"**
   ```bash
   # Check if databases are running
   docker-compose -f docker-compose.minimal.yml ps
   
   # Restart if needed
   docker-compose -f docker-compose.minimal.yml restart
   ```

2. **"Module not found" errors**
   ```bash
   # Install missing packages
   pip install xarray netcdf4 pandas google-generativeai
   ```

3. **"Port already in use"**
   ```bash
   # Check what's using the port
   lsof -i :8000  # Backend port
   lsof -i :3000  # Frontend port
   
   # Kill if needed
   kill -9 <PID>
   ```

4. **"No data available"**
   ```bash
   # Re-run data setup
   python setup_local_data.py
   ```

### Check Service Status:
```bash
# Database services
docker-compose -f docker-compose.minimal.yml ps

# Backend API
curl http://localhost:8000/api/v1/health/health

# Frontend
curl http://localhost:3000
```

## 🚀 Performance Benefits

### **vs Full Docker Setup:**
- ⚡ **10x faster** data processing
- 💾 **Less memory usage** (no heavy containers)
- 🔄 **Faster restarts** (no container rebuilds)
- 🛠️ **Easier debugging** (direct Python/Node.js)
- 📁 **Direct file access** (no volume mounts)

### **Resource Usage:**
- **Docker**: Only 3 lightweight database containers
- **CPU**: Local processing uses full CPU efficiently  
- **Memory**: ~500MB for databases vs ~2GB+ for full Docker
- **Disk**: No container images for backend/frontend

## 🎉 Success Indicators

Your setup is working when:

1. ✅ **Databases running**: `docker-compose ps` shows 3 services up
2. ✅ **Backend API**: http://localhost:8000/docs loads
3. ✅ **Frontend**: http://localhost:3000 loads
4. ✅ **Data loaded**: Can see floats/profiles in tables
5. ✅ **AI responses**: Chatbot answers questions about data
6. ✅ **Maps working**: Google Maps shows float locations
7. ✅ **Export working**: Can download CSV/NetCDF files

## 🔄 Daily Usage

### Start Everything:
```bash
# One-time: Start databases
docker-compose -f docker-compose.minimal.yml up -d

# Daily: Start application
python start_services.py --backend    # Terminal 1
python start_services.py --frontend   # Terminal 2
```

### Stop Everything:
```bash
# Stop application: Ctrl+C in terminals

# Stop databases (optional)
docker-compose -f docker-compose.minimal.yml down
```

---

**🌊 Enjoy your fast, local WavyAI setup! 🌊**

This configuration gives you the best of both worlds: reliable database services in Docker and fast local processing for everything else.

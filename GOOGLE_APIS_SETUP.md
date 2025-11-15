# 🚀 Google APIs Setup Guide for WavyAI

This guide will help you configure Google Gemini AI and Google Maps APIs to make WavyAI fully functional with enhanced AI responses, interactive maps, data visualizations, and download capabilities.

## 🔑 Required API Keys

### 1. Google Gemini API Key (for AI Responses)

**Get your API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (starts with `AIza...`)

**Add to your environment:**
```bash
# In backend/.env
GOOGLE_GEMINI_API_KEY=AIzaSyYour_Gemini_API_Key_Here
```

### 2. Google Maps API Key (for Interactive Maps)

**Get your API key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API (optional, for enhanced features)
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the generated API key

**Add to your environment:**
```bash
# In backend/.env
GOOGLE_MAPS_API_KEY=AIzaSyYour_Maps_API_Key_Here

# In frontend/.env
VITE_GOOGLE_MAPS_API_KEY=AIzaSyYour_Maps_API_Key_Here
```

## 📋 Complete Environment Setup

### Backend Environment (`backend/.env`)
```env
# Database
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
QDRANT_URL=http://localhost:6333

# Google APIs
GOOGLE_GEMINI_API_KEY=AIzaSyYour_Gemini_API_Key_Here
GOOGLE_MAPS_API_KEY=AIzaSyYour_Maps_API_Key_Here

# ARGO Data Path (update with your data location)
ARGO_DATA_PATH=/path/to/your/argo/data

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend Environment (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_GOOGLE_MAPS_API_KEY=AIzaSyYour_Maps_API_Key_Here
```

## 🛠️ Installation & Setup

### 1. Update Dependencies
```bash
cd backend
pip install google-generativeai==0.3.2
```

### 2. Copy Environment Files
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your Google Maps API key
```

### 3. Start the Services
```bash
# Start all services
docker-compose up -d

# Or start individually
docker-compose up -d postgres redis qdrant
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && npm run dev
```

## 🎯 New Features Available

### 🤖 Enhanced AI Responses
- **Powered by Google Gemini**: More accurate and contextual responses
- **User-type adaptation**: Responses tailored for researchers, students, managers
- **Rich context**: Incorporates data sources and query intent
- **Fallback system**: Works even without API key (basic responses)

### 🗺️ Interactive Google Maps
- **Real-time ARGO float locations**: See active floats worldwide
- **Data source markers**: Visualize query results on map
- **Custom styling**: Ocean-themed dark mode
- **Info windows**: Detailed float information on click
- **Responsive design**: Works on all screen sizes

### 📊 Advanced Data Visualizations
- **Interactive charts**: Temperature-salinity diagrams, depth profiles
- **Multiple chart types**: Line charts, scatter plots, heatmaps
- **Real-time data**: Updates based on query results
- **Export capabilities**: Save charts as images

### 📋 Comprehensive Data Tables
- **Dual view**: Profiles and Floats data
- **Advanced filtering**: Search, sort, and filter data
- **Pagination**: Handle large datasets efficiently
- **Real-time updates**: Reflects current query results

### 💾 Data Export Features
- **CSV Export**: Standard format for spreadsheet analysis
- **ARGO NetCDF Export**: Scientific standard format
- **Filtered exports**: Download only relevant data
- **Batch processing**: Handle multiple profiles/floats

## 🔬 Researcher Workflow

### 1. Query Ocean Data
```
"Show me temperature profiles in the North Atlantic from 2023"
```

### 2. View AI Response
- Get comprehensive analysis from Google Gemini
- Understand data patterns and trends
- Receive tailored insights based on user type

### 3. Explore Interactive Map
- See float locations on Google Maps
- Click markers for detailed information
- Visualize spatial distribution of data

### 4. Analyze Data Tables
- Switch to "Data Tables" tab
- Filter and sort profiles/floats
- Search specific parameters

### 5. Create Visualizations
- View temperature-salinity diagrams
- Analyze depth profiles
- Compare multiple datasets

### 6. Download Data
- Export filtered data as CSV
- Download ARGO-compliant NetCDF files
- Use in external analysis tools

## 🚨 API Key Security

### Best Practices:
1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Restrict API key usage** in Google Cloud Console:
   - Set HTTP referrer restrictions for Maps API
   - Set IP restrictions for server-side APIs
4. **Monitor usage** in Google Cloud Console
5. **Rotate keys regularly** for production use

### Google Maps API Restrictions:
```
# Add these domains to your API key restrictions:
http://localhost:3000/*
https://yourdomain.com/*
```

## 💰 Cost Considerations

### Google Gemini API:
- **Free tier**: 15 requests per minute
- **Paid tier**: $0.00025 per 1K characters
- **Recommendation**: Start with free tier for testing

### Google Maps API:
- **Free tier**: $200 credit monthly (≈28K map loads)
- **Cost**: $7 per 1K map loads after free tier
- **Recommendation**: Enable billing alerts

## 🔧 Troubleshooting

### Common Issues:

1. **"Google Maps API key not configured"**
   - Check `VITE_GOOGLE_MAPS_API_KEY` in frontend/.env
   - Ensure Maps JavaScript API is enabled

2. **"Gemini API key not provided"**
   - Check `GOOGLE_GEMINI_API_KEY` in backend/.env
   - Verify API key is valid and active

3. **Map not loading**
   - Check browser console for errors
   - Verify API key restrictions
   - Ensure internet connectivity

4. **AI responses are basic**
   - Gemini API key may be missing/invalid
   - Check backend logs for errors
   - System will use fallback responses

### Debug Commands:
```bash
# Check backend logs
docker-compose logs backend

# Check frontend console
# Open browser dev tools → Console tab

# Test API endpoints
curl http://localhost:8000/api/v1/health/health
```

## 🎉 Success Verification

Your setup is successful when you can:

1. ✅ Ask questions and get detailed AI responses
2. ✅ See interactive Google Maps with float locations
3. ✅ Switch between Visualizations and Data Tables tabs
4. ✅ Filter and search data in tables
5. ✅ Download data in CSV and NetCDF formats
6. ✅ View charts and plots based on queries

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify all API keys are correctly configured
3. Check browser console and backend logs
4. Ensure all services are running (`docker-compose ps`)

---

**🌊 Happy Ocean Data Analysis with WavyAI! 🌊**

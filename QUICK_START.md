# 🚀 WavyAI Prototype - Quick Start Guide

This guide will help you run the WavyAI prototype quickly. **No database setup or API keys required!**

## Prerequisites

- Python 3.11+ 
- Node.js 18+ and npm
- That's it! No database, Redis, or API keys needed for the prototype.

## Quick Start (5 minutes)

### Step 1: Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create minimal .env file (optional - uses defaults if not present):**
```bash
# Create backend/.env file
cat > .env << EOF
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
ENVIRONMENT=development
DEBUG=true
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
```

**Note:** Even though the .env mentions database URLs, the prototype works without them using sample data!

5. **Start the backend server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is running!** Test it at: http://localhost:8000/docs

---

### Step 2: Frontend Setup

Open a **new terminal window** (keep backend running):

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

3. **Create frontend .env file (optional):**
```bash
# Create frontend/.env file
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
```

4. **Start the frontend development server:**
```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Frontend is running!**

---

### Step 3: Access the Application

Open your browser and go to:
- **Frontend:** http://localhost:5173 (or http://localhost:3000)
- **Backend API Docs:** http://localhost:8000/docs

## 🎯 Testing the Prototype

### Try These Example Queries:

1. **"Where are ARGO floats located?"**
   - Should show a map with float locations

2. **"What is the temperature profile in the North Atlantic?"**
   - Should show temperature-depth chart

3. **"How does salinity change with depth?"**
   - Should show salinity-depth chart

4. **"What is the ocean temperature trend?"**
   - Should show time series chart

5. **"Show me the ARGO float data"**
   - Should show data tables with downloadable CSV

### Features to Test:

✅ **Text Answers:** AI responds with oceanographic information  
✅ **Maps:** Interactive Leaflet map showing float locations  
✅ **Charts:** Temperature/salinity profiles and trends  
✅ **Data Tables:** Browse profiles and floats  
✅ **CSV Download:** Export data for research  

## 🛠️ Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Module not found errors:**
```bash
# Make sure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 or 5173 already in use:**
```bash
# Vite will automatically use next available port
# Or specify a port:
npm run dev -- --port 3001
```

**Cannot connect to backend:**
- Check backend is running on port 8000
- Check `VITE_API_URL` in frontend/.env matches backend URL
- Try: `curl http://localhost:8000/health`

**CORS errors:**
- Make sure backend has CORS enabled for frontend URL
- Check `CORS_ORIGINS` in backend/.env includes frontend URL

### Common Issues

**Import errors in backend:**
```bash
# Make sure you're running from backend directory
cd backend
# And venv is activated
source venv/bin/activate
```

**Frontend build errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📁 Project Structure

```
WavyAI/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Main application
│   │   ├── services/    # Business logic (simple_llm, simple_query_service)
│   │   ├── api/         # API endpoints
│   │   └── data/        # Sample ocean data
│   ├── venv/            # Python virtual environment
│   └── requirements.txt
│
└── frontend/            # React frontend
    ├── src/
    │   ├── pages/       # Dashboard, LandingPage
    │   ├── components/  # Visualizations, Charts, Maps
    │   └── services/    # API client
    └── package.json
```

## 🔄 Development Workflow

1. **Backend changes:** Server auto-reloads (--reload flag)
2. **Frontend changes:** Vite hot-reloads automatically
3. **Check logs:** 
   - Backend logs in terminal
   - Frontend logs in browser console (F12)

## 📝 Next Steps

- Customize sample data in `backend/app/data/sample_ocean_data.py`
- Enhance queries in `backend/app/services/simple_llm.py`
- Modify visualizations in `frontend/src/components/Visualizations/`

## 🎉 You're All Set!

The prototype is fully functional with:
- ✅ No database required
- ✅ No API keys needed
- ✅ Free visualization libraries
- ✅ Sample data included
- ✅ All features working

Enjoy exploring WavyAI! 🌊



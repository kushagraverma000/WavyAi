# 🚀 How to Run WavyAI Prototype

## Quick Start (5 minutes)

### Prerequisites
- Python 3.11+ (tested with Python 3.13)
- Node.js 18+ and npm

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend (NO DATABASE NEEDED!)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend will start on: http://localhost:8000

### Step 2: Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Create .env file (optional)
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Start frontend
npm run dev
```

✅ Frontend will start on: http://localhost:5173

## 🎯 That's It!

Open http://localhost:5173 in your browser and start querying!

## ✅ All Issues Fixed

- ✅ Python 3.13 compatibility (pandas updated)
- ✅ Frontend dependencies installed (react-leaflet, leaflet)
- ✅ Database connection gracefully handled (prototype mode works without DB)
- ✅ All imports working correctly

## 📝 Test Queries

Try these in the frontend:
1. "Where are ARGO floats located?"
2. "What is the temperature profile in the North Atlantic?"
3. "How does salinity change with depth?"
4. "Show me the ARGO float data"

## 🛠️ Troubleshooting

**Backend won't start:**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Check Python version: `python3 --version` (should be 3.11+)
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Install dependencies: `npm install`
- Check Node version: `node --version` (should be 18+)

**Import errors:**
- All critical imports have been fixed
- Backend uses lazy database initialization
- Frontend dependencies are installed

## 🎉 Prototype Features

✅ Text answers from AI
✅ Interactive maps (Leaflet - no API keys needed)
✅ Charts and visualizations (Recharts - free)
✅ Data tables with CSV download
✅ Sample data included (no database needed)
✅ All features working end-to-end

Enjoy! 🌊



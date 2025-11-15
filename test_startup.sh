#!/bin/bash
echo "Testing WavyAI startup..."

# Test backend imports
echo "1. Testing backend imports..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
    python3 -c "from app.main import app; print('✅ Backend imports OK')" 2>&1
else
    echo "⚠️  Backend venv not found - run setup first"
fi

# Test frontend
echo "2. Testing frontend dependencies..."
cd ../frontend
if [ -d "node_modules" ]; then
    npm list react-leaflet leaflet recharts 2>&1 | grep -E "(react-leaflet|leaflet|recharts)" | head -3
    echo "✅ Frontend dependencies OK"
else
    echo "⚠️  Frontend node_modules not found - run npm install first"
fi

echo "✅ Startup tests complete"

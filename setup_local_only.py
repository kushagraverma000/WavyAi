#!/usr/bin/env python3
"""
Complete local setup for WavyAI without Docker.
This script sets up everything to run locally on your machine.
"""
import subprocess
import sys
import os
import json
from pathlib import Path
import time

def run_command(cmd, cwd=None, check=True, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=capture_output, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {e.stderr}")
        return None

def check_homebrew():
    """Check if Homebrew is installed (macOS)."""
    result = run_command("brew --version", check=False)
    if result and result.returncode == 0:
        print("✅ Homebrew is available")
        return True
    else:
        print("❌ Homebrew not found. Installing...")
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        print("Please run this command to install Homebrew:")
        print(install_cmd)
        return False

def install_postgresql():
    """Install PostgreSQL locally."""
    print("🗄️  Setting up PostgreSQL locally...")
    
    # Check if already installed
    result = run_command("psql --version", check=False)
    if result and result.returncode == 0:
        print("✅ PostgreSQL is already installed")
        return True
    
    # Install via Homebrew
    print("📦 Installing PostgreSQL via Homebrew...")
    result = run_command("brew install postgresql@15")
    if result:
        print("✅ PostgreSQL installed")
        
        # Start PostgreSQL service
        print("🚀 Starting PostgreSQL service...")
        run_command("brew services start postgresql@15")
        
        # Wait a moment for service to start
        time.sleep(3)
        
        # Create database and user
        print("👤 Setting up database and user...")
        run_command('createdb wavyai', check=False)
        run_command("psql -d wavyai -c \"CREATE USER wavyai WITH PASSWORD 'wavyai_password';\"", check=False)
        run_command("psql -d wavyai -c \"GRANT ALL PRIVILEGES ON DATABASE wavyai TO wavyai;\"", check=False)
        run_command("psql -d wavyai -c \"ALTER USER wavyai CREATEDB;\"", check=False)
        
        print("✅ PostgreSQL setup completed")
        return True
    else:
        print("❌ Failed to install PostgreSQL")
        return False

def install_redis():
    """Install Redis locally."""
    print("🔄 Setting up Redis locally...")
    
    # Check if already installed
    result = run_command("redis-server --version", check=False)
    if result and result.returncode == 0:
        print("✅ Redis is already installed")
        return True
    
    # Install via Homebrew
    print("📦 Installing Redis via Homebrew...")
    result = run_command("brew install redis")
    if result:
        print("✅ Redis installed")
        
        # Start Redis service
        print("🚀 Starting Redis service...")
        run_command("brew services start redis")
        
        print("✅ Redis setup completed")
        return True
    else:
        print("❌ Failed to install Redis")
        return False

def setup_local_vector_db():
    """Set up a simple local vector database alternative."""
    print("🔍 Setting up local vector search...")
    
    # Create a simple vector storage directory
    vector_dir = Path("data/vectors")
    vector_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple vector index file
    vector_config = {
        "type": "local_faiss",
        "dimension": 384,
        "index_path": str(vector_dir / "index.faiss"),
        "metadata_path": str(vector_dir / "metadata.json")
    }
    
    with open(vector_dir / "config.json", "w") as f:
        json.dump(vector_config, f, indent=2)
    
    print("✅ Local vector search setup completed")
    return True

def install_python_dependencies():
    """Install all required Python packages."""
    print("🐍 Installing Python dependencies...")
    
    # Backend dependencies
    backend_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "redis==5.0.1",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-multipart==0.0.6",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "xarray==2023.12.0",
        "netcdf4==1.6.5",
        "pandas==2.1.4",
        "numpy==1.24.3",
        "requests==2.31.0",
        "google-generativeai==0.3.2",
        "faiss-cpu==1.7.4",  # Local vector search
        "sentence-transformers==2.2.2"
    ]
    
    print("📦 Installing backend packages...")
    for package in backend_packages:
        try:
            result = run_command(f"pip install {package}")
            if result:
                print(f"✅ {package}")
            else:
                print(f"⚠️  Warning: {package}")
        except Exception as e:
            print(f"⚠️  Warning: {package} - {e}")
    
    print("✅ Python dependencies installed")
    return True

def setup_environment_files():
    """Set up environment files for local development."""
    print("⚙️  Setting up environment files...")
    
    # Backend .env
    backend_env = """# Database (Local PostgreSQL)
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai

# Redis (Local)
REDIS_URL=redis://localhost:6379/0

# Vector Database (Local FAISS)
VECTOR_DB_TYPE=local_faiss
VECTOR_DB_PATH=./data/vectors

# Google APIs (add your keys)
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# ARGO Data Path
ARGO_DATA_PATH=./data/raw

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# JWT and Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-local-dev
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# CORS
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Logging
LOG_FORMAT=json
LOG_FILE=logs/app.log

# Local development
LOCAL_DEVELOPMENT=true
"""
    
    with open("backend/.env", "w") as f:
        f.write(backend_env)
    
    # Frontend .env
    frontend_env = """VITE_API_URL=http://localhost:8000/api/v1
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
"""
    
    with open("frontend/.env", "w") as f:
        f.write(frontend_env)
    
    print("✅ Environment files created")
    return True

def install_node_dependencies():
    """Install Node.js dependencies for frontend."""
    print("📦 Installing Node.js dependencies...")
    
    # Check if Node.js is installed
    result = run_command("node --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Node.js not found. Installing via Homebrew...")
        result = run_command("brew install node")
        if not result:
            print("❌ Failed to install Node.js")
            return False
    
    print("✅ Node.js is available")
    
    # Install frontend dependencies
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        print("📦 Installing frontend packages...")
        result = run_command("npm install", cwd="frontend")
        if result:
            print("✅ Frontend dependencies installed")
            return True
        else:
            print("❌ Failed to install frontend dependencies")
            return False
    else:
        print("❌ Frontend directory not found")
        return False

def create_sample_data():
    """Create sample ARGO data."""
    print("🌊 Creating sample ARGO data...")
    
    try:
        import numpy as np
        import xarray as xr
        from datetime import datetime, timedelta
    except ImportError:
        print("❌ Required packages not installed. Installing...")
        run_command("pip install numpy xarray netcdf4")
        import numpy as np
        import xarray as xr
        from datetime import datetime, timedelta
    
    # Create data directory
    data_path = Path("data/raw")
    data_path.mkdir(parents=True, exist_ok=True)
    
    sample_files = []
    
    # Create sample data for last 7 days
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        
        # Create directory structure
        local_dir = data_path / str(date.year) / f"{date.month:02d}" / f"{date.day:02d}"
        local_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate sample profiles for this day
        for j in range(3):  # 3 profiles per day
            float_id = f"590{i:02d}{j:02d}"
            filename = f"argo_profile_{float_id}_001.nc"
            file_path = local_dir / filename
            
            if not file_path.exists():
                # Create sample profile data
                n_levels = np.random.randint(50, 150)
                pressure = np.linspace(0, 2000, n_levels)
                depth = pressure
                
                # Realistic temperature profile
                surface_temp = np.random.uniform(15, 28)
                temperature = surface_temp * np.exp(-pressure / 1000) + np.random.normal(0, 0.5, n_levels)
                temperature = np.maximum(temperature, 2)
                
                # Realistic salinity profile
                surface_salinity = np.random.uniform(34, 36)
                salinity = surface_salinity + (pressure / 2000) * np.random.uniform(-0.5, 0.5) + np.random.normal(0, 0.1, n_levels)
                salinity = np.maximum(salinity, 33)
                
                # Random location
                latitude = np.random.uniform(-60, 60)
                longitude = np.random.uniform(-180, 180)
                
                # Create xarray dataset
                ds = xr.Dataset({
                    'PRES': (['N_LEVELS'], pressure),
                    'TEMP': (['N_LEVELS'], temperature),
                    'PSAL': (['N_LEVELS'], salinity),
                    'DEPTH': (['N_LEVELS'], depth),
                }, coords={
                    'N_LEVELS': range(n_levels)
                })
                
                # Add attributes
                ds.attrs.update({
                    'title': 'Sample ARGO Profile',
                    'platform_number': float_id,
                    'cycle_number': 1,
                    'latitude': latitude,
                    'longitude': longitude,
                    'juld': date.timestamp(),
                    'date_creation': datetime.now().isoformat(),
                    'institution': 'WavyAI Local Sample Data',
                })
                
                # Save to NetCDF
                ds.to_netcdf(file_path)
                print(f"✅ Created: {filename}")
            
            sample_files.append(str(file_path))
    
    print(f"✅ Created {len(sample_files)} sample files")
    return True

def setup_database_tables():
    """Set up database tables."""
    print("🗄️  Setting up database tables...")
    
    # Set environment variables
    os.environ.update({
        'DATABASE_URL': 'postgresql://wavyai:wavyai_password@localhost:5432/wavyai',
        'REDIS_URL': 'redis://localhost:6379/0',
        'VECTOR_DB_TYPE': 'local_faiss',
        'VECTOR_DB_PATH': './data/vectors',
        'ARGO_DATA_PATH': './data/raw',
        'ENVIRONMENT': 'development',
        'DEBUG': 'true',
        'LOG_LEVEL': 'INFO'
    })
    
    # Add backend to Python path
    backend_dir = Path('backend').absolute()
    sys.path.insert(0, str(backend_dir))
    
    try:
        from app.core.database import engine
        from app.models.base import Base
        
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("Make sure PostgreSQL is running: brew services start postgresql@15")
        return False

def create_start_script():
    """Create a simple start script."""
    start_script = """#!/bin/bash
# WavyAI Local Start Script

echo "🌊 Starting WavyAI (Local Mode)"
echo "================================"

# Check services
echo "🔍 Checking local services..."

# Check PostgreSQL
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "🚀 Starting PostgreSQL..."
    brew services start postgresql@15
    sleep 3
fi

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "🚀 Starting Redis..."
    brew services start redis
    sleep 2
fi

echo "✅ Services are ready"
echo ""
echo "🎯 To start the application:"
echo "1. Backend:  cd backend && python -m uvicorn app.main:app --reload --port 8000"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "📱 Then visit: http://localhost:3000"
"""
    
    with open("start_local.sh", "w") as f:
        f.write(start_script)
    
    # Make executable
    run_command("chmod +x start_local.sh")
    print("✅ Created start_local.sh script")

def main():
    """Main setup function."""
    print("🌊 WavyAI Complete Local Setup")
    print("=" * 50)
    print("This will set up everything to run locally without Docker")
    print("(PostgreSQL, Redis, Python backend, Node.js frontend)")
    print()
    
    response = input("Continue with complete local setup? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    success_steps = []
    
    # Step 1: Check Homebrew
    if check_homebrew():
        success_steps.append("Homebrew")
    
    # Step 2: Install PostgreSQL
    if install_postgresql():
        success_steps.append("PostgreSQL")
    
    # Step 3: Install Redis
    if install_redis():
        success_steps.append("Redis")
    
    # Step 4: Set up vector DB alternative
    if setup_local_vector_db():
        success_steps.append("Vector DB")
    
    # Step 5: Install Python dependencies
    if install_python_dependencies():
        success_steps.append("Python packages")
    
    # Step 6: Install Node.js dependencies
    if install_node_dependencies():
        success_steps.append("Node.js packages")
    
    # Step 7: Set up environment files
    if setup_environment_files():
        success_steps.append("Environment files")
    
    # Step 8: Create sample data
    if create_sample_data():
        success_steps.append("Sample data")
    
    # Step 9: Set up database
    if setup_database_tables():
        success_steps.append("Database tables")
    
    # Step 10: Create start script
    create_start_script()
    success_steps.append("Start script")
    
    print(f"\n🎉 Setup completed! ({len(success_steps)}/10 steps successful)")
    print("\n✅ Successful steps:", ", ".join(success_steps))
    
    print("\n🚀 To start WavyAI:")
    print("1. ./start_local.sh  # Check services")
    print("2. cd backend && python -m uvicorn app.main:app --reload --port 8000")
    print("3. cd frontend && npm run dev")
    print("4. Visit: http://localhost:3000")
    
    print("\n📝 Don't forget to:")
    print("1. Add your Google API keys to backend/.env and frontend/.env")
    print("2. Check that services are running with: ./start_local.sh")

if __name__ == "__main__":
    main()

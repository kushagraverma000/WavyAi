#!/usr/bin/env python3
"""
Local ARGO data setup without heavy Docker usage.
This script runs data processing locally for better performance.
"""
import asyncio
import sys
import os
import subprocess
import time
from pathlib import Path
import json

def install_required_packages():
    """Install required packages for data processing."""
    print("📦 Installing required packages...")
    
    packages = [
        "xarray==2023.12.0",
        "netcdf4==1.6.5", 
        "pandas==2.1.4",
        "numpy",
        "requests",
        "google-generativeai==0.3.2"
    ]
    
    for package in packages:
        try:
            result = subprocess.run(['pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Installed: {package}")
            else:
                print(f"⚠️  Warning: {package} - {result.stderr.strip()}")
        except Exception as e:
            print(f"⚠️  Warning: Could not install {package}: {e}")

def create_sample_data():
    """Create sample ARGO data files locally."""
    print("🌊 Creating sample ARGO data...")
    
    try:
        import numpy as np
        import xarray as xr
        from datetime import datetime, timedelta
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Installing packages...")
        install_required_packages()
        import numpy as np
        import xarray as xr
        from datetime import datetime, timedelta
    
    # Create data directory
    data_path = Path("data/raw")
    data_path.mkdir(parents=True, exist_ok=True)
    
    sample_files = []
    
    print("📊 Generating realistic oceanographic profiles...")
    
    # Create sample data for last 7 days
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        
        # Create directory structure
        local_dir = data_path / str(date.year) / f"{date.month:02d}" / f"{date.day:02d}"
        local_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate sample profiles for this day
        for j in range(5):  # 5 profiles per day
            float_id = f"590{i:02d}{j:02d}"
            filename = f"argo_profile_{float_id}_001.nc"
            file_path = local_dir / filename
            
            if not file_path.exists():
                # Create sample profile data
                n_levels = np.random.randint(50, 200)
                pressure = np.linspace(0, 2000, n_levels)
                depth = pressure  # Simplified depth calculation
                
                # Realistic temperature profile (warm at surface, cold at depth)
                surface_temp = np.random.uniform(15, 28)  # Surface temperature
                temperature = surface_temp * np.exp(-pressure / 1000) + np.random.normal(0, 0.5, n_levels)
                temperature = np.maximum(temperature, 2)  # Minimum 2°C
                
                # Realistic salinity profile
                surface_salinity = np.random.uniform(34, 36)
                salinity = surface_salinity + (pressure / 2000) * np.random.uniform(-0.5, 0.5) + np.random.normal(0, 0.1, n_levels)
                salinity = np.maximum(salinity, 33)  # Minimum salinity
                
                # Add some BGC data
                oxygen = 300 - (pressure / 10) + np.random.normal(0, 10, n_levels)
                oxygen = np.maximum(oxygen, 50)  # Minimum oxygen
                
                chlorophyll = 2 * np.exp(-pressure / 100) + np.random.normal(0, 0.1, n_levels)
                chlorophyll = np.maximum(chlorophyll, 0.01)
                
                # Random location (global coverage)
                latitude = np.random.uniform(-60, 60)
                longitude = np.random.uniform(-180, 180)
                
                # Create xarray dataset
                ds = xr.Dataset({
                    'PRES': (['N_LEVELS'], pressure),
                    'TEMP': (['N_LEVELS'], temperature),
                    'PSAL': (['N_LEVELS'], salinity),
                    'DEPTH': (['N_LEVELS'], depth),
                    'DOXY': (['N_LEVELS'], oxygen),
                    'CHLA': (['N_LEVELS'], chlorophyll),
                }, coords={
                    'N_LEVELS': range(n_levels)
                })
                
                # Add global attributes
                ds.attrs.update({
                    'title': 'Sample ARGO Profile',
                    'platform_number': float_id,
                    'cycle_number': 1,
                    'latitude': latitude,
                    'longitude': longitude,
                    'juld': date.timestamp(),
                    'date_creation': datetime.now().isoformat(),
                    'institution': 'WavyAI Sample Data',
                    'project_name': 'ARGO_SAMPLE',
                    'wmo_inst_type': '846',
                    'positioning_system': 'GPS',
                })
                
                # Save to NetCDF
                ds.to_netcdf(file_path)
                print(f"✅ Created: {filename}")
            
            sample_files.append(str(file_path))
    
    # Create float metadata file
    metadata_file = data_path / "float_metadata.json"
    
    float_metadata = []
    for i in range(35):  # 35 sample floats
        float_id = f"590{i:04d}"
        
        # Random deployment location
        deploy_lat = np.random.uniform(-60, 60)
        deploy_lon = np.random.uniform(-180, 180)
        
        # Random current location (within reasonable drift)
        current_lat = deploy_lat + np.random.uniform(-5, 5)
        current_lon = deploy_lon + np.random.uniform(-10, 10)
        
        # Random deployment date (last 5 years)
        deploy_date = datetime.now() - timedelta(days=np.random.randint(30, 1825))
        last_profile = datetime.now() - timedelta(days=np.random.randint(0, 30))
        
        float_metadata.append({
            'platform_number': float_id,
            'wmo_number': f"59{i:05d}",
            'deployment_date': deploy_date.isoformat(),
            'deployment_latitude': deploy_lat,
            'deployment_longitude': deploy_lon,
            'last_latitude': current_lat,
            'last_longitude': current_lon,
            'last_profile_date': last_profile.isoformat(),
            'current_status': np.random.choice(['active', 'inactive'], p=[0.8, 0.2]),
            'project_name': np.random.choice(['ARGO_GLOBAL', 'ARGO_ATLANTIC', 'ARGO_PACIFIC']),
            'institution': 'Sample Institution',
        })
    
    with open(metadata_file, 'w') as f:
        json.dump(float_metadata, f, indent=2)
    
    print(f"✅ Created float metadata: {metadata_file}")
    
    print(f"\n🎉 Sample Data Created Successfully!")
    print(f"📁 Location: {data_path}")
    print(f"📊 Files: {len(sample_files)} profile files")
    print(f"🏷️ Metadata: {len(float_metadata)} floats")
    
    # Calculate total size
    total_size = sum(Path(f).stat().st_size for f in sample_files if Path(f).exists())
    print(f"💾 Total size: {total_size / (1024*1024):.1f} MB")
    
    return sample_files, float_metadata

def load_data_to_database():
    """Load the created data into the database."""
    print("\n🗄️  Loading data into database...")
    
    # Set up environment
    os.environ.update({
        'DATABASE_URL': 'postgresql://wavyai:wavyai_password@localhost:5432/wavyai',
        'REDIS_URL': 'redis://localhost:6379/0',
        'QDRANT_URL': 'http://localhost:6333',
        'ARGO_DATA_PATH': str(Path('data/raw').absolute()),
        'ENVIRONMENT': 'development',
        'DEBUG': 'true',
        'LOG_LEVEL': 'INFO'
    })
    
    # Add backend to Python path
    backend_dir = Path('backend').absolute()
    sys.path.insert(0, str(backend_dir))
    
    try:
        # Import database modules
        from app.core.database import SessionLocal, engine
        from app.models.base import Base
        from app.models.float import ARGOFloat
        from app.models.profile import Profile
        from app.models.measurement import Measurement
        from app.models.bgc_data import BGCData
        
        # Create tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Load sample data
        print("📊 Loading sample data...")
        
        # Load float metadata
        metadata_file = Path("data/raw/float_metadata.json")
        if metadata_file.exists():
            with open(metadata_file) as f:
                float_metadata = json.load(f)
            
            db = SessionLocal()
            
            for metadata in float_metadata:
                try:
                    # Check if float already exists
                    existing_float = db.query(ARGOFloat).filter(
                        ARGOFloat.platform_number == metadata['platform_number']
                    ).first()
                    
                    if not existing_float:
                        from uuid import uuid4
                        from datetime import datetime
                        
                        def parse_date(date_str):
                            try:
                                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            except:
                                return None
                        
                        # Create new float
                        float_obj = ARGOFloat(
                            id=uuid4(),
                            float_id=metadata['platform_number'],
                            platform_number=metadata['platform_number'],
                            wmo_number=metadata.get('wmo_number'),
                            project_name=metadata.get('project_name'),
                            deployment_date=parse_date(metadata.get('deployment_date')),
                            deployment_latitude=metadata.get('deployment_latitude'),
                            deployment_longitude=metadata.get('deployment_longitude'),
                            last_profile_date=parse_date(metadata.get('last_profile_date')),
                            last_latitude=metadata.get('last_latitude'),
                            last_longitude=metadata.get('last_longitude'),
                            current_status=metadata.get('current_status', 'unknown'),
                        )
                        db.add(float_obj)
                        print(f"✅ Added float: {metadata['platform_number']}")
                
                except Exception as e:
                    print(f"⚠️  Warning: Failed to load float {metadata.get('platform_number')}: {e}")
                    db.rollback()
                    continue
            
            db.commit()
            db.close()
            
            print(f"✅ Loaded {len(float_metadata)} floats into database")
        
        print("🎉 Database loading completed!")
        
    except Exception as e:
        print(f"❌ Database loading failed: {e}")
        print("Make sure the database is running and accessible")
        return False
    
    return True

def check_services():
    """Check if required services are running."""
    print("🔍 Checking services...")
    
    services = {
        'PostgreSQL': ('localhost', 5432),
        'Redis': ('localhost', 6379),
        'Qdrant': ('localhost', 6333)
    }
    
    import socket
    
    all_good = True
    for service, (host, port) in services.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service} is running on {host}:{port}")
            else:
                print(f"❌ {service} is not accessible on {host}:{port}")
                all_good = False
        except Exception as e:
            print(f"❌ Could not check {service}: {e}")
            all_good = False
    
    return all_good

def main():
    """Main setup function."""
    print("🌊 WavyAI Local Data Setup")
    print("=" * 50)
    print("This will create sample ARGO data and load it locally")
    print("(No heavy Docker operations - much faster!)")
    print()
    
    # Check if user wants to continue
    response = input("Continue with local data setup? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    # Install packages
    install_required_packages()
    
    # Check services
    if not check_services():
        print("\n⚠️  Some services are not running.")
        print("Please start the minimal services first:")
        print("  python start_services.py --setup")
        print("Or manually: docker-compose -f docker-compose.minimal.yml up -d")
        
        response = input("\nContinue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            return
    
    # Create sample data
    try:
        sample_files, metadata = create_sample_data()
        
        # Load to database
        if check_services():
            load_data_to_database()
        else:
            print("⚠️  Skipping database loading - services not available")
            print("You can load data later when services are running")
        
        print("\n🎉 Local data setup completed!")
        print("\n🚀 Next steps:")
        print("1. Start backend: python start_services.py --backend")
        print("2. Start frontend: python start_services.py --frontend") 
        print("3. Visit: http://localhost:3000")
        print("4. Try asking: 'Show me recent temperature profiles'")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check Python packages: pip install xarray netcdf4 pandas numpy")
        print("2. Ensure write permissions in current directory")
        print("3. Check available disk space")

if __name__ == "__main__":
    main()

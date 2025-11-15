#!/usr/bin/env python3
"""
Setup sample ARGO data without database dependency.
This creates realistic sample data files that can be loaded later.
"""
import os
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
from pathlib import Path

def create_sample_argo_data():
    """Create sample ARGO data files."""
    print("🌊 Creating Sample ARGO Data")
    print("=" * 40)
    
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
    import json
    
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
    
    print("\n🚀 Next Steps:")
    print("1. Start your database (PostgreSQL)")
    print("2. Run: python setup_real_data.py")
    print("3. Or use the web interface at http://localhost:3000/setup")
    
    return sample_files, float_metadata

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing required packages...")
    
    packages = [
        "xarray==2023.12.0",
        "netcdf4==1.6.5", 
        "pandas==2.1.4",
        "numpy",
    ]
    
    for package in packages:
        try:
            import subprocess
            result = subprocess.run(['pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Installed: {package}")
            else:
                print(f"⚠️  Warning: Failed to install {package}")
        except Exception as e:
            print(f"⚠️  Warning: Could not install {package}: {e}")

if __name__ == "__main__":
    print("🌊 WavyAI Sample Data Setup")
    print("=" * 50)
    
    # Install dependencies first
    try:
        install_dependencies()
    except Exception as e:
        print(f"⚠️  Warning: Dependency installation issues: {e}")
        print("You may need to install manually: pip install xarray netcdf4 pandas")
    
    # Create sample data
    try:
        sample_files, metadata = create_sample_argo_data()
        print("\n✅ Sample data setup completed!")
        print("\nYour WavyAI system now has realistic sample data ready to use!")
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {e}")
        print("\nTroubleshooting:")
        print("1. Install required packages: pip install xarray netcdf4 pandas numpy")
        print("2. Ensure you have write permissions in the current directory")
        print("3. Check available disk space")

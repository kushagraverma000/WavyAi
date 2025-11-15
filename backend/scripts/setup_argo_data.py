#!/usr/bin/env python3
"""Setup script for ARGO NetCDF data loading."""
import sys
import os
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_argo_netcdf import ArgoNetCDFLoader


def validate_data_structure(data_path: str) -> bool:
    """Validate the year/month/day directory structure."""
    data_dir = Path(data_path)
    
    if not data_dir.exists():
        print(f"❌ Data directory does not exist: {data_path}")
        return False
    
    print(f"✅ Data directory found: {data_path}")
    
    # Look for year directories
    year_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    
    if not year_dirs:
        print("❌ No year directories found")
        return False
    
    print(f"✅ Found {len(year_dirs)} year directories: {[d.name for d in sorted(year_dirs)]}")
    
    # Check structure of first year
    first_year = sorted(year_dirs)[0]
    month_dirs = [d for d in first_year.iterdir() if d.is_dir()]
    
    if not month_dirs:
        print(f"❌ No month directories found in {first_year}")
        return False
    
    print(f"✅ Found {len(month_dirs)} month directories in {first_year.name}")
    
    # Check structure of first month
    first_month = sorted(month_dirs)[0]
    day_dirs = [d for d in first_month.iterdir() if d.is_dir()]
    
    if not day_dirs:
        print(f"❌ No day directories found in {first_month}")
        return False
    
    print(f"✅ Found {len(day_dirs)} day directories in {first_month}")
    
    # Check for NetCDF files
    first_day = sorted(day_dirs)[0]
    nc_files = list(first_day.glob("*.nc"))
    
    if not nc_files:
        print(f"❌ No NetCDF files found in {first_day}")
        return False
    
    print(f"✅ Found {len(nc_files)} NetCDF files in {first_day}")
    print(f"   Example file: {nc_files[0].name}")
    
    return True


def test_single_file(data_path: str) -> bool:
    """Test loading a single NetCDF file."""
    data_dir = Path(data_path)
    
    # Find first NetCDF file
    nc_files = list(data_dir.rglob("*.nc"))
    
    if not nc_files:
        print("❌ No NetCDF files found for testing")
        return False
    
    test_file = nc_files[0]
    print(f"🧪 Testing with file: {test_file}")
    
    try:
        with ArgoNetCDFLoader(data_path) as loader:
            success = loader.load_netcdf_file(test_file)
            
            if success:
                print("✅ Test file loaded successfully!")
                return True
            else:
                print("❌ Test file failed to load")
                return False
                
    except Exception as e:
        print(f"❌ Error testing file: {e}")
        return False


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup ARGO NetCDF data loading')
    parser.add_argument('data_path', help='Path to ARGO data directory')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate directory structure')
    parser.add_argument('--test-load', action='store_true',
                       help='Test loading a single file')
    
    args = parser.parse_args()
    
    print("🌊 ARGO NetCDF Data Setup")
    print("=" * 50)
    
    # Validate directory structure
    print("\n📁 Validating directory structure...")
    if not validate_data_structure(args.data_path):
        print("\n❌ Directory structure validation failed!")
        sys.exit(1)
    
    if args.validate_only:
        print("\n✅ Directory structure validation completed!")
        return
    
    # Test loading a single file
    if args.test_load:
        print("\n🧪 Testing file loading...")
        if not test_single_file(args.data_path):
            print("\n❌ Test loading failed!")
            sys.exit(1)
        print("\n✅ Test loading completed!")
        return
    
    # Show next steps
    print("\n🚀 Next Steps:")
    print("1. Copy and configure environment variables:")
    print("   cp backend/.env.example backend/.env")
    print("   # Edit backend/.env and set ARGO_DATA_PATH")
    print()
    print("2. Test loading a single file:")
    print(f"   python scripts/setup_argo_data.py '{args.data_path}' --test-load")
    print()
    print("3. Load data for a specific date:")
    print(f"   python scripts/load_argo_netcdf.py '{args.data_path}' --year 2023 --month 1 --day 1")
    print()
    print("4. Load data for a specific month:")
    print(f"   python scripts/load_argo_netcdf.py '{args.data_path}' --year 2023 --month 1")
    print()
    print("5. Load all data (be careful with large datasets!):")
    print(f"   python scripts/load_argo_netcdf.py '{args.data_path}'")


if __name__ == "__main__":
    main()

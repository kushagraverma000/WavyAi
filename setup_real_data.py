#!/usr/bin/env python3
"""
Quick setup script to fetch and load real ARGO data.
Run this script to automatically set up your WavyAI system with real oceanographic data.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

def main():
    """Main setup function."""
    print("🌊 WavyAI Real Data Setup")
    print("=" * 50)
    print()
    
    print("This script will:")
    print("1. 📥 Download recent ARGO data from official sources")
    print("2. 🗄️  Load data into your database")
    print("3. 🚀 Make your AI assistant ready with real ocean data")
    print()
    
    # Check if user wants to continue
    response = input("Continue with setup? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    print("\n🔧 Starting setup process...")
    
    try:
        # Import and run the data fetcher
        from backend.scripts.fetch_and_load_argo_data import main as fetch_main
        
        print("📡 Fetching and loading ARGO data...")
        asyncio.run(fetch_main())
        
        print("\n✅ Setup completed successfully!")
        print("\n🎉 Your WavyAI system is now ready with real ARGO data!")
        print("\nNext steps:")
        print("1. Start the application: docker-compose up -d")
        print("2. Open http://localhost:3000")
        print("3. Ask questions about ocean data!")
        print("\nExample queries:")
        print("- 'Show me temperature profiles in the Atlantic Ocean'")
        print("- 'What are the salinity levels near the equator?'")
        print("- 'Find ARGO floats with recent data'")
        
    except ImportError as e:
        print(f"\n❌ Error: Could not import required modules: {e}")
        print("\nPlease ensure you have:")
        print("1. Installed backend dependencies: pip install -r backend/requirements.txt")
        print("2. Set up your environment variables in backend/.env")
        print("3. Started the database: docker-compose up -d postgres")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify database is running: docker-compose ps")
        print("3. Check backend logs: docker-compose logs backend")


if __name__ == "__main__":
    main()

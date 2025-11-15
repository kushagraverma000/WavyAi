#!/usr/bin/env python3
"""
Fix environment setup for WavyAI without Docker dependency.
This script will update your .env file with proper values.
"""
import os
from pathlib import Path

def fix_env_setup():
    """Fix the environment setup."""
    print("🔧 Fixing WavyAI Environment Setup")
    print("=" * 40)
    
    # Path to backend .env file
    env_file = Path("backend/.env")
    env_example = Path("backend/.env.example")
    
    # Read the example file
    if not env_example.exists():
        print("❌ Error: backend/.env.example not found")
        return False
    
    print("📝 Updating backend/.env file...")
    
    # Create proper .env content
    env_content = """# Database
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
QDRANT_URL=http://localhost:6333

# Google APIs (add your keys here)
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# ARGO Data Path
ARGO_DATA_PATH=/Users/kushagraverma/WavyAI/data/raw

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# JWT and Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
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

# Celery (if using background tasks)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
"""
    
    # Write the .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Updated backend/.env file")
    
    # Create data directory
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Created data directory")
    
    # Update frontend .env
    frontend_env = Path("frontend/.env")
    frontend_content = """VITE_API_URL=http://localhost:8000/api/v1
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
"""
    
    with open(frontend_env, 'w') as f:
        f.write(frontend_content)
    
    print("✅ Updated frontend/.env file")
    
    print("\n🎯 Next Steps:")
    print("1. Add your Google API keys to backend/.env and frontend/.env")
    print("2. Start services manually or with Docker")
    print("3. Run the setup script again")
    
    print("\n📋 Manual Service Start (if Docker is slow):")
    print("# Start PostgreSQL locally (if you have it installed)")
    print("# Or use Docker for just the database:")
    print("# docker run -d --name wavyai-postgres -p 5432:5432 -e POSTGRES_DB=wavyai -e POSTGRES_USER=wavyai -e POSTGRES_PASSWORD=wavyai_password postgres:15")
    
    return True

if __name__ == "__main__":
    success = fix_env_setup()
    if success:
        print("\n✅ Environment setup fixed!")
        print("You can now run: python setup_real_data.py")
    else:
        print("\n❌ Failed to fix environment setup")

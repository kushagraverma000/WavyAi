"""Initialize database with tables and extensions."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import get_settings
from app.core.database import Base, engine
# Import all models to register them with Base
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData
from app.models.user_context import UserContext

settings = get_settings()


def init_database():
    """Initialize database with tables and extensions."""
    try:
        print("Creating database extensions...")
        with engine.connect() as conn:
            # Create PostGIS extension
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.commit()
                print("PostGIS extension created successfully")
            except Exception as e:
                print(f"Warning: Could not create PostGIS extension: {e}")
            
            # Create TimescaleDB extension
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
                conn.commit()
                print("TimescaleDB extension created successfully")
            except Exception as e:
                print(f"Warning: Could not create TimescaleDB extension: {e}")
        
        print("Creating database tables...")
        # Import models to register them
        import app.models
        Base.metadata.create_all(bind=engine)
        print(f"Created {len(Base.metadata.tables)} tables")
        
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


if __name__ == "__main__":
    init_database()


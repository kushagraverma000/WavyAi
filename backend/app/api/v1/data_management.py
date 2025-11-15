"""Data management endpoints for fetching and loading ARGO data."""
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.argo_data_fetcher import get_argo_fetcher
from app.core.database import SessionLocal
from app.models.float import ARGOFloat
from app.models.profile import Profile

router = APIRouter()
logger = get_logger(__name__)


class DataFetchRequest(BaseModel):
    """Request model for data fetching."""
    days_back: int = 30
    max_files: int = 50
    force_refresh: bool = False


class DataSummaryResponse(BaseModel):
    """Response model for data summary."""
    total_floats: int
    total_profiles: int
    total_files: int
    data_size_mb: float
    date_range: str
    last_updated: str


@router.post("/fetch-argo-data")
async def fetch_argo_data(
    request: DataFetchRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Fetch ARGO data from official sources."""
    try:
        logger.info(f"Starting ARGO data fetch: {request.days_back} days, max {request.max_files} files")
        
        # Start background task for data fetching
        background_tasks.add_task(
            _fetch_and_load_data_task,
            request.days_back,
            request.max_files,
            request.force_refresh
        )
        
        return {
            "status": "started",
            "message": f"ARGO data fetch started for last {request.days_back} days",
            "max_files": request.max_files,
            "estimated_time": "5-15 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to start data fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start data fetch: {str(e)}")


@router.get("/data-summary")
async def get_data_summary() -> DataSummaryResponse:
    """Get summary of current ARGO data in the database."""
    try:
        db = SessionLocal()
        
        # Get database counts
        total_floats = db.query(ARGOFloat).count()
        total_profiles = db.query(Profile).count()
        
        # Get file system summary
        fetcher = get_argo_fetcher()
        file_summary = await fetcher.get_data_summary()
        
        db.close()
        
        return DataSummaryResponse(
            total_floats=total_floats,
            total_profiles=total_profiles,
            total_files=file_summary['total_files'],
            data_size_mb=file_summary['size_mb'],
            date_range=file_summary['date_range'] or 'No data',
            last_updated="Recently updated"
        )
        
    except Exception as e:
        logger.error(f"Failed to get data summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get data summary: {str(e)}")


@router.get("/data-status")
async def get_data_status() -> Dict[str, Any]:
    """Get current status of data loading operations."""
    try:
        # This would typically check a task queue or status store
        # For now, return basic status
        db = SessionLocal()
        
        float_count = db.query(ARGOFloat).count()
        profile_count = db.query(Profile).count()
        
        db.close()
        
        status = "ready" if float_count > 0 else "no_data"
        
        return {
            "status": status,
            "floats_loaded": float_count,
            "profiles_loaded": profile_count,
            "ready_for_queries": float_count > 0,
            "message": "Data is ready for queries" if float_count > 0 else "No data loaded yet"
        }
        
    except Exception as e:
        logger.error(f"Failed to get data status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get data status: {str(e)}")


@router.post("/initialize-sample-data")
async def initialize_sample_data(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Initialize with sample ARGO data for immediate testing."""
    try:
        logger.info("Initializing sample ARGO data")
        
        background_tasks.add_task(_initialize_sample_data_task)
        
        return {
            "status": "started",
            "message": "Sample data initialization started",
            "estimated_time": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize sample data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize sample data: {str(e)}")


async def _fetch_and_load_data_task(days_back: int, max_files: int, force_refresh: bool):
    """Background task to fetch and load ARGO data."""
    try:
        logger.info(f"Background task: Fetching ARGO data ({days_back} days, {max_files} files)")
        
        # Import here to avoid circular imports
        from backend.scripts.fetch_and_load_argo_data import ARGODataLoader
        
        loader = ARGODataLoader()
        await loader.fetch_and_load_data(days_back, max_files)
        
        logger.info("Background task: ARGO data fetch and load completed successfully")
        
    except Exception as e:
        logger.error(f"Background task failed: {e}")


async def _initialize_sample_data_task():
    """Background task to initialize sample data."""
    try:
        logger.info("Background task: Initializing sample data")
        
        fetcher = get_argo_fetcher()
        
        # Create sample data files
        sample_files = await fetcher._create_sample_data()
        logger.info(f"Created {len(sample_files)} sample files")
        
        # Load sample float metadata
        float_metadata = fetcher._create_sample_float_metadata()
        logger.info(f"Created metadata for {len(float_metadata)} sample floats")
        
        # Load into database
        from backend.scripts.fetch_and_load_argo_data import ARGODataLoader
        loader = ARGODataLoader()
        
        # Load float metadata
        await loader._load_float_metadata(float_metadata)
        
        # Load profile files
        loaded_count = 0
        for file_path in sample_files:
            try:
                if await loader._load_profile_file(file_path):
                    loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load sample file {file_path}: {e}")
                continue
        
        logger.info(f"Background task: Sample data initialization completed - {loaded_count} profiles loaded")
        
    except Exception as e:
        logger.error(f"Sample data initialization failed: {e}")

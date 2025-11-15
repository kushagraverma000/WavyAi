"""Data ingestion endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import tempfile
import os

from app.core.database import get_db
from app.core.logging import get_logger
from app.services.data_ingestion import DataIngestionService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ingest")
async def ingest_netcdf_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Ingest a NetCDF file."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Ingest file
            ingestion_service = DataIngestionService(db)
            result = ingestion_service.ingest_netcdf_file(tmp_file_path)
            
            if result["status"] == "error":
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to ingest file: {result.get('error', 'Unknown error')}",
                )
            
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        logger.error("File ingestion failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {str(e)}")


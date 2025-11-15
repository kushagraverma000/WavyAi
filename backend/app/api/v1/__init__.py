"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import query, profiles, floats, health, data, export, data_management, visualization, mock_data, simple_viz

router = APIRouter()

# Include route modules
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(query.router, prefix="/query", tags=["query"])
router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
router.include_router(floats.router, prefix="/floats", tags=["floats"])
router.include_router(data.router, prefix="/data", tags=["data"])
router.include_router(export.router, prefix="/export", tags=["export"])
router.include_router(data_management.router, prefix="/data-management", tags=["data-management"])
router.include_router(visualization.router, prefix="/viz", tags=["visualization"])
router.include_router(mock_data.router, prefix="/viz", tags=["mock-data"])
router.include_router(simple_viz.router, prefix="/simple", tags=["simple-viz"])


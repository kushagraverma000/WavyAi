from datetime import date, datetime
import re
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .config import settings
from .csv_utils import ensure_day_csv, find_netcdf_for_day, load_depth_profile, load_map_features
from .db import Base, engine, get_db, get_database_backend
from .document import Document
from .models import DaySummary
from .simple_llm import answer_with_gemini as simple_answer_with_gemini
try:  # In full mode, prefer real Gemini+LangChain stack if available
    if settings.mode == "full":
        from .llm import answer_with_gemini as full_answer_with_gemini
    else:  # light mode
        full_answer_with_gemini = None  # type: ignore[assignment]
except Exception:  # pragma: no cover
    full_answer_with_gemini = None  # type: ignore[assignment]
from .sample_data import (
    SALINITY_DEPTH_DATA,
    SAMPLE_FLOATS,
    SAMPLE_PROFILES,
    TEMPERATURE_DEPTH_DATA,
)
from .schemas import (
    DataStatus,
    DataSummary,
    PaginatedFloats,
    PaginatedProfiles,
    QueryRequest,
    QueryResponse,
    Source,
)
from .vectorstore import search_month


_MONTH_NAME_TO_NUM = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _infer_date_from_text(text: str) -> date | None:
    """Best-effort parser for dates written inside the user's question.

    Example: "give data for this date 12 jan" -> 12 Jan of the current UTC year.
    This is only used when payload.selected_date is not provided explicitly.
    """

    if not text:
        return None

    # Look for patterns like "12 nov 2023" or "12 nov" (case-insensitive).
    # If the year is omitted, fall back to the current year.
    match = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3,9})(?:\s+(\d{4}))?\b", text, flags=re.IGNORECASE)
    if not match:
        return None

    day = int(match.group(1))
    month_name = match.group(2).lower()[:3]
    month = _MONTH_NAME_TO_NUM.get(month_name)
    if month is None:
        return None

    has_year = match.group(3) is not None
    year = int(match.group(3)) if has_year else datetime.utcnow().year
    try:
        return date(year, month, day)
    except ValueError:
        return None


app = FastAPI(title="WavyAI Backend", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "database": get_database_backend(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_api(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:  # noqa: ARG001
    text_query = (payload.query or "").strip()

    if not text_query and payload.selected_date is None:
        raise HTTPException(status_code=400, detail="Either query or selected_date must be provided.")

    # Derive an "effective" date for ARGO context:
    # - start from the picker-provided selected_date (if any)
    # - but if the user mentions a specific date in the question text (e.g. "12 nov 2023"),
    #   prefer that parsed date.
    effective_date = payload.selected_date
    if text_query:
        inferred = _infer_date_from_text(text_query)
        if inferred is not None and (effective_date is None or effective_date != inferred):
            effective_date = inferred

    question_parts: List[str] = []
    if text_query:
        question_parts.append(f"User question: {text_query}")
    if effective_date is not None:
        question_parts.append(
            "The user selected this specific date for ARGO data: "
            f"{effective_date.isoformat()}. Explain the ocean conditions on this date in simple language."
        )

    question_for_llm = "\n".join(question_parts) if question_parts else "Summarize the ARGO data."  # pragma: no cover

    # Retrieve context documents based on selected date (if any)
    docs: List[Document] = []
    if effective_date is not None:
        year = effective_date.year
        month = effective_date.month
        # Try vector search within that month (best-effort; may return empty list)
        try:
            docs = search_month(year, month, f"ocean conditions on {effective_date.isoformat()}", k=5)
        except Exception:  # pragma: no cover
            docs = []

        # Fallback: use DaySummary from database if vector search empty
        if not docs:
            summary = db.query(DaySummary).filter(DaySummary.date == effective_date).one_or_none()
            if summary is not None:
                docs = [
                    Document(
                        page_content=summary.summary_text,
                        metadata={
                            "date": summary.date.isoformat(),
                            "year": summary.year,
                            "month": summary.month,
                            "day": summary.day,
                        },
                    )
                ]

    # Choose LLM implementation based on mode / availability
    try:
        if full_answer_with_gemini is not None:
            response_text = full_answer_with_gemini(question_for_llm, context_docs=docs or None)
        else:
            response_text = simple_answer_with_gemini(question_for_llm, context_docs=docs or None)
    except RuntimeError as exc:
        response_text = (
            "Gemini is not configured (" + str(exc) + "). "
            "Please set GOOGLE_API_KEY or WAVYAI_GEMINI_API_KEY to enable AI answers."
        )

    now = datetime.utcnow()

    metadata: dict = {"demo": True}
    if effective_date is not None:
        metadata["selected_date"] = effective_date.isoformat()

    return QueryResponse(
        response=response_text,
        sources=[],
        visualization=None,
        data_table=None,
        user_type=None,
        query_intent=None,
        entities=None,
        metadata=metadata,
        timestamp=now,
    )


@app.get("/api/v1/visualization/day/depth-profile")
def get_day_depth_profile(day: str = Query(...), profile_index: int = Query(0, ge=0)) -> dict:
    """Return depth-profile data (temperature & salinity vs depth) for a given day.

    Data come from the per-day CSV generated from the NetCDF file.
    """

    try:
        target_date = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD.")

    data = load_depth_profile(target_date, profile_index=profile_index)
    return {
        "data": data,
        "metadata": {
            "parameter": "temperature_salinity_profile",
            "units": "mixed",
            "date": target_date.isoformat(),
            "profile_index": profile_index,
        },
    }


@app.get("/api/v1/export/day-csv")
def export_day_csv(day: str = Query(...)) -> StreamingResponse:
    """Download the CSV for a specific calendar day, generating it from NetCDF if needed."""

    try:
        target_date = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD.")

    paths = ensure_day_csv(target_date)
    if paths is None:
        raise HTTPException(status_code=404, detail="No NetCDF/CSV data found for this date.")

    file_obj = paths.csv_path.open("rb")
    headers = {"Content-Disposition": f"attachment; filename=argo_{target_date.isoformat()}.csv"}
    return StreamingResponse(file_obj, media_type="text/csv", headers=headers)


@app.get("/api/v1/export/day-netcdf")
def export_day_netcdf(day: str = Query(...)) -> StreamingResponse:
    """Download the raw NetCDF file for a specific calendar day."""

    try:
        target_date = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD.")

    path = find_netcdf_for_day(target_date)
    if path is None:
        raise HTTPException(status_code=404, detail="No NetCDF file found for this date.")

    file_obj = path.open("rb")
    headers = {"Content-Disposition": f"attachment; filename={path.name}"}
    return StreamingResponse(file_obj, media_type="application/x-netcdf", headers=headers)


@app.get("/api/v1/profiles", response_model=PaginatedProfiles)
def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1),
    float_id: str | None = None,
) -> PaginatedProfiles:
    items = SAMPLE_PROFILES
    if float_id is not None:
        items = [p for p in items if p.get("float_id") == float_id]

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    sliced = items[start:end]

    return PaginatedProfiles(
        profiles=sliced,
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get("/api/v1/profiles/{profile_id}")
def get_profile(profile_id: str) -> dict:
    for p in SAMPLE_PROFILES:
        if p.get("id") == profile_id or p.get("float_id") == profile_id:
            return p
    raise HTTPException(status_code=404, detail="Profile not found")


@app.get("/api/v1/floats", response_model=PaginatedFloats)
def list_floats(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1),
    status: str | None = None,
) -> PaginatedFloats:
    items = SAMPLE_FLOATS
    if status is not None:
        items = [f for f in items if (f.get("current_status") or "").lower() == status.lower()]

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    sliced = items[start:end]

    return PaginatedFloats(
        floats=sliced,
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get("/api/v1/floats/{float_id}")
def get_float(float_id: str) -> dict:
    for f in SAMPLE_FLOATS:
        if f.get("id") == float_id or f.get("float_id") == float_id:
            return f
    raise HTTPException(status_code=404, detail="Float not found")


@app.get("/api/v1/visualization/float-locations")
def get_float_locations(
    limit: int = Query(100, ge=1),
    day: str | None = None,
) -> dict:
    """Return ARGO float locations.

    - If a `day` (YYYY-MM-DD) is provided, load positions from that day's CSV/NetCDF.
    - Otherwise, fall back to bundled SAMPLE_FLOATS.
    """

    if day is not None:
        try:
            target_date = date.fromisoformat(day)
        except ValueError:
            target_date = None
        if target_date is not None:
            return load_map_features(target_date, max_floats=limit)

    features: List[dict] = []
    for f in SAMPLE_FLOATS[:limit]:
        lon = f.get("last_longitude") or f.get("deployment_longitude") or 0.0
        lat = f.get("last_latitude") or f.get("deployment_latitude") or 0.0
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f.get("float_id"),
                    "name": f.get("name"),
                    "status": f.get("current_status"),
                    "last_update": f.get("last_profile_date"),
                    "total_profiles": int((f.get("metadata") or {}).get("cycles", 0)),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/v1/visualization/profile-locations")
def get_profile_locations(limit: int = Query(100, ge=1)) -> dict:
    profiles = SAMPLE_PROFILES[:limit]
    return {"profiles": profiles, "total": len(SAMPLE_PROFILES)}


@app.get("/api/v1/visualization/profiles/{profile_id}/temperature-depth")
def get_temperature_depth_chart(profile_id: str) -> dict:  # noqa: ARG001
    return {"data": TEMPERATURE_DEPTH_DATA, "metadata": {"parameter": "temperature", "units": "°C"}}


@app.get("/api/v1/visualization/profiles/{profile_id}/salinity-depth")
def get_salinity_depth_chart(profile_id: str) -> dict:  # noqa: ARG001
    return {"data": SALINITY_DEPTH_DATA, "metadata": {"parameter": "salinity", "units": "PSU"}}


@app.get("/api/v1/visualization/profiles/{profile_id}/ts-diagram")
def get_ts_diagram(profile_id: str) -> dict:  # noqa: ARG001
    return {"data": [], "metadata": {"parameter": "ts_diagram", "units": "mixed"}}


@app.get("/api/v1/profiles/{profile_id}/export/csv")
def export_profile_csv(profile_id: str) -> StreamingResponse:  # noqa: ARG001
    csv_content = (
        "level,pressure,depth,temperature,salinity\n"
        "1,5,5.1,25.2,35.1\n"
        "2,55,56.1,24.8,35.0\n"
        "3,105,107.1,24.2,34.9\n"
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=argo_profile_{profile_id}.csv"},
    )


@app.get("/api/v1/simple/export/profiles/csv")
def simple_export_profiles_csv() -> StreamingResponse:
    csv_content = (
        "id,float_id,profile_number,profile_date,latitude,longitude\n"
        + "\n".join(
            f"{p['id']},{p['float_id']},{p['profile_number']},{p['profile_date']},{p['latitude']},{p['longitude']}"
            for p in SAMPLE_PROFILES
        )
        + "\n"
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=profiles.csv"},
    )


@app.get("/api/v1/export/profiles/netcdf")
def export_profiles_netcdf() -> Response:
    content = b"NetCDF export is not implemented in the prototype."
    return Response(
        content,
        media_type="application/x-netcdf",
        headers={"Content-Disposition": "attachment; filename=profiles.nc"},
    )


@app.get("/api/v1/export/floats/netcdf")
def export_floats_netcdf() -> Response:
    content = b"NetCDF export is not implemented in the prototype."
    return Response(
        content,
        media_type="application/x-netcdf",
        headers={"Content-Disposition": "attachment; filename=floats.nc"},
    )


@app.get("/api/v1/data-management/data-summary", response_model=DataSummary)
def data_summary() -> DataSummary:
    total_files = len(SAMPLE_PROFILES)
    total_floats = len(SAMPLE_FLOATS)
    total_profiles = len(SAMPLE_PROFILES)
    data_size_mb = float(total_files) * 0.1
    date_range = "prototype-only"
    last_updated = datetime.utcnow().isoformat() + "Z"

    return DataSummary(
        total_floats=total_floats,
        total_profiles=total_profiles,
        total_files=total_files,
        data_size_mb=data_size_mb,
        date_range=date_range,
        last_updated=last_updated,
    )


@app.get("/api/v1/data-management/data-status", response_model=DataStatus)
def data_status() -> DataStatus:
    status = "ready" if SAMPLE_PROFILES and SAMPLE_FLOATS else "no_data"
    message = "Prototype sample data is loaded in-memory and ready for queries."
    return DataStatus(
        status=status,
        floats_loaded=len(SAMPLE_FLOATS),
        profiles_loaded=len(SAMPLE_PROFILES),
        ready_for_queries=bool(SAMPLE_PROFILES and SAMPLE_FLOATS),
        message=message,
    )


@app.post("/api/v1/data-management/fetch-argo-data")
def fetch_argo_data() -> dict:
    return {
        "status": "started",
        "message": "Real ARGO data download is not implemented in the prototype; using bundled sample data instead.",
        "estimated_time": "a few minutes",
    }


@app.post("/api/v1/data-management/initialize-sample-data")
def initialize_sample_data() -> dict:
    return {
        "status": "started",
        "message": "Sample ARGO data is already bundled with the prototype and ready to use.",
        "estimated_time": "less than a minute",
    }

"""Ingestion utilities for converting raw ARGO NetCDF files into
lightweight structured storage (Postgres day summaries + FAISS).

This first version focuses on:
- Creating a DaySummary row per day
- Creating a FAISS document per day for semantic search / context

It does NOT yet ingest full per-profile measurements (to keep things
fast and robust across different NetCDF variants). You can extend
this later to populate the Float/Profile tables in more detail.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

import xarray as xr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, SessionLocal, engine
from .document import Document
from .models import DaySummary
from .vectorstore import upsert_day_summaries


def _parse_date_from_filename(path: Path) -> date | None:
    """Extract YYYYMMDD from filenames like 20171231_prof.nc.

    Returns a date object or None if parsing fails.
    """

    stem = path.stem  # e.g. "20171231_prof"
    for part in stem.split("_"):
        if len(part) == 8 and part.isdigit():
            y = int(part[0:4])
            m = int(part[4:6])
            d = int(part[6:8])
            try:
                return date(y, m, d)
            except ValueError:
                return None
    return None


def summarize_netcdf_day(path: Path) -> str:
    """Generate a simple human-readable summary for a day's NetCDF file.

    This uses only very generic NetCDF assumptions so it works even if
    variable naming differs slightly between datasets.
    """

    try:
        ds = xr.open_dataset(path, decode_cf=True)
    except Exception as exc:  # pragma: no cover - defensive
        return f"ARGO profiles for {path.name} (could not fully parse dataset: {exc})"

    n_profiles = None
    for dim_name in ("N_PROF", "PROFILE", "n_prof"):
        if dim_name in ds.dims:
            n_profiles = int(ds.sizes[dim_name])
            break

    lat_var = None
    for v in ("LATITUDE", "latitude", "lat"):
        if v in ds.variables:
            lat_var = v
            break

    lon_var = None
    for v in ("LONGITUDE", "longitude", "lon"):
        if v in ds.variables:
            lon_var = v
            break

    lat_span = "unknown"
    lon_span = "unknown"
    try:
        if lat_var is not None:
            lats = ds[lat_var].values
            lats = lats[~(lats != lats)]  # drop NaNs
            if lats.size:
                lat_span = f"{float(lats.min()):.1f}° to {float(lats.max()):.1f}°"
        if lon_var is not None:
            lons = ds[lon_var].values
            lons = lons[~(lons != lons)]
            if lons.size:
                lon_span = f"{float(lons.min()):.1f}° to {float(lons.max()):.1f}°"
    except Exception:  # pragma: no cover - best-effort only
        pass

    pieces: List[str] = [
        f"NetCDF file {path.name} contains ARGO profile data.",
    ]

    if n_profiles is not None:
        pieces.append(f"It includes approximately {n_profiles} vertical profiles.")

    pieces.append(f"Latitude coverage: {lat_span}. Longitude coverage: {lon_span}.")

    return " " .join(pieces)


def ingest_day_file(path: Path, db: Session) -> None:
    """Ingest a single NetCDF file as a DaySummary + FAISS document."""

    day = _parse_date_from_filename(path)
    if day is None:
        return

    # Build summary text
    summary_text = summarize_netcdf_day(path)

    # Upsert DB row
    year = day.year
    month = day.month
    day_num = day.day

    existing = db.query(DaySummary).filter(DaySummary.date == day).one_or_none()
    if existing:
        existing.summary_text = summary_text
        existing.year = year
        existing.month = month
        existing.day = day_num
    else:
        db.add(
            DaySummary(
                date=day,
                year=year,
                month=month,
                day=day_num,
                summary_text=summary_text,
            )
        )

    # Add to FAISS for this month
    doc = Document(
        page_content=summary_text,
        metadata={
            "date": day.isoformat(),
            "year": year,
            "month": month,
            "day": day_num,
            "file_path": str(path),
        },
    )
    upsert_day_summaries(year, month, [doc])


def ingest_all_raw(root: Path | None = None) -> None:
    """Traverse the raw data tree and ingest all *_prof.nc files.

    This is intentionally simple and safe to re-run; it will update
    existing DaySummary rows and FAISS entries.
    """

    if root is None:
        root = settings.raw_data_root

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for path in sorted(root.rglob("*_prof.nc")):
            ingest_day_file(path, db)
            try:
                db.commit()
            except IntegrityError:
                # Duplicate date (UNIQUE constraint) or similar issue; skip and continue
                db.rollback()


def main() -> None:  # pragma: no cover - CLI entrypoint
    # For the developer workstation, default to ingesting only recent data (year 2025)
    root = settings.raw_data_root / "2025"
    print(f"Ingesting raw ARGO data from {root} ...")
    ingest_all_raw(root=root)
    print("Done.")


if __name__ == "__main__":  # pragma: no cover
    main()

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import xarray as xr

from .config import settings


@dataclass
class DayPaths:
    day: date
    netcdf_path: Path
    csv_path: Path


def _csv_root() -> Path:
    root = getattr(settings, "csv_data_root", None)
    if root is None:
        # Default alongside raw/ as csv/
        root = settings.project_root / "csv"
    root.mkdir(parents=True, exist_ok=True)
    return root


def find_netcdf_for_day(day: date) -> Optional[Path]:
    """Locate a NetCDF file for the given calendar day.

    We search under raw_data_root recursively for files named
    YYYYMMDD_prof.nc and return the first match.
    """

    pattern = f"{day.strftime('%Y%m%d')}_prof.nc"
    for path in settings.raw_data_root.rglob(pattern):
        if path.is_file():
            return path
    return None


def day_csv_path(day: date) -> Path:
    root = _csv_root()
    return root / str(day.year) / f"{day.month:02d}" / f"{day.strftime('%Y%m%d')}.csv"


def ensure_day_csv(day: date) -> Optional[DayPaths]:
    """Ensure there is a CSV for this day, creating it from NetCDF if needed.

    The CSV schema is long format with one row per profile+level:
    profile_index, level_index, latitude, longitude, depth, pressure,
    temperature, salinity
    """

    netcdf_path = find_netcdf_for_day(day)
    if netcdf_path is None:
        return None

    csv_path = day_csv_path(day)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if csv_path.exists():
        return DayPaths(day=day, netcdf_path=netcdf_path, csv_path=csv_path)

    ds = xr.open_dataset(netcdf_path, decode_cf=True)

    # Profiles
    n_prof = None
    for dim in ("N_PROF", "PROFILE", "n_prof"):
        if dim in ds.dims:
            n_prof = int(ds.sizes[dim])
            prof_dim_name = dim
            break
    if n_prof is None:
        # Fall back: treat whole file as a single pseudo-profile
        n_prof = 1
        prof_dim_name = None

    # Latitude / longitude per profile
    lat_var_name = next((v for v in ("LATITUDE", "latitude", "lat") if v in ds.variables), None)
    lon_var_name = next((v for v in ("LONGITUDE", "longitude", "lon") if v in ds.variables), None)

    if lat_var_name is not None:
        lats = np.asarray(ds[lat_var_name]).reshape(-1)
    else:
        lats = np.full(n_prof, np.nan)

    if lon_var_name is not None:
        lons = np.asarray(ds[lon_var_name]).reshape(-1)
    else:
        lons = np.full(n_prof, np.nan)

    # Vertical variables
    pres_var_name = next((v for v in ("PRES", "PRES_ADJUSTED", "pressure", "PRESSURE") if v in ds.variables), None)
    temp_var_name = next((v for v in ("TEMP", "TEMP_ADJUSTED", "temperature", "TEMP_C") if v in ds.variables), None)
    sal_var_name = next((v for v in ("PSAL", "PSAL_ADJUSTED", "salinity") if v in ds.variables), None)

    # Determine level dimension if present
    level_dim_name = None
    for cand in ("N_LEVELS", "DEPTH", "depth", "LEVEL", "level"):
        if cand in ds.dims:
            level_dim_name = cand
            break

    # Helper to get array with shape (n_prof, n_levels)
    def _as_prof_level(name: Optional[str]) -> Optional[np.ndarray]:
        if name is None:
            return None
        var = ds[name]
        arr = np.asarray(var)
        if arr.ndim == 2:
            return arr
        # Try to align dims to (prof, level)
        dims = list(var.dims)
        if prof_dim_name in dims and level_dim_name in dims:
            # Reorder
            arr = np.moveaxis(arr, (dims.index(prof_dim_name), dims.index(level_dim_name)), (0, 1))
            return arr
        # If 1D, broadcast to all profiles
        if arr.ndim == 1 and level_dim_name in var.dims:
            return np.tile(arr.reshape(1, -1), (n_prof, 1))
        return None

    pres = _as_prof_level(pres_var_name)
    temp = _as_prof_level(temp_var_name)
    sal = _as_prof_level(sal_var_name)

    # Determine number of levels from first non-None variable
    n_levels = 1
    for arr in (pres, temp, sal):
        if arr is not None and arr.ndim == 2:
            n_levels = arr.shape[1]
            break

    rows: List[dict] = []
    for iprof in range(n_prof):
        lat = float(lats[iprof]) if iprof < len(lats) else float("nan")
        lon = float(lons[iprof]) if iprof < len(lons) else float("nan")
        for ilevel in range(n_levels):
            row = {
                "profile_index": iprof,
                "level_index": ilevel,
                "latitude": lat,
                "longitude": lon,
            }
            if pres is not None and iprof < pres.shape[0] and ilevel < pres.shape[1]:
                row["pressure"] = float(pres[iprof, ilevel])
            if temp is not None and iprof < temp.shape[0] and ilevel < temp.shape[1]:
                row["temperature"] = float(temp[iprof, ilevel])
            if sal is not None and iprof < sal.shape[0] and ilevel < sal.shape[1]:
                row["salinity"] = float(sal[iprof, ilevel])
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)

    return DayPaths(day=day, netcdf_path=netcdf_path, csv_path=csv_path)


def load_map_features(day: date, max_floats: int = 100) -> dict:
    paths = ensure_day_csv(day)
    if paths is None:
        return {"type": "FeatureCollection", "features": []}

    df = pd.read_csv(paths.csv_path)
    # One point per profile (use first level of each profile)
    profiles = df.groupby("profile_index").first().reset_index()
    profiles = profiles.head(max_floats)

    features: List[dict] = []
    for _, row in profiles.iterrows():
        lat = float(row.get("latitude", float("nan")))
        lon = float(row.get("longitude", float("nan")))
        if not np.isfinite(lat) or not np.isfinite(lon):
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f"{day.isoformat()}_prof_{int(row['profile_index'])}",
                    "profile_index": int(row["profile_index"]),
                    "date": day.isoformat(),
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}


def load_depth_profile(day: date, profile_index: int = 0) -> List[dict]:
    paths = ensure_day_csv(day)
    if paths is None:
        return []

    df = pd.read_csv(paths.csv_path)
    df_prof = df[df["profile_index"] == profile_index].copy()
    if df_prof.empty:
        # Fallback: use first profile
        df_prof = df[df["profile_index"] == df["profile_index"].min()].copy()

    # Prefer pressure as depth if available
    if "pressure" in df_prof.columns:
        depth = df_prof["pressure"].astype(float).to_list()
    elif "depth" in df_prof.columns:
        depth = df_prof["depth"].astype(float).to_list()
    else:
        depth = list(range(len(df_prof)))

    temp = df_prof["temperature"].astype(float).to_list() if "temperature" in df_prof.columns else [np.nan] * len(depth)
    sal = df_prof["salinity"].astype(float).to_list() if "salinity" in df_prof.columns else [np.nan] * len(depth)

    out: List[dict] = []
    for d, t, s in zip(depth, temp, sal):
        row = {"depth": d}
        if np.isfinite(t):
            row["temperature"] = t
        if np.isfinite(s):
            row["salinity"] = s
        out.append(row)
    return out

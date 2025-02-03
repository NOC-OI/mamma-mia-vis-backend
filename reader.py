import zarr
from typing import List, Optional


class ZarrReader:
    """Simple reader for Zarr stores using zarr.open."""

    @staticmethod
    def list_variables(store_path: str, group: Optional[str] = None) -> List[str]:
        """List variables in the Zarr group."""
        zarr_group = zarr.open(store_path, mode="r")
        if group:
            zarr_group = zarr_group[group]
        return list(zarr_group.array_keys())

    @staticmethod
    def list_dimensions(store_path: str, group: Optional[str] = None) -> List[str]:
        """List dimensions in the Zarr group."""
        zarr_group = zarr.open(store_path, mode="r")
        if group:
            zarr_group = zarr_group[group]
        dimensions = {}
        for key in zarr_group.array_keys():
            array = zarr_group[key]
            dimensions[key] = array.shape
        return dimensions

    @staticmethod
    def list_time_values(store_path: str, group: Optional[str] = None) -> List[str]:
        """List time values if a 'time' dimension exists."""
        zarr_group = zarr.open(store_path, mode="r")
        if group:
            zarr_group = zarr_group[group]
        if "time" in zarr_group:
            time_array = zarr_group["time"][:]
            return [str(t) for t in time_array]
        return []

    @staticmethod
    def get_trajectory(store_path: str, group: Optional[str] = None) -> dict:
        """Get latitude and longitude arrays."""
        zarr_group = zarr.open(store_path, mode="r")
        if group:
            zarr_group = zarr_group[group]
        result = {}

        # Check for datetimes
        if "datetimes" in zarr_group or "time" in zarr_group:
            result["datetimes"] = zarr_group.get("datetimes", zarr_group.get("time"))[:].tolist()

        # Check for latitudes
        if "latitudes" in zarr_group or "latitude" in zarr_group or "nav_lat" in zarr_group:
            result["latitudes"] = zarr_group.get("latitude", zarr_group.get("latitudes", zarr_group.get("nav_lat")))[:].tolist()

        # Check for longitudes
        if "longitudes" in zarr_group or "longitude" in zarr_group or "nav_lon" in zarr_group:
            result["longitudes"] = zarr_group.get("longitude", zarr_group.get("longitudes", zarr_group.get("nav_lon")))[:].tolist()

        # Check for depths
        if "depths" in zarr_group or "depth" in zarr_group or "deptht" in zarr_group:
            result["depths"] = zarr_group.get("depths", zarr_group.get("depth", zarr_group.get("deptht")))[:].tolist()

        return result
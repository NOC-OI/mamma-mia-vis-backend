from fastapi import APIRouter, Query
from typing import List, Optional
from fastapi.responses import JSONResponse
from  reader import ZarrReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZarrTilerFactory:
    """Factory to expose Zarr reader functionalities via API."""

    def __init__(self):
        self.router = APIRouter()

        @self.router.get(
            "/zarr_variables",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's Variables."}},
        )
        def variable_endpoint(
            url: str = Query(..., description="Dataset URL"),
            group: Optional[str] = Query(None, description="Zarr group to inspect"),
        ) -> List[str]:
            """Return available variables."""
            return ZarrReader.list_variables(url, group)

        @self.router.get(
            "/zarr_dimensions",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's Dimensions."}},
        )
        def dimensions_endpoint(
            url: str = Query(..., description="Dataset URL"),
            group: Optional[str] = Query(None, description="Zarr group to inspect"),
        ) -> dict:
            """Return dimensions and their shapes."""
            return ZarrReader.list_dimensions(url, group)

        @self.router.get(
            "/zarr_time_values",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's Time values."}},
        )
        def time_values_endpoint(
            url: str = Query(..., description="Dataset URL"),
            group: Optional[str] = Query(None, description="Zarr group to inspect"),
        ) -> List[str]:
            """Return time values."""
            logger.info(f"Fetching time values for URL: {url}, Group: {group}")
            return ZarrReader.list_time_values(url, group)

        @self.router.get(
            "/zarr_trajectory",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's datetime, latitude, longitude and depth."}},
        )
        def trajectory_endpoint(
            url: str = Query(..., description="Dataset URL"),
            group: Optional[str] = Query(None, description="Zarr group to inspect"),
        ) -> dict:
            """Return datetime, latitude, longitude and depth arrays."""
            logger.info(f"Fetching datetime, latitude, longitude and depth values for URL: {url}, Group: {group}")
            return ZarrReader.get_trajectory(url, group)
        
        @self.router.get(
            "/zarr_metrics",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's datetime, latitude, longitude, depth, nitrate, phosphate, pitch, pressure, salinity, silicate, temperature values."}},
        )
        def metrics_endpoint(
            url: str = Query(..., description="Dataset URL"),
            trajectory_group: Optional[str] = Query(None, description="Zarr group to inspect to get trajectory data"),
            reality_group: Optional[str] = Query(None, description="Zarr group to inspect to get metrics data"),
        ) -> dict:
            """Return datetime, latitude, longitude, depth, nitrate, phosphate, pressure, salinity, silicate, temperature arrays."""
            logger.info(f"Fetching datetime, latitude, longitude, depth, nitrate, phosphate, pitch, pressure, salinity, silicate, temperature values for URL: {url}, Group: {reality_group}")
            return ZarrReader.get_metrics(url, trajectory_group, reality_group)
        
        @self.router.get(
            "/zarr_metrics_units",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's salinity and temperature units."}},
        )
        def metrics_units_endpoint(
                url: str = Query(..., description="Dataset URL"), 
                attributes_group: str = Query(..., description="Zarr group to inspect to get metrics from attributes"),
                sensor_name: str = Query(..., description="Sensor name of Autonomous Underwater Vehicle")
        )-> dict:
            """Return salinity and temperature units."""
            logger.info(f"Fetching salinity and temperature units for URL: {url}, Group: {attributes_group}")
            return ZarrReader.get_metrics_units(url, attributes_group, sensor_name)

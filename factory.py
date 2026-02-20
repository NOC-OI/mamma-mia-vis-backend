from fastapi import APIRouter, Query
from typing import List, Optional, Annotated
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
            logger.info(f"Fetching variables for URL: {url} and group: {group}")
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
            logger.info(f"Fetching dimensions and shapes for URL: {url} and group: {group}")
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
            logger.info(f"Fetching time values for URL: {url} and group: {group}")
            return ZarrReader.list_time_values(url, group)

        @self.router.get(
            "/zarr_trajectory",
            response_class=JSONResponse,
            responses={200: {"description": "Return dataset's datetime, latitude, longitude and depth."}},
        )
        def trajectory_endpoint(
            url: str = Query(..., description="Dataset URL"),
            payload_group: Optional[str] = Query(None, description="Zarr group to get AUV's trajectory data"),
            platform_group: Optional[str] = Query(None, description="Zarr group to get AUV's platform data"),
            start_date: Annotated[Optional[str], Query(description="Start date to get AUV's trajectory data")] = None,
            end_date: Annotated[Optional[str], Query(description="End date to get AUV's trajectory data")] = None,
        ) -> dict:
            """Return czml json file."""
            logger.info(f"Fetching czml json file which contains latitude, longitude and depth values of AUV's trajectory: {url} and group: {payload_group}")
            return ZarrReader.get_trajectory(url, payload_group, platform_group, start_date, end_date)
        
        @self.router.get(
            "/zarr_metrics",
            response_class=JSONResponse,
            responses={200: {"description": "Return datetime, latitude, longitude, depth, conductivity/salinity, temperature, pressure and chlorophyll values."}},
        )
        def metrics_endpoint(
            url: Annotated[str, Query(description="Dataset URL")] = ...,
            reality_group: Annotated[Optional[str], Query(description="Zarr group to inspect to get sensor readings")] = None,
            start_date: Annotated[Optional[str], Query(description="Start date to get sensor readings")] = None,
            end_date: Annotated[Optional[str], Query(description="End date to get sensor readings")] = None,
            page_number: Annotated[Optional[int], Query(description="Page number")] = 0,
            page_size: Annotated[Optional[int], Query(description="Page size")] = 10
        ) -> dict:
            """Return datetime, latitude, longitude, depth, conductivity/salinity, temperature, pressure and chlorophyll values."""
            logger.info(f"Fetching datetime, latitude, longitude, depth, conductivity/salinity, temperature, pressure and chlorophyll values for URL: {url} and group: {reality_group}")
            return ZarrReader.get_metrics(url, reality_group, start_date, end_date, page_number, page_size)
        
        @self.router.get(
            "/zarr_metrics_units",
            response_class=JSONResponse,
            responses={200: {"description": "Return conductivity, salinity, temperature, pressure and chlorophyll level units."}},
        )
        def metrics_units_endpoint(
                url: str = Query(..., description="Dataset URL"), 
                attributes_group: str = Query(..., description="Zarr group to inspect to get sensor readings units from attributes"),
                second_sensor: str = Query(..., description="Sensor name of Autonomous Underwater Vehicle which reads conductivity/salinity, temperature and pressure values"),
                third_sensor: str = Query(..., description="Sensor name of Autonomous Underwater Vehicle which reads chlorophyll levels")
        
        )-> dict:
            """Return conductivity, salinity, temperature, pressure and chlorophyll level units."""
            logger.info(f"Fetching conductivity, salinity, temperature, pressure and chlorophyll level units for URL: {url}, group: {attributes_group} and second sensor name: {second_sensor}")
            return ZarrReader.get_metrics_units(url, attributes_group, second_sensor, third_sensor)

        @self.router.get(
            "/zarr_mission_deployments",
            response_class=JSONResponse,
            responses={200: {"description": "Return mission's deployments"}}
        )
        def mission_deployments_endpoint(
            url: str = Query(..., description="Dataset URL")
        )-> dict:
            """Return mission's deployments."""
            logger.info(f"Fetching mission's deployments for URL: {url}")
            return ZarrReader.get_mission_deployments(url)

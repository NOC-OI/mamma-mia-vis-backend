import zarr
import numpy as np
from typing import List, Optional, Any, Tuple
import json
import pandas as pd
import pyproj
from utils.util import *
from utils.czmlFile import *
from models.cartesian2D import *
from models.cartesian3D import *
from models.typeAUV import *
from models.metricUnit import MetricUnit, short_name, formatMetricUnitName


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
    def get_trajectory_dataframe(store_path: str, payload_group: Optional[str] = None, platform_group: Optional[str] = None, platform_model_name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Any:
        """Helper to get and filter trajectory data into a pandas DataFrame."""
        zarr_group_data = zarr.open(store_path, mode="r")
        payload_group_data = zarr_group_data[payload_group] if payload_group else zarr_group_data

        platform_group_metadata = {}
        if platform_group:
            platform_group_metadata = dict(zarr_group_data[platform_group].attrs)

        datetimes = payload_group_data.get("datetimes", payload_group_data.get("time"))[:].tolist() if ("datetimes" in payload_group_data or "time" in payload_group_data) else []
        latitudes = payload_group_data.get("latitude", payload_group_data.get("latitudes", payload_group_data.get("nav_lat", payload_group_data.get("ALATPT01"))))[:].tolist() if ("latitudes" in payload_group_data or "latitude" in payload_group_data or "nav_lat" in payload_group_data or "ALATPT01" in payload_group_data) else []
        longitudes = payload_group_data.get("longitude", payload_group_data.get("longitudes", payload_group_data.get("nav_lon", payload_group_data.get("ALONPT01"))))[:].tolist() if ("longitudes" in payload_group_data or "longitude" in payload_group_data or "nav_lon" in payload_group_data or "ALONPT01" in payload_group_data) else []
        depths = payload_group_data.get("depths", payload_group_data.get("depth", payload_group_data.get("deptht", payload_group_data.get("glider_depth", payload_group_data.get("ADEPPT01")))))[:].tolist() if ("depths" in payload_group_data or "depth" in payload_group_data or "deptht" in payload_group_data or "glider_depth" in payload_group_data or "ADEPPT01" in payload_group_data) else []
        
        platform_type = "unknown"
        short_platform_name = "unknown"
        if platform_group and platform_model_name and platform_model_name in platform_group_metadata:
            platform_type = platform_group_metadata[platform_model_name]
            short_platform_name = name[get_key_by_value(TypeAUV, platform_type)]

        full_global_df = pd.DataFrame({
            "raw_datetime": datetimes,
            "latitude": latitudes,
            "longitude": longitudes,
            "depth": depths
        })

        # 1. Convert Nanoseconds to ISO String format
        full_global_df['datetime'] = pd.to_datetime(full_global_df['raw_datetime'], unit='ns').dt.strftime("%Y-%m-%d %H:%M:%S")

        # 2. Convert the 'datetime' column from nanoseconds to total seconds
        full_global_df['raw_datetime'] = pd.to_datetime(full_global_df['raw_datetime'], unit='ns')        
        
        # 3. Filter by Date Range
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        mask = (full_global_df['raw_datetime'] >= start_dt) & (full_global_df['raw_datetime'] <= end_dt)
        filtered_df = full_global_df.loc[mask].copy()

        return filtered_df, full_global_df, short_platform_name, platform_type

    @staticmethod
    def get_trajectory(store_path: str, payload_group: Optional[str] = None, platform_group: Optional[str] = None, platform_model_name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """Get datetime, latitude, longitude and depth data."""

        filtered_df, full_global_df, short_platform_name, platform_type = ZarrReader.get_trajectory_dataframe(store_path, payload_group, platform_group, platform_model_name, start_date, end_date)

        start_coordinates = []
        output_trajectory = []
        AUV_base64_svg = ""

        if not filtered_df.empty:
            start_time = filtered_df['raw_datetime'].min()
            filtered_df['time_offset'] = (filtered_df['raw_datetime'] - start_time).dt.total_seconds()
            start_coordinates = filtered_df[["longitude", "latitude"]].iloc[0:1].values.flatten().tolist()
            output_trajectory = filtered_df[['time_offset', 'longitude', 'latitude', 'depth']].values.flatten().tolist()
            AUV_svg_path = get_AUV_svg_path(platform_type)
            AUV_base64_svg = get_svg_base64(AUV_svg_path)
            
        deployment_start_date = full_global_df['datetime'].min() if not full_global_df.empty else None
        deployment_end_date = full_global_df['datetime'].max() if not full_global_df.empty else None

        return {
                 "trajectory":  [
                        get_document_data(), 
                        {
                            "id": short_platform_name,
                            "availability": to_interval_format(start_date, end_date),
                            "billboard": get_billboard(start_date, end_date, True, AUV_base64_svg, Origin("CENTER", "BOTTOM"), 0.6, Cartesian3D(0, 0, 0), Cartesian2D(1, -10)),
                            "label": get_label(start_date, end_date, platform_type, Colour(255, 255, 0, 255), Colour(0, 0, 0, 255), Origin("CENTER", "BOTTOM"), Cartesian2D(0, -10)),
                            "path":get_path(start_date, end_date, True),
                            "position":get_position(start_date, output_trajectory)
                        }
                ] if not filtered_df.empty else [],
                "startCoordinates": start_coordinates if not filtered_df.empty else [],
                "deploymentStartDate": deployment_start_date,
                "deploymentEndDate": deployment_end_date,
                "totalRecords": full_global_df.shape[0],
        }

    @staticmethod
    def get_trajectory_csv(store_path: str, payload_group: Optional[str] = None, platform_group: Optional[str] = None, platform_model_name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, target_depth_format: Optional[str] = None) -> str:
        """Get trajectory data in CSV format."""
        filtered_df, _, _, _ = ZarrReader.get_trajectory_dataframe(store_path, payload_group, platform_group, platform_model_name, start_date, end_date)

        if filtered_df.empty:
            return "id,longitude,latitude,depth\n"

        csv_df = filtered_df[['longitude', 'latitude', 'depth']].copy()
        final_csv_df = csv_df
        csv_df.insert(0, 'id', range(1, len(csv_df) + 1))
        if target_depth_format and target_depth_format.lower() == "wgs84 ellipsoid":
            # TODO: Check if there is a way to move grid files from this pyproj.datadir.get_data_dir() path to assets folder and read from there instead of calling from the local file system.
            csv_df['wgs84_depth'] = csv_df.rename(columns={'depth': 'msl_depth'}).apply(convert_depth_to_ellipsoid, axis=1)
            final_csv_df = csv_df[['id', 'longitude', 'latitude', 'wgs84_depth']].rename(columns={'wgs84_depth': 'depth'})    

        return final_csv_df.to_csv(index=False)

 
    @staticmethod
    def get_metrics(store_path: str, payload_group: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """Get datetime, latitude, longitude, depth, nitrate, phosphate, pressure, conductivity/sainity, silicate and temperature data."""

        zarr_groups = zarr.open(store_path, mode="r")
        
        if payload_group:
            payload_zarr_group = zarr_groups[payload_group]

        datetimes = payload_zarr_group.get("TIME", payload_zarr_group.get("datetimes"))[:].tolist() if ("TIME" or "datetimes" in payload_zarr_group) else []
        latitudes = payload_zarr_group.get("LATITUDE", payload_zarr_group.get("LAT", payload_zarr_group.get("ALATPT01")))[:].tolist() if ("LATITUDE" or "LAT" or "ALATPT01" in payload_zarr_group) else []
        longitudes = payload_zarr_group.get("LONGITUDE", payload_zarr_group.get("LON", payload_zarr_group.get("ALONPT01")))[:].tolist() if ("LONGITUDE" or "LON" or "ALONPT01" in payload_zarr_group) else []
        depths = payload_zarr_group.get("DEPTH", payload_zarr_group.get("GLIDER_DEPTH", payload_zarr_group.get("ADEPPT01")))[:].tolist() if ("DEPTH" or "GLIDER_DEPTH" or "ADEPPT01" in payload_zarr_group) else []
        pressure_values = payload_zarr_group.get("pressure", payload_zarr_group.get("PRES", payload_zarr_group.get("PRESSURE")))[:].tolist() if ("pressure" or "PRES" or "PRESSURE" in payload_zarr_group) else []
        conductivity_values = payload_zarr_group.get("CNDC")[:].tolist() if ("CNDC" in payload_zarr_group) else []
        salinity_values = payload_zarr_group.get("salinity", payload_zarr_group.get("PRACTICAL_SALINITY"))[:].tolist() if ("salinity" or "PRACTICAL_SALINITY" in payload_zarr_group) else []
        temperature_values = payload_zarr_group.get("temperature", payload_zarr_group.get("TEMP", payload_zarr_group.get("INSITU_TEMPERATURE", payload_zarr_group.get("POTENTIAL_TEMPERATURE"))))[:].tolist() if ("temperature" or "TEMP" or "INSITU_TEMPERATURE" or "POTENTIAL_TEMPERATURE" in payload_zarr_group) else []
        chlorophyll_values = payload_zarr_group.get("CHLOROPHYLL")[:].tolist() if ("CHLOROPHYLL" in payload_zarr_group) else []

        full_global_df = pd.DataFrame({
            "raw_datetime": datetimes,
            "latitude": latitudes,
            "longitude": longitudes,
            "depth": depths,
            "pressure": pressure_values,
            "conductivity": conductivity_values if len(conductivity_values) > 0 else None,
            "salinity": salinity_values if len(salinity_values) > 0 else None,
            "temperature": temperature_values,
            "chlorophyll": chlorophyll_values if len(chlorophyll_values) > 0 else None
        })


        # 1. Convert Nanoseconds to ISO String format
        full_global_df['datetime'] = pd.to_datetime(full_global_df['raw_datetime'], unit='ns').dt.strftime("%Y-%m-%d %H:%M:%S")
        global_df = full_global_df.drop(["raw_datetime"], axis=1)

        start_date_iso = to_iso_format(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_iso = to_iso_format(end_date, "%Y-%m-%d %H:%M:%S")

        # 2. Filter by Date Range
        mask = (global_df['datetime'] >= start_date_iso) & (global_df['datetime'] <= end_date_iso)
        filtered_df = global_df.loc[mask]
        
        # 3. Convert to JSON format
        json_output = filtered_df.to_json(orient='records', date_format='iso')
        sensor_readings = json.loads(json_output)
                
        return {
            "metrics": sensor_readings,
            "totalRecords": global_df.shape[0]
        }
    
    @staticmethod
    def get_metrics_units(store_path: str, attributes_group: str, second_sensor: str, third_sensor: str)-> dict:
        """Get conductivity, salinity, temperature, pressure and chlorophyll units."""
        zarr_groups = zarr.open(store_path, mode="r")
        attrs_dict = dict(zarr_groups[attributes_group].attrs)

        sensor_reading_names = ["CNDC", "PRACTICAL_SALINITY", "TEMP", "INSITU_TEMPERATURE", "POTENTIAL_TEMPERATURE", "PRES", "PRESSURE", "CHLOROPHYLL"]
        sensor_reading_json = "{"
        sensor_readings_groups = []
        
        for parameter in sensor_reading_names:
            if parameter == "CHLOROPHYLL" and third_sensor:
                parameter_name_group = "parameter_id"
                second_sensor_group = third_sensor
            else:
                parameter_name_group = "alternate_labels"
                second_sensor_group = second_sensor
        
            if "parameters" in attrs_dict["sensors"][second_sensor_group] and parameter in attrs_dict["sensors"][second_sensor_group]["parameters"]:
                sensor_readings_groups = ["parameters"]
            elif "specification" in attrs_dict["sensors"][second_sensor_group] and parameter in attrs_dict["sensors"][second_sensor_group]["specification"]:
                sensor_readings_groups = ["specification", "meta_data"]

            if len(sensor_readings_groups) > 0:    
                if len(sensor_readings_groups) > 1:
                    parameter_name = attrs_dict["sensors"][second_sensor_group][sensor_readings_groups[0]][parameter][sensor_readings_groups[1]][parameter_name_group]
                    var_unit = attrs_dict["sensors"][second_sensor_group][sensor_readings_groups[0]][parameter][sensor_readings_groups[1]]["unit_of_measure"]    
                else:
                    parameter_name = attrs_dict["sensors"][second_sensor_group][sensor_readings_groups[0]][parameter]["alternate_labels"]
                    var_unit = attrs_dict["sensors"][second_sensor_group][sensor_readings_groups[0]][parameter]["unit_of_measure"] 
                sensor_readings_groups = []   
                sensor_reading_name = parameter_name if isinstance(parameter_name, str) else parameter_name[0]
                sensor_reading_json = sensor_reading_json + "\"" + sensor_reading_name + "\":\"" + var_unit + "\","     
        
        sensor_reading_json = json.loads(sensor_reading_json[:-1] + "}")
        json_str = "{"
        for metric, metric_unit in sensor_reading_json.items():
            json_str = json_str + "\"" + formatMetricUnitName(metric)  +  "\":\"" + short_name[get_key_by_value(MetricUnit, metric_unit)] + "\","
        json_str = json_str[:-1] + "}"
        
        return json.loads(json_str)

    @staticmethod
    def get_mission_deployments(store_path: str):
        """Get mission's deployments."""
        zarr_groups = zarr.open(store_path, mode="r")
        deployments_list = list(zarr_groups)
        return {"deployments": deployments_list}

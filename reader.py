import zarr
import numpy as np
from typing import List, Optional
import datetime
import json
import pandas as pd
from metricUnit import MetricUnit, short_name, get_key_by_value, formatMetricUnitName
from util import to_iso_format


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
    def get_trajectory(store_path: str, payload_group: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, page_number: Optional[int] = 0, page_size: Optional[int] = 10) -> dict:
        """Get datetime, latitude, longitude and depth data."""
        zarr_group = zarr.open(store_path, mode="r")
        if payload_group:
            zarr_group = zarr_group[payload_group]

        datetimes = zarr_group.get("datetimes", zarr_group.get("time"))[:].tolist() if ("datetimes" in zarr_group or "time" in zarr_group) else []
        latitudes = zarr_group.get("latitude", zarr_group.get("latitudes", zarr_group.get("nav_lat")))[:].tolist() if ("latitudes" in zarr_group or "latitude" in zarr_group or "nav_lat" in zarr_group) else []
        longitudes = zarr_group.get("longitude", zarr_group.get("longitudes", zarr_group.get("nav_lon")))[:].tolist() if ("longitudes" in zarr_group or "longitude" in zarr_group or "nav_lon" in zarr_group) else []
        depths = zarr_group.get("depths", zarr_group.get("depth", zarr_group.get("deptht", zarr_group.get("glider_depth"))))[:].tolist() if ("depths" in zarr_group or "depth" in zarr_group or "deptht" in zarr_group or "glider_depth" in zarr_group) else []

        full_global_df = pd.DataFrame({
            "raw_datetime": datetimes,
            "latitude": latitudes,
            "longitude": longitudes,
            "depth": depths
        })

        
        # 1. Convert Nanoseconds to ISO String format
        full_global_df['datetime'] = pd.to_datetime(full_global_df['raw_datetime'], unit='ns').dt.strftime("%Y-%m-%d %H:%M:%S")
        global_df = full_global_df.drop(["raw_datetime"], axis=1)

        start_date_iso = to_iso_format(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_iso = to_iso_format(end_date, "%Y-%m-%d %H:%M:%S")

        # 2. Filter by Date Range
        # Convert boundary strings to datetime objects for comparison
        mask = (global_df['datetime'] >= start_date_iso) & (global_df['datetime'] <= end_date_iso)
        filtered_df = global_df.loc[mask]
        
        # 3. Handle Pagination
        # Calculate start and end indices
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        
        # Slice the dataframe for the specific page
        paginated_df = filtered_df.iloc[start_idx:end_idx]
        
        # 4. Convert to JSON format
        json_output = paginated_df.to_json(orient='records', date_format='iso')
        auv_trajectory = json.loads(json_output)

        return {
            "trajectory": auv_trajectory,
            "totalRecords": global_df.size,
            "pageNumber": page_number,
            "pageSize": page_size
        }

    @staticmethod
    def get_metrics(store_path: str, payload_group: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, page_number: Optional[int] = 0, page_size: Optional[int] = 10) -> dict:
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
        # Convert boundary strings to datetime objects for comparison
        mask = (global_df['datetime'] >= start_date_iso) & (global_df['datetime'] <= end_date_iso)
        filtered_df = global_df.loc[mask]
        
        # 3. Handle Pagination
        # Calculate start and end indices
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        
        # Slice the dataframe for the specific page
        paginated_df = filtered_df.iloc[start_idx:end_idx]
        
        # 4. Convert to JSON format
        json_output = paginated_df.to_json(orient='records', date_format='iso')
        sensor_readings = json.loads(json_output)
                
        return {
            "metrics": sensor_readings,
            "totalRecords": global_df.size,
            "currentPage": page_number,
            "recordsPerPage": page_size
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

import zarr
import numpy as np
from typing import List, Optional
import datetime
import json
from metricUnit import MetricUnit, short_name, get_key_by_value


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
        """Get datetime, latitude, longitude and depth data."""
        zarr_group = zarr.open(store_path, mode="r")
        if group:
            zarr_group = zarr_group[group]

        datetimes = zarr_group.get("datetimes", zarr_group.get("time"))[:].tolist() if ("datetimes" in zarr_group or "time" in zarr_group) else []
        latitudes = zarr_group.get("latitude", zarr_group.get("latitudes", zarr_group.get("nav_lat")))[:].tolist() if ("latitudes" in zarr_group or "latitude" in zarr_group or "nav_lat" in zarr_group) else []
        longitudes = zarr_group.get("longitude", zarr_group.get("longitudes", zarr_group.get("nav_lon")))[:].tolist() if ("longitudes" in zarr_group or "longitude" in zarr_group or "nav_lon" in zarr_group) else []
        depths = zarr_group.get("depths", zarr_group.get("depth", zarr_group.get("deptht")))[:].tolist() if ("depths" in zarr_group or "depth" in zarr_group or "deptht" in zarr_group) else []

        trajectory = []
        for i in range(min(len(datetimes), len(latitudes), len(longitudes), len(depths))):
                datetime_str = ""
                dt_value = datetimes[i]  # Store the original datetime value

                if isinstance(dt_value, np.datetime64):
                    try:
                        dt_object = dt_value.astype('datetime64[s]').astype(datetime.datetime)
                        datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    except OverflowError:  # Handle datetime64 out of range
                        print(f"OverflowError at index {i}: datetime64 value {dt_value} is out of range.")
                        datetime_str = "Invalid Date"  # Or handle differently
                elif isinstance(dt_value, (int, np.int64)):
                    try:
                        dt_object = datetime.datetime.fromtimestamp(dt_value / 1000000000)
                        datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    except (ValueError, OSError) as e:  # Handle integer timestamp out of range
                        print(f"Timestamp error at index {i}: Integer timestamp {dt_value} is out of range: {e}")
                        datetime_str = "Invalid Date"  # Or handle differently
                elif isinstance(dt_value, datetime.date):
                    dt_object = dt_value
                    datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                elif isinstance(dt_value, str):
                    datetime_str = dt_value
                else:  # Handle other data types or missing data as needed
                    print(f"Unexpected datetime type at index {i}: {type(dt_value)}")
                    datetime_str = "Invalid Date"
                
                trajectory.append({
                    "datetime": datetime_str,
                    "latitude": latitudes[i],
                    "longitude": longitudes[i],
                    "depth": depths[i]
                })

        return {"trajectory": trajectory}

    @staticmethod
    def get_metrics(store_path: str, trajectory_group: Optional[str] = None, payload_group: Optional[str] = None, page: Optional[int] = 0, records_per_page: Optional[int] = 10) -> dict:
        """Get datetime, latitude, longitude, depth, nitrate, phosphate, pressure, conductivity/sainity, silicate and temperature data."""

        zarr_groups = zarr.open(store_path, mode="r")
        if trajectory_group:
            traj_zarr_group = zarr_groups[trajectory_group]
        
        if payload_group:
            payload_zarr_group = zarr_groups[payload_group]

        datetimes = payload_zarr_group.get("TIME", payload_zarr_group.get("datetimes"))[:].tolist() if ("TIME" or "datetimes" in payload_zarr_group) else []
        latitudes = payload_zarr_group.get("LATITUDE", payload_zarr_group.get("LAT", payload_zarr_group.get("ALATPT01")))[:].tolist() if ("LATITUDE" or "LAT" or "ALATPT01" in payload_zarr_group) else []
        longitudes = payload_zarr_group.get("LONGITUDE", payload_zarr_group.get("LON", payload_zarr_group.get("ALONPT01")))[:].tolist() if ("LONGITUDE" or "LON" or "ALONPT01" in payload_zarr_group) else []
        depths = payload_zarr_group.get("DEPTH", payload_zarr_group.get("GLIDER_DEPTH", payload_zarr_group.get("ADEPPT01")))[:].tolist() if ("DEPTH" or "GLIDER_DEPTH" or "ADEPPT01" in payload_zarr_group) else []
        pressure_values = payload_zarr_group.get("pressure", payload_zarr_group.get("PRES", payload_zarr_group.get("PRESSURE")))[:].tolist() if ("pressure" or "PRES" or "PRESSURE" in payload_zarr_group) else []
        conductivity_values = payload_zarr_group.get("salinity", payload_zarr_group.get("CNDC", payload_zarr_group.get("PRACTICAL_SALINITY")))[:].tolist() if ("salinity" or "CNDC" or "PRACTICAL_SALINITY" in payload_zarr_group) else []
        temperature_values = payload_zarr_group.get("temperature", payload_zarr_group.get("TEMP", payload_zarr_group.get("INSITU_TEMPERATURE", payload_zarr_group.get("POTENTIAL_TEMPERATURE"))))[:].tolist() if ("temperature" or "TEMP" or "INSITU_TEMPERATURE" or "POTENTIAL_TEMPERATURE" in payload_zarr_group) else []
        chlorophyll_values = payload_zarr_group.get("CHLOROPHYLL")[:].tolist() if ("CHLOROPHYLL" in payload_zarr_group) else []

                
        sensor_readings = []
        min_size = min(len(datetimes), len(latitudes), len(longitudes), len(depths), len(conductivity_values), len(temperature_values))
        current_page = page if min_size > 0 else 0
        cur_records_page = records_per_page if records_per_page > 0 else 10
        start_index = (current_page - 1) * cur_records_page if current_page > 0 else 0
        end_index = current_page * cur_records_page if current_page > 0 and cur_records_page > 0 else 0
        for start_index in range(start_index, end_index):
            datetime_str = ""
            dt_value = datetimes[start_index]  # Store the original datetime value

            if isinstance(dt_value, np.datetime64):
                try:
                    dt_object = dt_value.astype('datetime64[s]').astype(datetime.datetime)
                    datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                except OverflowError:  # Handle datetime64 out of range
                    print(f"OverflowError at index {start_index}: datetime64 value {dt_value} is out of range.")
                    datetime_str = "Invalid Date"
            elif isinstance(dt_value, (int, np.int64)):
                try:
                    dt_object = datetime.datetime.fromtimestamp(dt_value / 1000000000)
                    datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                except (ValueError, OSError) as e:  # Handle integer timestamp out of range
                    print(f"Timestamp error at index {start_index}: Integer timestamp {dt_value} is out of range: {e}")
                    datetime_str = "Invalid Date" 
            elif isinstance(dt_value, datetime.date):
                dt_object = dt_value
                datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
            elif isinstance(dt_value, str):
                datetime_str = dt_value
            elif isinstance(dt_value, float):
                # Convert nanoseconds to seconds
                # The timestamp is in nanoseconds, so divide by 1e9 (10^9) to get seconds.
                # print(' NANOSEC TIMESTAMP: ', dt_value)
                seconds_timestamp = dt_value / 1e9
                # Convert the Unix timestamp (in seconds) to a datetime object
                dt_object = datetime.datetime.fromtimestamp(seconds_timestamp)
                # Format the datetime object to "dd/mm/yyyy HH:mm:ss"
                datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                print(f"Unexpected datetime type at index {start_index}: {(dt_value)}")
                datetime_str = "Invalid Date"

            sensor_readings.append({
                "datetime": datetime_str,
                "latitude": latitudes[start_index],
                "longitude": longitudes[start_index],
                "depth": depths[start_index],
                "pressure": pressure_values[start_index],
                "conductivity": conductivity_values[start_index],
                "temperature": temperature_values[start_index],
                "pressure": pressure_values[start_index],
                "chlorophyll": chlorophyll_values[start_index],
            })
        
        return {
            "metrics": sensor_readings,
            "totalRecords": min_size,
            "currentPage": current_page,
            "recordsPerPage": records_per_page
        }
    
    @staticmethod
    def get_metrics_units(store_path: str, attributes_group: str, sensor_name: str)-> dict:
        """Get conductivity, temperature and pressure units."""
        zarr_groups = zarr.open(store_path, mode="r")
        attrs_dict = dict(zarr_groups[attributes_group].attrs)

        sensor_reading_names = ["CNDC", "TEMP", "PRES"]
        sensor_reading_json = "{"
        for parameter in sensor_reading_names:
            parameter_name = attrs_dict["sensors"][sensor_name]["parameters"][parameter]["alternate_labels"]
            sensor_reading_json = sensor_reading_json + "\"" + parameter + "\":\"" + parameter_name[0] + "\","     
        sensor_reading_json = json.loads(sensor_reading_json[:-1] + "}")

        json_str = "{"
        for variable_name in sensor_reading_json.keys():
            var_unit = attrs_dict["sensors"][sensor_name]["parameters"][variable_name]["unit_of_measure"]
            json_str = json_str + "\"" + sensor_reading_json.get(variable_name).lower() + "\":\"" + var_unit + "\","
        json_str = json_str[:-1] + "}"
        metrics_units_json = json.loads(json_str)

        json_str = "{"
        for metric, metric_unit in metrics_units_json.items():
            json_str = json_str + "\"" + metric  +  "\":\"" + short_name[get_key_by_value(MetricUnit, metric_unit)] + "\","
        json_str = json_str[:-1] + "}"
        
        return json.loads(json_str)

    @staticmethod
    def get_mission_deployments(store_path: str):
        """Get mission's deployments."""
        zarr_groups = zarr.open(store_path, mode="r")
        deployments_list = list(zarr_groups)
        return {"deployments": deployments_list}

import zarr
import numpy as np
from typing import List, Optional
import datetime


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
    def get_metrics(store_path: str, trajectory_group: Optional[str] = None, reality_group: Optional[str] = None) -> dict:
        """Get datetime, latitude, longitude, depth, nitrate, phosphate, pressure, salinity, silicate and temperature data."""

        zarr_groups = zarr.open(store_path, mode="r")
        if trajectory_group:
            traj_zarr_group = zarr_groups[trajectory_group]
        
        if reality_group:
            reality_zarr_group = zarr_groups[reality_group]

        datetimes = traj_zarr_group.get("datetimes", traj_zarr_group.get("time"))[:].tolist() if ("datetimes" or "time" in traj_zarr_group) else []
        latitudes = traj_zarr_group.get("latitude", traj_zarr_group.get("latitudes", traj_zarr_group.get("nav_lat")))[:].tolist() if ("latitudes" or "latitude" or "nav_lat" in traj_zarr_group) else []
        longitudes = traj_zarr_group.get("longitude", traj_zarr_group.get("longitudes", traj_zarr_group.get("nav_lon")))[:].tolist() if ("longitudes" or "longitude" or "nav_lon" in traj_zarr_group) else []
        depths = traj_zarr_group.get("depths", traj_zarr_group.get("depth", traj_zarr_group.get("deptht")))[:].tolist() if ("depths" or "depth" or "deptht" in traj_zarr_group) else []

        nitrate_values = reality_zarr_group.get("nitrate")[:].tolist() if ("nitrate" in reality_zarr_group) else []
        phosphate_values = reality_zarr_group.get("phosphate")[:].tolist() if ("phosphate" in reality_zarr_group) else []
        pressure_values = reality_zarr_group.get("pressure")[:].tolist() if ("pressure" in reality_zarr_group) else []
        salinity_values = reality_zarr_group.get("salinity", reality_zarr_group.get("CNDC"))[:].tolist() if ("salinity" or "CNDC" in reality_zarr_group) else []
        silicate_values = reality_zarr_group.get("silicate")[:].tolist() if ("silicate" in reality_zarr_group) else []
        temperature_values = reality_zarr_group.get("temperature", reality_zarr_group.get("TEMP"))[:].tolist() if ("temperature" or "TEMP" in reality_zarr_group) else []
        number_readings = len(datetimes)
        
        salinity_values =  np.array(salinity_values).reshape((number_readings)) if number_readings > len(salinity_values) else salinity_values
        temperature_values = np.array(temperature_values).reshape((number_readings)) if number_readings > len(temperature_values) else temperature_values
        
        metrics = []
        min_size = min(len(datetimes), len(latitudes), len(longitudes), len(depths), len(salinity_values), len(temperature_values))
        for i in range(min_size):
            datetime_str = ""
            dt_value = datetimes[i]  # Store the original datetime value

            if isinstance(dt_value, np.datetime64):
                try:
                    dt_object = dt_value.astype('datetime64[s]').astype(datetime.datetime)
                    datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                except OverflowError:  # Handle datetime64 out of range
                    print(f"OverflowError at index {i}: datetime64 value {dt_value} is out of range.")
                    datetime_str = "Invalid Date"
            elif isinstance(dt_value, (int, np.int64)):
                try:
                    dt_object = datetime.datetime.fromtimestamp(dt_value / 1000000000)
                    datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                except (ValueError, OSError) as e:  # Handle integer timestamp out of range
                    print(f"Timestamp error at index {i}: Integer timestamp {dt_value} is out of range: {e}")
                    datetime_str = "Invalid Date" 
            elif isinstance(dt_value, datetime.date):
                dt_object = dt_value
                datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
            elif isinstance(dt_value, str):
                datetime_str = dt_value
            else:
                print(f"Unexpected datetime type at index {i}: {type(dt_value)}")
                datetime_str = "Invalid Date"

            metrics.append({
                "datetime": datetime_str,
                "latitude": latitudes[i],
                "longitude": longitudes[i],
                "depth": depths[i],
                # "nitrate": nitrate_values[i],
                # "phosphate": phosphate_values[i],
                # "pressure": pressure_values[i],
                "salinity": salinity_values[i],
                # "silicate": silicate_values[i],
                "temperature": temperature_values[i]
            })
        
        return {"metrics": metrics}

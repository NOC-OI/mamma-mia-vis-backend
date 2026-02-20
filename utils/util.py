from datetime import datetime
from typing import Type, Any, Optional
from enum import Enum
import base64

def to_iso_format(date_str, input_format="%Y-%m-%d", output_format="%Y-%m-%d %H:%M:%S.%f"):
    """
    Converts a date string into a specific ISO 8601-like format.
    
    :param date_str: The string representation of the date.
    :param input_format: The format of the date_str (default is YYYY-MM-DD).
    :return: String formatted as "YYYY-MM-DD HH:MM:SS.ffffff"
    """
    try:
        # 1. Parse string into a datetime object
        dt_obj = datetime.strptime(date_str, input_format)
        
        # 2. Return as ISO format string with microseconds
        return dt_obj.strftime(output_format)
        
    except ValueError as e:
        return f"Error: Invalid date or format. {e}"



def to_interval_format(start_date: str, end_date: str, input_format="%Y-%m-%d %H:%M:%S"):
    # "availability":"2012-08-04T16:00:00Z/2012-08-04T17:04:54.9962195740191Z",
    try:
        # 1. Parse string dates into a datetime objects
        formatted_start_date = datetime.strptime(start_date, input_format)

        formatted_end_date = datetime.strptime(end_date, input_format)
        
        # 2. Return as ISO format interval including time zone
        
        return formatted_start_date.strftime("%Y-%m-%dT%H:%M:%SZ") + '/' + formatted_end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    
    except ValueError as e:
        return f"Error: Invalid date or format. {e}"
    


def get_key_by_value(enum_class: Type[Enum], value: Any) -> Optional[Enum]:
    """
    Retrieves the name (key) of an enum member based on its associated value.

    Args:
        enum_class: The Enum class (e.g., StatusCode) to search within.
        value: The value (e.g., Degrees Celsius, Siemens per metre, Decibars) to look up.

    Returns:
        The enum member (e.g., SIEMENS_PER_METER, DEGREES_CELSIUS) 
        or None if no matching value is found.
    """
    # Iterate through all members of the Enum class
    for member in enum_class:
        if member.value == value:
            # Return the name (key) of the matching member
            return member
            
    # Return None if the loop completes without a match
    return None

def get_svg_base64(file_path):
    """
    Reads an SVG file and returns a Base64 encoded string 
    formatted for use in CZML/HTML.
    """
    try:
        with open(file_path, "rb") as svg_file:
            # Read the binary data
            binary_data = svg_file.read()
            # Encode to base64
            base64_encoded = base64.b64encode(binary_data).decode('utf-8')
            # Add the header for CZML/Data URI
            return f"data:image/svg+xml;base64,{base64_encoded}"
    except FileNotFoundError:
        return "Error: File not found."
from datetime import datetime

def to_iso_format(date_str, input_format="%Y-%m-%d"):
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
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
        
    except ValueError as e:
        return f"Error: Invalid date or format. {e}"

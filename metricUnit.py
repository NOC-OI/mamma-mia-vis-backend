from enum import Enum
from typing import Type, Any, Optional

class MetricUnit(Enum):
    KG_PER_CUBIC_METER = "Kilograms per cubic metre"
    SIEMENS_PER_METER = "Siemens per metre"
    DEGREES_CELSIUS = "Degrees Celsius"
    DECIBARS = "Decibars"
    DIMENSIONLESS = "Dimensionless"

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

def formatMetricUnitName(name: str):
    formatted_name = name.replace(" ", "_").lower()
    wordToLook = "temperature"
    if wordToLook in name:
        foundIndex = name.index(wordToLook)
        formatted_name = name[foundIndex:]

    return formatted_name

long_name = {
    MetricUnit.KG_PER_CUBIC_METER: "Kilograms per cubic metre",
    MetricUnit.SIEMENS_PER_METER : "Siemens per metre",
    MetricUnit.DEGREES_CELSIUS : "Degrees Celsius",
    MetricUnit.DECIBARS: "Decibars",
    MetricUnit.DIMENSIONLESS: ""
}

short_name = {
    MetricUnit.KG_PER_CUBIC_METER: "kg/m3",
    MetricUnit.SIEMENS_PER_METER : "S/m",
    MetricUnit.DEGREES_CELSIUS : "°C",
    MetricUnit.DECIBARS: "dbar",
    MetricUnit.DIMENSIONLESS: ""
}




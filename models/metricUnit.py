from enum import Enum

class MetricUnit(Enum):
    KG_PER_CUBIC_METER = "Kilograms per cubic metre"
    SIEMENS_PER_METER = "Siemens per metre"
    DEGREES_CELSIUS = "Degrees Celsius"
    DECIBARS = "Decibars"
    DIMENSIONLESS = "Dimensionless"

def formatMetricUnitName(name: str):
    formatted_name = name.replace(" ", "_").lower()
    wordsToLook = ["temperature", "salinity"]
    for unit_name in wordsToLook:        
        if unit_name in name:
            foundIndex = name.index(unit_name)
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




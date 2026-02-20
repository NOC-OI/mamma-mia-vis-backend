
from models.colour import *
from models.typeAUV import *
from utils.util import *
from models.cartesian2D import *
from models.origin import *

def get_document_data():
    return {
            "id":"document",
            "version":"1.0"
    }

def get_fill_colour_at_interval(interval: str, inputColour: Colour):
    return [
        {
            "interval": interval,
            "rgba": inputColour.get_rgba()
        }
    ]

def get_billboard(start_date: str, end_date: str, is_shown: bool, AUV_image: str, horizontal_origin = "CENTER", scale = 0.8333333333333334, show = True, vertical_origin = "BOTTOM"):
    return {
        "eye_offset": {
            "cartesian":[
            0.0,0.0,0.0
            ]
        },
        "horizontal_origin": horizontal_origin,
        "image": AUV_image,
        "pixel_offset": {
            "cartesian2":[
            0.0,0.0
            ]
        },
        "scale":scale,
        "show": show_at_interval(to_interval_format(start_date, end_date), is_shown),
        "vertical_origin": vertical_origin
    }

def get_label(start_date: str, end_date: str, platform_type: str, fill_colour: Colour, outline_colour: Colour, pixel_offset: Cartesian2D, origin: Origin):
    return {
            "fillColor":get_fill_colour_at_interval(to_interval_format(start_date, end_date), fill_colour),
            "font":"bold 10pt Segoe UI Semibold",
            "horizontalOrigin": origin.horizontal,
            "outlineColor":{
                "rgba": outline_colour.get_rgba()
            },
            "pixelOffset":{
                "cartesian2": pixel_offset.get2DCoordinates()
            },
            "scale":1.0,
            "show":show_at_interval(to_interval_format(start_date, end_date), True),
            "style":"FILL",
            "text":platform_type,
            "verticalOrigin": origin.vertical
    }

def get_material(start_date: str, end_date: str):
    return {
        "solidColor":{
            "color":{
                "interval": to_interval_format(start_date, end_date),
                "rgba": Colour(222, 237, 237, 255).get_rgba()
            }
        }
    }

def get_path(start_date: str, end_date: str, is_shown: bool):
    return {
        "material": get_material(start_date, end_date),
        "width": vehicle_width(to_interval_format(start_date, end_date), 5.0),
        "show": show_at_interval(to_interval_format(start_date, end_date), is_shown) 
    }

def get_position(start_date: str, output_trajectory: list):
    return {
        "interpolationAlgorithm":"LAGRANGE",
        "interpolationDegree":1,
        "epoch": to_iso_format(start_date, "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"),
        "cartographicDegrees":output_trajectory
    }

def show_at_interval(interval: str, is_shown: bool):
    return [
        {
        "interval": interval,
        "boolean": is_shown
        }
    ]

def vehicle_width(interval: str, width: int):
    return [
        {
        "interval":interval,
        "number":width
        }
    ]

def get_AUV_svg_path(typeAUV: str):
     print( 'AUV TYPE: ', typeAUV, ' OTHER: ', TypeAUV.ALR.value)
     return "./assets/icons/auv_boaty_mc_boatface.svg" if typeAUV == TypeAUV.ALR.value else "./assets/icons/glider.svg"

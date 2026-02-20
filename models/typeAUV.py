from enum import Enum


class TypeAUV(Enum):
    GLIDER = "glider"
    SLOCUM_GLIDER = "Slocum_G2"
    ALR = "ALR_1500"

name = {
    TypeAUV.ALR: "ALR",
    TypeAUV.SLOCUM_GLIDER : "glider",
    TypeAUV.GLIDER : "glider"
}
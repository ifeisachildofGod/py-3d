from dataclasses import dataclass
from enum import Enum

Number = int | float

WIDTH = 500
HEIGHT = 500
POINT_SIZE = 4

class DisplayFlags(Enum):
    VERTEX   =  0b0001
    VERTEX_I =  0b0010
    WIRE     =  0b0100
    FACE     =  0b1000

@dataclass
class ModelData:
    v: list[tuple[Number, Number, Number]]
    f: list[tuple[int, int, int]]

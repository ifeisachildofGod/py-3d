from dataclasses import dataclass
import math


class AreaError(Exception):
    pass

@dataclass
class Area:
    def _parallel_angle(a: float, b: float, c: float, dp: int | None):
        if 0 in (a, b):
            return None
        
        v = round((a*a + b*b - c*c) / (2*a*b), dp) if dp is not None else (a*a + b*b - c*c) / (2*a*b)
        
        return math.acos(v)

    def area_of_triangle(a: float, b: float, c: float, dp: int = 10):
        theta_1 = Area._parallel_angle(a, b, c, dp)
        theta_2 = Area._parallel_angle(c, b, a, dp)
        
        if None in (theta_1, theta_2):
            return 0
        
        area_1 = a*a * math.cos(theta_1) * math.sin(theta_1)
        area_2 = c*c * math.cos(theta_2) * math.sin(theta_2)
        
        return math.fabs(area_1 + area_2) / 2

    def area_of_quadrillateral(a: float, b: float, c: float, d: float, dp: int = 10):
        lengths = a, b, c, d
        
        l3, l4 = min(lengths), max(lengths)
        l3_i, l4_i = lengths.index(l3), lengths.index(l4)
        
        l1, l2 = [lengths[i] for i in range(len(lengths)) if i not in (l3_i, l4_i)]
        l1_i, l2_i = lengths.index(l1), lengths.index(l2)
        
        if (l1_i + l2_i) % 2 == 0:
            l1, l2, l3, l4 = a, b, c, d
        
        diag = (l1*l1 + l2*l2)**0.5
        
        return round(Area.area_of_triangle(l1, l2, diag, None) + Area.area_of_triangle(l3, l4, diag, None), dp)

    def area_of_polygon(*args):
        match len(args):
            case 0:
                raise ValueError("Arguments are not optional")
            case 1:
                raise AreaError("Cannot determine area of a single point")
            case 2:
                raise AreaError("Cannot determine area of a line")
            case 3:
                return Area.area_of_triangle(*args)
            case 4:
                return Area.area_of_quadrillateral(*args)
        
        a, b = args[:2]
        
        area =  0.5 * a * b
        area += Area.area_of_polygon(*((a*a + b*b)**0.5, *args[2:]))
        
        return area



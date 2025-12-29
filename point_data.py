from dataclasses import dataclass
import math
import pygame
from constants import Number

class Vector:
    def __init__(self, x: Number, y: Number):
        self.x = x
        self.y = y
    
    def project(self):
        pass
    
    def coordinates(self):
        pass
    
    def dot(self, vec: "Vector"):
        pass


class Vec2(Vector):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.at_infinity = False
    
    # --- Iterator Overloading ---
    def __getitem__(self, index: int):
        return self.coordinates()[index]
    def __setitem__(self, index: int, value: Number):
        [self.x, self.y][index]
        
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
    def __len__(self):
        return 2
    def __iter__(self):
        return iter((self.x, self.y))
    
    # --- Arithmetic Overloading ---
    def __add__(self, other):
        if not self.at_infinity:
            if isinstance(other, Vec2):
                return Vec2(self.x + other.x, self.y + other.y)
            elif isinstance(other, tuple | list):
                if len(other) != 2:
                    raise ValueError("Tuple must have 2 elements")
                return Vec2(self.x + other[0], self.y + other[1])
            elif isinstance(other, (int, float)):
                return Vec2(self.x + other, self.y + other)
            
            raise NotImplementedError(f"Cannot not add Vec2 to '{other.__class__.__name__}'")
    def __radd__(self, other):
        return self.__add__(other)
     
    def __sub__(self, other):
        if not self.at_infinity:
            if isinstance(other, (Vec2, int, float)):
                return self.__add__(other * -1)
            elif isinstance(other, tuple | list):
                if len(other) != 2:
                    raise ValueError("Tuple must have 2 elements")
                return Vec2(self.x - other[0], self.y - other[1])
            
            raise NotImplementedError(f"Cannot not subtract '{other.__class__.__name__}' from Vec2")
    
    def __mul__(self, other):
        if not self.at_infinity:
            if isinstance(other, (int, float)):
                return Vec2(self.x * other, self.y * other)
            
            raise NotImplementedError(f"Cannot not multiply Vec2 with '{other.__class__.__name__}'")
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        return f"Vec2({self.x if self.x is not None else "Inf"}, {self.y if self.y is not None else "Inf"})"

    def project(self, screen: pygame.Surface):
        if self.at_infinity:
            return self
        return Vec2((self.x + 1) * screen.get_width() / 2, (1 - self.y) * screen.get_height() / 2)
    
    def coordinates(self):
        return self.x, self.y

    def dot(self, vec: "Vec2"):
        return self.x * vec.x + self.y * vec.y

class Vec3(Vector):
    def __init__(self, x: Number, y: Number, z: Number):
        self._x = x
        self._y = y
        self._z = z
        
        super().__init__(self._x, self._y)
        
        self.z = self._z
    
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value: Number):
        self._x = value
    
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value: Number):
        self._y = value
    
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self, value: Number):
        self._z = value
    
    # --- Iterator Overloading ---
    def __getitem__(self, index: int):
        return self.coordinates()[index]
    def __setitem__(self, index: int, value: Number):
        [self.x, self.y, self.z][index]
        
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
    def __len__(self):
        return 3
    def __iter__(self):
        return iter((self.x, self.y, self.z))
    
    # --- Arithmetic Overloading ---
    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec3(self.x + other.x, self.y + other.y, self.z)
        elif isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, tuple | list):
            if len(other) != 3:
                raise ValueError("Tuple must have 3 elements")
            return self.__class__(self.x + other[0], self.y + other[1], self.z + other[2])
        elif isinstance(other, (int, float)):
            return self.__class__(self.x + other, self.y + other, self.z + other)
        
        raise NotImplementedError(f"Cannot not add Vec3 to '{other.__class__.__name__}'")
    def __radd__(self, other):
        return self.__add__(other)
     
    def __sub__(self, other):
        if isinstance(other, (Vec2, self.__class__, int, float)):
            return self.__add__(other * -1)
        elif isinstance(other, tuple | list):
            if len(other) != 3:
                raise ValueError("Tuple must have 3 elements")
            return Vec3(self.x - other[0], self.y - other[1], self.z - other[2])
        
        raise NotImplementedError(f"Cannot not subtract '{other.__class__.__name__}' from Vec3")
    
    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, (int, float)):
            return self.__class__(self.x * other, self.y * other, self.z * other)
        
        raise NotImplementedError(f"Cannot not multiply Vec3 with '{other.__class__.__name__}'")
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y}, {self.z})"

    def project(self):
        at_infinity = not self.z
        
        v = Vec2(self.x / self.z, self.y / self.z) if not at_infinity else Vec2(None, None)
        v.at_infinity = at_infinity
        
        return v

    def coordinates(self):
        return self.x, self.y, self.z
    
    def dot(self, vec: "Vec3"):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z

class AngleVec3(Vec3):
    @property
    def xz(self):
        return self._xz
    @xz.setter
    def xz(self, value: Number):
        self.x = value
    
    @property
    def yz(self):
        return self._yz
    @yz.setter
    def yz(self, value: Number):
        self.y = value
    
    @property
    def xy(self):
        return self._xy
    @xy.setter
    def xy(self, value: Number):
        self.z = value
    
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value: Number):
        self._x = self._xz = value
    
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value: Number):
        self._y = self._yz = value
    
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self, value: Number):
        self._z = self._xy = value

@dataclass
class Transforms:
    def translate(vertex: Vec3, offset: Vec3):
        return vertex + offset
    
    def scale(vertex: Vec3, scale: Vec3):
        return vertex * scale
    
    def rotate(vertex: Vec3, angle: AngleVec3):
        x_prime1, y_prime1, z_prime1 = (
            vertex.x * math.cos(math.radians(angle.xy)) - vertex.y * math.sin(math.radians(angle.xy)),
            vertex.y * math.cos(math.radians(angle.xy)) + vertex.x * math.sin(math.radians(angle.xy)),
            vertex.z,
        )
        
        x_prime2, y_prime2, z_prime2 = (
            x_prime1 * math.cos(math.radians(angle.xz)) - z_prime1 * math.sin(math.radians(angle.xz)),
            y_prime1,
            z_prime1 * math.cos(math.radians(angle.xz)) + x_prime1 * math.sin(math.radians(angle.xz)),
        )
        
        x_prime3, y_prime3, z_prime3 = (
            x_prime2,
            y_prime2 * math.cos(math.radians(angle.yz)) + z_prime2 * math.sin(math.radians(angle.yz)),
            z_prime2 * math.cos(math.radians(angle.yz)) - y_prime2 * math.sin(math.radians(angle.yz)),
        )
        
        return Vec3(x_prime3, y_prime3, z_prime3)



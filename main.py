from enum import Enum
import math
from typing import Any, Callable
import pygame
from sys import exit

WIDTH = 500
HEIGHT = 500

POINT_SIZE = 4

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def point(x: float, y: float):
    return (x + 1) * WIDTH / 2, (1 - y) * HEIGHT / 2

def project(x: float, y: float, z: float):
    if not z:
        return None, None
    
    return x / z, y / z

def translate(x: float, y: float, z: float, dx: float, dy: float, dz: float):
    return x + dx, y + dy, z + dz

def scale(x: float, y: float, z: float, sx: float, sy: float, sz: float):
    return x * sx, y * sy, z * sz

def rotate(x: float, y: float, z: float, xy_angle: float, xz_angle: float, yz_angle: float):
    x_prime1, y_prime1, z_prime1 = (
        x * math.cos(math.radians(xy_angle)) - y * math.sin(math.radians(xy_angle)),
        y * math.cos(math.radians(xy_angle)) + x * math.sin(math.radians(xy_angle)),
        z,
    )
    
    x_prime2, y_prime2, z_prime2 = (
        x_prime1 * math.cos(math.radians(xz_angle)) - z_prime1 * math.sin(math.radians(xz_angle)),
        y_prime1,
        z_prime1 * math.cos(math.radians(xz_angle)) + x_prime1 * math.sin(math.radians(xz_angle)),
    )
    
    x_prime3, y_prime3, z_prime3 = (
        x_prime2,
        y_prime2 * math.cos(math.radians(yz_angle)) + z_prime2 * math.sin(math.radians(yz_angle)),
        z_prime2 * math.cos(math.radians(yz_angle)) - y_prime2 * math.sin(math.radians(yz_angle)),
    )
    
    return x_prime3, y_prime3, z_prime3

def screen_point(x: float, y: float, z: float, *transformations: tuple[Callable[[float, float, float], tuple[float, float, float]], list]):
    x_prime, y_prime, z_prime = x, y, z
    for fn, params in transformations:
        x_prime, y_prime, z_prime = fn(x_prime, y_prime, z_prime, *params)
    
    x_prime, y_prime = project(x_prime, y_prime, z_prime)
    
    if None not in (x_prime, y_prime):
        x_prime, y_prime = point(x_prime, y_prime)
        
    return x_prime, y_prime

def vertex_to_screen_point(x: float, y: float, z: float, dx: float, dy: float, dz: float, sx: float, sy: float, sz: float, xy_angle: float, xz_angle: float, yz_angle: float):
    return screen_point(x, y, z, (rotate, (xy_angle, xz_angle, yz_angle)), (scale, (sx, sy, sz)), (translate, (dx, dy, dz + 1)))

Number = int | float


class Vec2:
    def __init__(self, x: Number, y: Number):
        self.x = x
        self.y = y
        
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
            return NotImplemented
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
            return NotImplemented
    
    def __mul__(self, other):
        if not self.at_infinity:
            if isinstance(other, (int, float)):
                return Vec2(self.x * other, self.y * other)
            return NotImplemented
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

class Vec3:
    def __init__(self, x: Number, y: Number, z: Number):
        self._x = x
        self._y = y
        self._z = z
        
        self.x = self._x
        self.y = self._y
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
        
        return NotImplemented
    def __radd__(self, other):
        return self.__add__(other)
     
    def __sub__(self, other):
        if isinstance(other, (Vec2, self.__class__, int, float)):
            return self.__add__(other * -1)
        elif isinstance(other, tuple | list):
            if len(other) != 3:
                raise ValueError("Tuple must have 3 elements")
            return Vec3(self.x - other[0], self.y - other[1], self.z - other[2])
        
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, (int, float)):
            return self.__class__(self.x * other, self.y * other, self.z * other)
        return NotImplemented
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


class Transforms:
    @staticmethod
    def translate(vertex: Vec3, offset: Vec3):
        return vertex + offset
    
    @staticmethod
    def scale(vertex: Vec3, scale: Vec3):
        return vertex * scale
    
    @staticmethod
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

class DisplayFlags(Enum):
    VERTEX   =  0b0001
    VERTEX_I =  0b0010
    WIRE     =  0b0100
    FACE     =  0b1000


class Model:
    def __init__(self, screen: pygame.Surface, vertices: list[tuple[Number, Number, Number]], faces: list[list[int]], origin: Vec3 = Vec3(0, 0, 1)):
        self.screen = screen
        
        self.vertices = [Vec3(*vertex) for vertex in vertices]
        self.faces = faces
        
        self.origin = origin
        
        self.position = Vec3(0, 0, 0)
        self.scale = Vec3(1, 1, 1)
        self.angle = AngleVec3(0, 0, 0)
        
        self.Update_init()
    
    # Display Logic
    def _transform(self, vertex: Vec3, *transformations: tuple[Callable[[Vec3, Any], Vec3], list]):
        for fn, params in transformations:
            # print(vertex)
            vertex = fn(vertex, *params)
        
        vertex_prime = vertex.project()
        
        return vertex_prime
    
    def _project_vertex(self, vertex: Vec3):
        return self._transform(
                vertex,
                (Transforms.rotate, (self.angle,)),
                (Transforms.scale, (self.scale,)),
                (Transforms.translate, (self.position + self.origin,))
            ).project(self.screen)
    
    # Display
    def _draw_point_data(self, show_vertex: bool, show_vertex_indices: bool):
        for i, vertex in enumerate(self.vertices):
            v = self._project_vertex(vertex)
            
            if not v.at_infinity:
                if show_vertex:
                    pygame.draw.rect(screen, "green", (v.x - POINT_SIZE / 2, v.y - POINT_SIZE / 2, POINT_SIZE, POINT_SIZE))
                
                if show_vertex_indices:
                    text_surf = font.render(str(i), True, "green")
                    screen.blit(text_surf, text_surf.get_rect(midbottom=(v.x, v.y - POINT_SIZE / 2)))
    
    def _draw_surface_data(self, show_wireframe: bool, show_face: bool):
        for face in self.faces:
            for index, vert_index in enumerate(face):
                v1 = self.vertices[vert_index]
                v2 = self.vertices[face[(index + 1) % len(face)]]
                
                p1 = self._project_vertex(v1)
                p2 = self._project_vertex(v2)
                
                if not (p1.at_infinity + p2.at_infinity):
                    if show_face:
                        raise NotImplementedError("Figure this out")
                    
                    if show_wireframe:
                        pygame.draw.line(screen, "white", p1.coordinates(), p2.coordinates())
    
    def draw(self, display_flag: int):
        vertices = display_flag & DisplayFlags.VERTEX.value == DisplayFlags.VERTEX.value
        vertex_indices = display_flag & DisplayFlags.VERTEX_I.value == DisplayFlags.VERTEX_I.value
        wireframe = display_flag & DisplayFlags.WIRE.value == DisplayFlags.WIRE.value
        faces = display_flag & DisplayFlags.FACE.value == DisplayFlags.FACE.value
        
        if vertices + vertex_indices:
            self._draw_point_data(vertices, vertex_indices)
        if wireframe + faces:
            self._draw_surface_data(wireframe, faces)
    
    # Update
    def Update_init(self):
        pass
    
    def Update(self, *args, **kwargs):
        pass
    
    def run(self, display_flag: int, *args, **kwargs):
        self.Update()
        self.draw(display_flag)

class KeyBoardControlledBox(Model):
    def Update_init(self):
        self._i_dx = self._i_dy = self._i_dz = 0
        self._i_sx = self._i_sy = self._i_sz = 1
        self._i_xy_angle = self._i_xz_angle = self._i_yz_angle = 0
        
        self._reset_time = 0
        self._is_resetting = False
        
        self.font = pygame.font.SysFont("Monospace", 15)
    
    def Update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.position.z += 1 / clock.get_fps()
        if keys[pygame.K_DOWN]:
            self.position.z -= 1 / clock.get_fps()
        if keys[pygame.K_RIGHT]:
            self.position.x += 1 / clock.get_fps()
        if keys[pygame.K_LEFT]:
            self.position.x -= 1 / clock.get_fps()
        if keys[pygame.K_PAGEUP]:
            self.position.y += 1 / clock.get_fps()
        if keys[pygame.K_PAGEDOWN]:
            self.position.y -= 1 / clock.get_fps()
        
        if keys[pygame.K_q]:
            self.angle.xy += 360 / 60
        if keys[pygame.K_z]:
            self.angle.xy -= 360 / 60
        if keys[pygame.K_d]:
            self.angle.xz += 360 / 60
        if keys[pygame.K_a]:
            self.angle.xz -= 360 / 60
        if keys[pygame.K_w]:
            self.angle.yz += 360 / 60
        if keys[pygame.K_s]:
            self.angle.yz -= 360 / 60
        
        if keys[pygame.K_i]:
            self.scale.z += 1 / clock.get_fps()
        if keys[pygame.K_k]:
            self.scale.z -= 1 / clock.get_fps()
        if keys[pygame.K_l]:
            self.scale.x += 1 / clock.get_fps()
        if keys[pygame.K_j]:
            self.scale.x -= 1 / clock.get_fps()
        if keys[pygame.K_HOME]:
            self.scale.y += 1 / clock.get_fps()
        if keys[pygame.K_END]:
            self.scale.y -= 1 / clock.get_fps()
        
        self.angle.xy = self.angle.xy % 360
        self.angle.xz = self.angle.xz % 360
        self.angle.yz = self.angle.yz % 360
        
        if keys[pygame.K_r] and (self.position.x + self.position.y + self.position.z + self.scale.x + self.scale.y + self.scale.z + self.angle.xy + self.angle.xz + self.angle.yz) and not self._is_resetting:
            self._is_resetting = True
            
            self._i_dx = self.position.x
            self._i_dy = self.position.y
            self._i_dz = self.position.z
            
            self._i_sx = self.scale.x - 1
            self._i_sy = self.scale.y - 1
            self._i_sz = self.scale.z - 1
            
            self._i_xy_angle = self.angle.xy
            self._i_xz_angle = self.angle.xz
            self._i_yz_angle = self.angle.yz
        
        if self._is_resetting:
            dt = 2 / clock.get_fps()
            
            self.position.x -= self._i_dx * dt
            self.position.y -= self._i_dy * dt
            self.position.z -= self._i_dz * dt
            
            self.scale.x -= self._i_sx * dt
            self.scale.y -= self._i_sy * dt
            self.scale.z -= self._i_sz * dt
            
            self.angle.xy -= self._i_xy_angle * dt
            self.angle.xz -= self._i_xz_angle * dt
            self.angle.yz -= self._i_yz_angle * dt
            
            self._reset_time += dt
            
            if self._reset_time >= 1:
                self._is_resetting = False
                
                self._reset_time = 0
                self.position *= 0
                self.angle *= 0
                
                self.scale *= 0
                self.scale += 1
        
        


v = [
    # Back Face
    (-0.25, -0.25, 0.25),
    (-0.25, 0.25, 0.25),
    (0.25, 0.25, 0.25),
    (0.25, -0.25, 0.25),
    
    # Front Face
    (-0.25, -0.25, -0.25),
    (-0.25, 0.25, -0.25),
    (0.25, 0.25, -0.25),
    (0.25, -0.25, -0.25),
]

f = [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [4, 0],
    [3, 7],
    [2, 6],
    [1, 5]
]

font = pygame.font.SysFont("Cambria", 20)

b = KeyBoardControlledBox(screen, v, f)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
    b.run(DisplayFlags.VERTEX.value | DisplayFlags.VERTEX_I.value | DisplayFlags.WIRE.value)
    
    screen.blit(font.render(str(int(clock.get_fps())), False, "White"), (10, 10))
    
    pygame.display.update()
    
    screen.fill("black")
    
    clock.tick(60)
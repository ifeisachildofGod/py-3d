import pygame
from constants import *
from typing import Any, Callable
from point_data import Vec3, AngleVec3, Transforms

class BaseModel:
    def __init__(self, screen: pygame.Surface, data: ModelData, origin: Vec3 = Vec3(0, 0, 1), *args, **kwargs):
        self.screen = screen
        self.font = pygame.font.SysFont("Monospace", 15)
        
        self.vertices = [Vec3(*vertex) for vertex in data.v]
        self.faces = data.f
        
        self.origin = origin
        
        self.position = Vec3(0, 0, 0)
        self.scale = Vec3(1, 1, 1)
        self.angle = AngleVec3(0, 0, 0)
        
        self.Update_init(*args, **kwargs)
    
    # Display Logic
    def _transform(self, vertex: Vec3, *transformations: tuple[Callable[[Vec3, Any], Vec3], list]):
        for fn, params in transformations:
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
                    pygame.draw.rect(self.screen, "green", (v.x - POINT_SIZE / 2, v.y - POINT_SIZE / 2, POINT_SIZE, POINT_SIZE))
                
                if show_vertex_indices:
                    text_surf = self.font.render(str(i), True, "green")
                    self.screen.blit(text_surf, text_surf.get_rect(midbottom=(v.x, v.y - POINT_SIZE / 2)))
    
    def _draw_surface_data(self, show_wireframe: bool, show_face: bool):
        for face in self.faces:
            for index, vert_index in enumerate(face):
                if len(face) == 2 and index == 1:
                    break
                
                v1 = self.vertices[vert_index]
                v2 = self.vertices[face[(index + 1) % len(face)]]
                
                p1 = self._project_vertex(v1)
                p2 = self._project_vertex(v2)
                
                if not (p1.at_infinity + p2.at_infinity):
                    if show_face:
                        raise NotImplementedError()
                        # pygame.draw.rect(self.screen, "white", (p1.coordinates(), p2.coordinates()))
                    
                    if show_wireframe:
                        pygame.draw.line(self.screen, "white", p1.coordinates(), p2.coordinates())
    
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
    def Update_init(self, *args, **kwargs):
        pass
    
    def Update(self, *args, **kwargs):
        pass
    
    def run(self, display_flag: int, *args, **kwargs):
        self.Update(*args, **kwargs)
        self.draw(display_flag)

class KeyBoardControlledBox(BaseModel):
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, data: ModelData, origin = Vec3(0, 0, 1)):
        super().__init__(screen, data, origin, clock)
    
    def Update_init(self, clock: pygame.time.Clock):
        self.origin.z = 10
        
        self._i_dx = self._i_dy = self._i_dz = 0
        self._i_sx = self._i_sy = self._i_sz = 1
        self._i_xy_angle = self._i_xz_angle = self._i_yz_angle = 0
        
        self._reset_time = 0
        self._is_resetting = False
        
        self.clock = clock
    
    def Update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.position.z += 2 / self.clock.get_fps()
        if keys[pygame.K_DOWN]:
            self.position.z -= 2 / self.clock.get_fps()
        if keys[pygame.K_RIGHT]:
            self.position.x += 2 / self.clock.get_fps()
        if keys[pygame.K_LEFT]:
            self.position.x -= 2 / self.clock.get_fps()
        if keys[pygame.K_PAGEUP]:
            self.position.y += 2 / self.clock.get_fps()
        if keys[pygame.K_PAGEDOWN]:
            self.position.y -= 2 / self.clock.get_fps()
        
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
            self.scale.z += 2 / self.clock.get_fps()
        if keys[pygame.K_k]:
            self.scale.z -= 2 / self.clock.get_fps()
        if keys[pygame.K_l]:
            self.scale.x += 2 / self.clock.get_fps()
        if keys[pygame.K_j]:
            self.scale.x -= 2 / self.clock.get_fps()
        if keys[pygame.K_HOME]:
            self.scale.y += 2 / self.clock.get_fps()
        if keys[pygame.K_END]:
            self.scale.y -= 2 / self.clock.get_fps()
        
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
            dt = 2 / self.clock.get_fps()
            
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


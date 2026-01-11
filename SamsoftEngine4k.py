#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║               ULTRA MARIO 64 - PURE MATH EDITION (PYGAME CE)                      ║
║                          Team Flames / Samsoft / Cat OS                           ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  ENGINE: Custom Software Rasterizer (No OpenGL/3D acceleration)                   ║
║  TECH:   Manual Matrix Multiplication, Perspective Projection, Z-Sorting          ║
║  REQ:    pygame-ce (or standard pygame), math                                     ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

import pygame
import math
import sys
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ═══════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════

WIDTH, HEIGHT = 960, 720  # Retro resolution
FPS = 60
FOV = 600.0  # Field of view scale factor

# Colors (N64 Palette)
C_SKY = (100, 149, 237)
C_MARIO_RED = (255, 20, 20)
C_MARIO_BLUE = (20, 20, 240)
C_SKIN = (255, 200, 150)
C_BROWN = (100, 50, 20)
C_GOLD = (255, 215, 0)
C_GRASS = (34, 139, 34)
C_CASTLE = (200, 200, 200)
C_ROOF = (200, 50, 50)
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_SHADOW = (0, 0, 0, 100) # Fake shadow

# ═══════════════════════════════════════════════════════════════════════════════════
# 3D MATH ENGINE (THE MIYAMOTO STUFF)
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other): return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other): return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, scalar): return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        l = self.length()
        if l == 0: return Vec3(0,0,0)
        return Vec3(self.x/l, self.y/l, self.z/l)

@dataclass
class Polygon:
    """A projected polygon ready for rendering"""
    points: List[Tuple[float, float]]
    z_depth: float  # Average Z for sorting
    color: Tuple[int, int, int]

class Mesh:
    """A collection of vertices and faces forming a 3D object"""
    def __init__(self, vertices: List[Vec3], faces: List[List[int]], color: Tuple[int, int, int]):
        self.vertices = vertices  # Local space vertices
        self.faces = faces        # Indices into vertices list
        self.color = color
        self.position = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0) # Pitch, Yaw, Roll
        self.scale = Vec3(1, 1, 1)
        self.visible = True

class MathEngine:
    """Handles raw geometric calculations"""
    
    @staticmethod
    def rotate_point(point: Vec3, rot: Vec3) -> Vec3:
        """Apply Euler rotation (X, Y, Z) to a point"""
        # Copy coordinates
        x, y, z = point.x, point.y, point.z
        
        # Rotate X (Pitch)
        if rot.x != 0:
            cos_x, sin_x = math.cos(rot.x), math.sin(rot.x)
            y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
            
        # Rotate Y (Yaw)
        if rot.y != 0:
            cos_y, sin_y = math.cos(rot.y), math.sin(rot.y)
            x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
            
        # Rotate Z (Roll)
        if rot.z != 0:
            cos_z, sin_z = math.cos(rot.z), math.sin(rot.z)
            x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
            
        return Vec3(x, y, z)

    @staticmethod
    def project(point: Vec3, camera_pos: Vec3, camera_rot: Vec3) -> Optional[Tuple[float, float, float]]:
        """
        World Space -> Camera Space -> Screen Space
        Returns (screen_x, screen_y, depth) or None if behind camera
        """
        # 1. Translate to camera space (World - Camera)
        x = point.x - camera_pos.x
        y = point.y - camera_pos.y
        z = point.z - camera_pos.z
        
        # 2. Rotate by Camera inverse orientation
        # Reverse order of camera rotation logic to "un-rotate" the world
        
        # Yaw (Camera Y rotation)
        cos_y, sin_y = math.cos(-camera_rot.y), math.sin(-camera_rot.y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
        
        # Pitch (Camera X rotation)
        cos_x, sin_x = math.cos(-camera_rot.x), math.sin(-camera_rot.x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # 3. Clip objects behind the camera
        if z <= 1.0: # Near clipping plane
            return None
            
        # 4. Perspective Projection (The "Magic" divide by Z)
        factor = FOV / z
        screen_x = x * factor + WIDTH / 2
        screen_y = -y * factor + HEIGHT / 2 # Flip Y for screen coords
        
        return (screen_x, screen_y, z)

# ═══════════════════════════════════════════════════════════════════════════════════
# GAME OBJECTS & LEVEL GENERATION
# ═══════════════════════════════════════════════════════════════════════════════════

class ObjectFactory:
    """Procedurally generates 3D meshes"""
    
    @staticmethod
    def create_cube(size: float, color: Tuple[int, int, int]) -> Mesh:
        s = size / 2
        verts = [
            Vec3(-s, -s, -s), Vec3(s, -s, -s), Vec3(s, s, -s), Vec3(-s, s, -s), # Bottom
            Vec3(-s, -s, s), Vec3(s, -s, s), Vec3(s, s, s), Vec3(-s, s, s)      # Top
        ]
        faces = [
            [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], # Sides
            [0, 1, 2, 3], [4, 5, 6, 7] # Bottom, Top
        ]
        return Mesh(verts, faces, color)

    @staticmethod
    def create_mario() -> List[Mesh]:
        """Constructs Mario from geometric primitives (Low Poly Style)"""
        parts = []
        
        # Head (Cube approximation)
        head = ObjectFactory.create_cube(12, C_SKIN)
        head.position = Vec3(0, 24, 0)
        parts.append(head)
        
        # Hat (Red Box + Brim)
        hat = ObjectFactory.create_cube(12.5, C_MARIO_RED)
        hat.position = Vec3(0, 28, -1)
        hat.scale = Vec3(1, 0.4, 1)
        parts.append(hat)
        
        brim = ObjectFactory.create_cube(12, C_MARIO_RED)
        brim.position = Vec3(0, 27, 4)
        brim.scale = Vec3(1.1, 0.1, 0.5)
        parts.append(brim)
        
        # Torso (Blue + Red)
        torso = ObjectFactory.create_cube(10, C_MARIO_BLUE)
        torso.position = Vec3(0, 14, 0)
        torso.scale = Vec3(1.2, 1.4, 0.8)
        parts.append(torso)
        
        shirt = ObjectFactory.create_cube(9, C_MARIO_RED)
        shirt.position = Vec3(0, 18, 0)
        shirt.scale = Vec3(1.1, 0.5, 0.7)
        parts.append(shirt)
        
        # Arms
        l_arm = ObjectFactory.create_cube(3, C_MARIO_RED)
        l_arm.position = Vec3(-8, 16, 0)
        l_arm.scale = Vec3(1, 3, 1)
        l_arm.rotation.z = 0.5
        parts.append(l_arm)
        
        r_arm = ObjectFactory.create_cube(3, C_MARIO_RED)
        r_arm.position = Vec3(8, 16, 0)
        r_arm.scale = Vec3(1, 3, 1)
        r_arm.rotation.z = -0.5
        parts.append(r_arm)
        
        # Hands
        l_hand = ObjectFactory.create_cube(4, C_WHITE)
        l_hand.position = Vec3(-10, 12, 0)
        parts.append(l_hand)
        
        r_hand = ObjectFactory.create_cube(4, C_WHITE)
        r_hand.position = Vec3(10, 12, 0)
        parts.append(r_hand)
        
        # Legs
        l_leg = ObjectFactory.create_cube(3.5, C_MARIO_BLUE)
        l_leg.position = Vec3(-3, 6, 0)
        l_leg.scale = Vec3(1, 2.5, 1)
        parts.append(l_leg)
        
        r_leg = ObjectFactory.create_cube(3.5, C_MARIO_BLUE)
        r_leg.position = Vec3(3, 6, 0)
        r_leg.scale = Vec3(1, 2.5, 1)
        parts.append(r_leg)
        
        # Shoes
        l_shoe = ObjectFactory.create_cube(4, C_BROWN)
        l_shoe.position = Vec3(-3, 1, 2)
        l_shoe.scale = Vec3(1, 1, 1.5)
        parts.append(l_shoe)
        
        r_shoe = ObjectFactory.create_cube(4, C_BROWN)
        r_shoe.position = Vec3(3, 1, 2)
        r_shoe.scale = Vec3(1, 1, 1.5)
        parts.append(r_shoe)
        
        return parts

    @staticmethod
    def create_level() -> List[Mesh]:
        """Generates the Castle Grounds"""
        level_parts = []
        
        # Main Ground
        ground = ObjectFactory.create_cube(2000, C_GRASS)
        ground.position = Vec3(0, -1005, 0) # Floor at y=0 roughly
        level_parts.append(ground)
        
        # Castle Base
        base = ObjectFactory.create_cube(400, C_CASTLE)
        base.position = Vec3(0, 100, 300)
        base.scale = Vec3(1, 0.5, 1)
        level_parts.append(base)
        
        # Castle Tower
        tower = ObjectFactory.create_cube(150, C_CASTLE)
        tower.position = Vec3(0, 250, 300)
        tower.scale = Vec3(1, 1.5, 1)
        level_parts.append(tower)
        
        # Roof
        roof = ObjectFactory.create_cube(160, C_ROOF)
        roof.position = Vec3(0, 360, 300)
        roof.rotation = Vec3(0, 0.78, 0) # 45 degrees
        level_parts.append(roof)
        
        # Bridge
        bridge = ObjectFactory.create_cube(100, C_BROWN)
        bridge.position = Vec3(0, 5, 100)
        bridge.scale = Vec3(0.6, 0.1, 2.0)
        level_parts.append(bridge)
        
        # Coins
        for i in range(8):
            angle = (i / 8) * math.pi * 2
            x = math.cos(angle) * 200
            z = math.sin(angle) * 200
            
            coin = ObjectFactory.create_cube(20, C_GOLD)
            coin.position = Vec3(x, 40, z)
            coin.rotation = Vec3(0, i, 0) # Initial rotation
            coin.tag = "coin" # Marker for animation
            level_parts.append(coin)
            
        return level_parts

# ═══════════════════════════════════════════════════════════════════════════════════
# GAME LOGIC
# ═══════════════════════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ultra Mario 64 - Math Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        
        # Game State
        self.running = True
        
        # Camera (Lakitu)
        self.camera_pos = Vec3(0, 100, -300)
        self.camera_rot = Vec3(0.2, 0, 0) # Pitch, Yaw, Roll
        self.cam_dist = 300
        self.cam_angle = 0
        
        # Player (Mario)
        self.mario_pos = Vec3(0, 0, 0)
        self.mario_rot = 0 # Yaw
        self.mario_vel = Vec3(0, 0, 0)
        self.is_grounded = True
        
        # Assets
        self.mario_meshes = ObjectFactory.create_mario()
        self.level_meshes = ObjectFactory.create_level()
        
        # Animation
        self.anim_timer = 0
        
        # Input
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Movement
        speed = 5.0
        moved = False
        
        # Mario controls are camera-relative in standard SM64, 
        # but for this math demo, we'll use tank controls relative to Mario's facing
        # to simplify the vector math visualization.
        
        # Rotation
        if keys[pygame.K_a]:
            self.mario_rot -= 0.05
        if keys[pygame.K_d]:
            self.mario_rot += 0.05
            
        # Movement vector based on rotation
        forward = Vec3(math.sin(self.mario_rot), 0, math.cos(self.mario_rot))
        
        if keys[pygame.K_w]:
            self.mario_vel.x = forward.x * speed
            self.mario_vel.z = forward.z * speed
            moved = True
        elif keys[pygame.K_s]:
            self.mario_vel.x = -forward.x * speed
            self.mario_vel.z = -forward.z * speed
            moved = True
        else:
            self.mario_vel.x = 0
            self.mario_vel.z = 0
            
        # Jump
        if keys[pygame.K_SPACE] and self.is_grounded:
            self.mario_vel.y = 15
            self.is_grounded = False
            
        # Camera controls (Arrow keys)
        if keys[pygame.K_LEFT]: self.cam_angle -= 0.03
        if keys[pygame.K_RIGHT]: self.cam_angle += 0.03
        
        # Animation state
        if moved and self.is_grounded:
            self.anim_timer += 0.3
        else:
            self.anim_timer = 0

    def update_physics(self):
        # Gravity
        if not self.is_grounded:
            self.mario_vel.y -= 0.8
            
        # Apply velocity
        self.mario_pos.x += self.mario_vel.x
        self.mario_pos.y += self.mario_vel.y
        self.mario_pos.z += self.mario_vel.z
        
        # Simple floor collision (y = 0)
        if self.mario_pos.y <= 0:
            self.mario_pos.y = 0
            self.mario_vel.y = 0
            self.is_grounded = True
            
        # Update Lakitu Camera (Orbit around Mario)
        target_x = self.mario_pos.x - math.sin(self.cam_angle) * self.cam_dist
        target_z = self.mario_pos.z - math.cos(self.cam_angle) * self.cam_dist
        
        # Smooth follow
        self.camera_pos.x += (target_x - self.camera_pos.x) * 0.1
        self.camera_pos.z += (target_z - self.camera_pos.z) * 0.1
        self.camera_pos.y += ((self.mario_pos.y + 100) - self.camera_pos.y) * 0.1
        
        # Camera LookAt rotation (simplified)
        dx = self.mario_pos.x - self.camera_pos.x
        dy = self.mario_pos.y + 40 - self.camera_pos.y
        dz = self.mario_pos.z - self.camera_pos.z
        
        self.camera_rot.y = math.atan2(dx, dz)
        self.camera_rot.x = math.atan2(dy, math.sqrt(dx*dx + dz*dz))

    def animate_mario(self):
        """Update Mario's body parts based on state"""
        # Bobbing
        bounce = math.sin(self.anim_timer) * 2
        
        # Access body parts by index (known from factory)
        # 5=L_Arm, 6=R_Arm, 9=L_Leg, 10=R_Leg
        
        walk_swing = math.sin(self.anim_timer) * 0.5
        
        # Arms swing opposite to legs
        self.mario_meshes[5].rotation.x = walk_swing
        self.mario_meshes[6].rotation.x = -walk_swing
        
        # Legs
        self.mario_meshes[9].rotation.x = -walk_swing
        self.mario_meshes[10].rotation.x = walk_swing
        
        # Rotate whole group
        for mesh in self.mario_meshes:
            mesh.rotation.y = self.mario_rot

    def render(self):
        self.screen.fill(C_SKY)
        
        # 1. Collect all polygons from all meshes
        polygons = []
        
        all_meshes = self.level_meshes + self.mario_meshes
        
        for mesh in all_meshes:
            # Handle object-specific animation/logic
            if hasattr(mesh, 'tag') and mesh.tag == "coin":
                mesh.rotation.y += 0.05
            
            # Pre-calculate Trignometry for rotation
            cr_x, sr_x = math.cos(mesh.rotation.x), math.sin(mesh.rotation.x)
            cr_y, sr_y = math.cos(mesh.rotation.y), math.sin(mesh.rotation.y)
            cr_z, sr_z = math.cos(mesh.rotation.z), math.sin(mesh.rotation.z)
            
            # Position offset for Mario parts relative to Mario Center
            offset = mesh.position
            if mesh in self.mario_meshes:
                offset = mesh.position + self.mario_pos
            
            # Process Vertices
            world_verts = []
            for v in mesh.vertices:
                # 1. Scale
                vx, vy, vz = v.x * mesh.scale.x, v.y * mesh.scale.y, v.z * mesh.scale.z
                
                # 2. Rotation (Local)
                # X
                vy, vz = vy * cr_x - vz * sr_x, vy * sr_x + vz * cr_x
                # Y
                vx, vz = vx * cr_y + vz * sr_y, -vx * sr_y + vz * cr_y
                # Z
                vx, vy = vx * cr_z - vy * sr_z, vx * sr_z + vy * cr_z
                
                # 3. Translation (World)
                world_verts.append(Vec3(vx + offset.x, vy + offset.y, vz + offset.z))
                
            # Process Faces
            for face in mesh.faces:
                # Get vertices for this face
                face_verts = [world_verts[i] for i in face]
                
                # Simple Backface Culling (Check normal vs camera vector)
                # Calculate normal vector of the face
                v1 = face_verts[1] - face_verts[0]
                v2 = face_verts[2] - face_verts[0]
                normal = Vec3(
                    v1.y * v2.z - v1.z * v2.y,
                    v1.z * v2.x - v1.x * v2.z,
                    v1.x * v2.y - v1.y * v2.x
                )
                
                # Vector from camera to face
                cam_to_face = face_verts[0] - self.camera_pos
                
                # Dot product
                dot = normal.x * cam_to_face.x + normal.y * cam_to_face.y + normal.z * cam_to_face.z
                
                if dot >= 0: # If normal points away from camera (or perpendicular), Cull it
                    continue
                
                # Project Vertices
                projected_points = []
                avg_z = 0
                valid_face = True
                
                for v in face_verts:
                    proj = MathEngine.project(v, self.camera_pos, self.camera_rot)
                    if proj is None:
                        valid_face = False
                        break
                    projected_points.append((proj[0], proj[1]))
                    avg_z += proj[2]
                
                if valid_face:
                    avg_z /= len(face_verts)
                    # Simple lighting based on normal
                    normal.normalize()
                    light_dir = Vec3(0.5, 1, -0.5).normalize()
                    light_intensity = max(0.2, min(1.0, normal.x*light_dir.x + normal.y*light_dir.y + normal.z*light_dir.z))
                    
                    lit_color = (
                        int(mesh.color[0] * light_intensity),
                        int(mesh.color[1] * light_intensity),
                        int(mesh.color[2] * light_intensity)
                    )
                    
                    polygons.append(Polygon(projected_points, avg_z, lit_color))

        # 2. Sort polygons by depth (Painter's Algorithm)
        # Sort desc (far to near)
        polygons.sort(key=lambda p: p.z_depth, reverse=True)
        
        # 3. Draw
        for poly in polygons:
            pygame.draw.polygon(self.screen, poly.color, poly.points)
            # Wireframe outline for that retro crunchy look
            # pygame.draw.polygon(self.screen, (0,0,0), poly.points, 1)

        # UI
        ui_text = f"STARS: {len(self.collected_stars)}  FPS: {int(self.clock.get_fps())}"
        surf = self.font.render(ui_text, True, C_WHITE)
        self.screen.blit(surf, (20, 20))
        
        # Ground Shadow (Fake)
        shadow_proj = MathEngine.project(self.mario_pos, self.camera_pos, self.camera_rot)
        if shadow_proj:
            pygame.draw.circle(self.screen, (0,0,0), (shadow_proj[0], shadow_proj[1]), 2000/shadow_proj[2])

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.handle_input()
            self.update_physics()
            self.animate_mario()
            self.render()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

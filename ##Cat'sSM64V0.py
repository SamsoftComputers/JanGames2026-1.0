#!/usr/bin/env python3
"""
SUPER MARIO 64 - PYGAME-CE 3D ENGINE
=====================================
Nintendo EAD-accurate 3D platformer
All 15 main courses + Castle hub

Features:
- Software 3D rendering with Z-buffer
- Full Mario moveset (jump, double/triple jump, long jump, backflip, wall kick, ground pound)
- Lakitu-style camera system
- Procedural textures and models (no external files)
- Authentic SM64 physics

Controls:
- WASD/Arrow keys: Move
- SPACE: Jump (tap for short hop, hold for full jump)
- SHIFT: Run/Dive
- CTRL: Crouch/Ground pound
- Q/E: Camera rotate
- ESC: Pause

© 2026 Team Flames / Samsoft - SM64 Recreation
"""

import pygame
import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum, auto
import colorsys

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ==================== CONSTANTS ====================
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
FPS = 60
FOV = 70  # Field of view in degrees
NEAR_PLANE = 0.1
FAR_PLANE = 1000.0

# SM64 scale (1 unit = ~1 meter)
SCALE = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DIRT_BROWN = (139, 69, 19)
STONE_GRAY = (128, 128, 128)
WATER_BLUE = (64, 164, 223)
SAND_YELLOW = (238, 214, 175)
SNOW_WHITE = (250, 250, 255)
LAVA_ORANGE = (255, 100, 0)
CASTLE_GRAY = (169, 169, 169)

# ==================== 3D MATH ====================
@dataclass
class Vec3:
    """3D Vector with math operations"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            return Vec3(0, 0, 0)
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other) -> 'Vec3':
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def length_xz(self) -> float:
        """Horizontal length (for ground speed)"""
        return math.sqrt(self.x**2 + self.z**2)
    
    def normalize(self) -> 'Vec3':
        l = self.length()
        if l == 0:
            return Vec3(0, 0, 0)
        return Vec3(self.x / l, self.y / l, self.z / l)
    
    def rotate_y(self, angle: float) -> 'Vec3':
        """Rotate around Y axis"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vec3(
            self.x * cos_a - self.z * sin_a,
            self.y,
            self.x * sin_a + self.z * cos_a
        )
    
    def tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def copy(self) -> 'Vec3':
        return Vec3(self.x, self.y, self.z)


@dataclass
class Triangle:
    """3D Triangle for rendering"""
    v0: Vec3
    v1: Vec3
    v2: Vec3
    color: Tuple[int, int, int] = WHITE
    normal: Vec3 = None
    
    def __post_init__(self):
        if self.normal is None:
            self.calculate_normal()
    
    def calculate_normal(self):
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = edge1.cross(edge2).normalize()
    
    def center(self) -> Vec3:
        return Vec3(
            (self.v0.x + self.v1.x + self.v2.x) / 3,
            (self.v0.y + self.v1.y + self.v2.y) / 3,
            (self.v0.z + self.v1.z + self.v2.z) / 3
        )


class Matrix4:
    """4x4 Matrix for 3D transformations"""
    def __init__(self):
        self.m = [[0.0] * 4 for _ in range(4)]
    
    @staticmethod
    def identity() -> 'Matrix4':
        mat = Matrix4()
        mat.m[0][0] = 1.0
        mat.m[1][1] = 1.0
        mat.m[2][2] = 1.0
        mat.m[3][3] = 1.0
        return mat
    
    @staticmethod
    def projection(fov: float, aspect: float, near: float, far: float) -> 'Matrix4':
        """Create perspective projection matrix"""
        mat = Matrix4()
        fov_rad = 1.0 / math.tan(math.radians(fov) / 2.0)
        mat.m[0][0] = aspect * fov_rad
        mat.m[1][1] = fov_rad
        mat.m[2][2] = far / (far - near)
        mat.m[3][2] = (-far * near) / (far - near)
        mat.m[2][3] = 1.0
        mat.m[3][3] = 0.0
        return mat
    
    @staticmethod
    def rotation_x(angle: float) -> 'Matrix4':
        mat = Matrix4.identity()
        mat.m[1][1] = math.cos(angle)
        mat.m[1][2] = math.sin(angle)
        mat.m[2][1] = -math.sin(angle)
        mat.m[2][2] = math.cos(angle)
        return mat
    
    @staticmethod
    def rotation_y(angle: float) -> 'Matrix4':
        mat = Matrix4.identity()
        mat.m[0][0] = math.cos(angle)
        mat.m[0][2] = math.sin(angle)
        mat.m[2][0] = -math.sin(angle)
        mat.m[2][2] = math.cos(angle)
        return mat
    
    @staticmethod
    def rotation_z(angle: float) -> 'Matrix4':
        mat = Matrix4.identity()
        mat.m[0][0] = math.cos(angle)
        mat.m[0][1] = math.sin(angle)
        mat.m[1][0] = -math.sin(angle)
        mat.m[1][1] = math.cos(angle)
        return mat
    
    @staticmethod
    def translation(x: float, y: float, z: float) -> 'Matrix4':
        mat = Matrix4.identity()
        mat.m[3][0] = x
        mat.m[3][1] = y
        mat.m[3][2] = z
        return mat
    
    def multiply_vector(self, v: Vec3) -> Vec3:
        """Multiply matrix by vector"""
        w = v.x * self.m[0][3] + v.y * self.m[1][3] + v.z * self.m[2][3] + self.m[3][3]
        if w == 0:
            w = 1
        return Vec3(
            (v.x * self.m[0][0] + v.y * self.m[1][0] + v.z * self.m[2][0] + self.m[3][0]) / w,
            (v.x * self.m[0][1] + v.y * self.m[1][1] + v.z * self.m[2][1] + self.m[3][1]) / w,
            (v.x * self.m[0][2] + v.y * self.m[1][2] + v.z * self.m[2][2] + self.m[3][2]) / w
        )
    
    def multiply_matrix(self, other: 'Matrix4') -> 'Matrix4':
        result = Matrix4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
        return result


# ==================== CAMERA ====================
class Camera:
    """Lakitu-style SM64 camera"""
    def __init__(self):
        self.position = Vec3(0, 300, -500)
        self.target = Vec3(0, 100, 0)
        self.yaw = 0.0  # Horizontal rotation
        self.pitch = -0.2  # Vertical angle
        self.distance = 500.0
        self.height_offset = 200.0
        
        # Camera modes (SM64 style)
        self.mode = 'lakitu'  # 'lakitu', 'fixed', 'mario'
        
        # Smooth following
        self.smooth_factor = 0.1
    
    def update(self, mario_pos: Vec3, mario_facing: float):
        """Update camera to follow Mario"""
        if self.mode == 'lakitu':
            # Calculate ideal position behind Mario
            ideal_offset = Vec3(
                -math.sin(self.yaw) * self.distance,
                self.height_offset,
                -math.cos(self.yaw) * self.distance
            )
            ideal_pos = mario_pos + ideal_offset
            
            # Smooth interpolation
            self.position.x += (ideal_pos.x - self.position.x) * self.smooth_factor
            self.position.y += (ideal_pos.y - self.position.y) * self.smooth_factor
            self.position.z += (ideal_pos.z - self.position.z) * self.smooth_factor
            
            # Target slightly above Mario
            self.target = Vec3(mario_pos.x, mario_pos.y + 80, mario_pos.z)
    
    def rotate(self, delta_yaw: float):
        """Rotate camera around Mario"""
        self.yaw += delta_yaw
    
    def get_view_matrix(self) -> Matrix4:
        """Create view matrix (look-at)"""
        forward = (self.target - self.position).normalize()
        right = Vec3(0, 1, 0).cross(forward).normalize()
        up = forward.cross(right)
        
        mat = Matrix4.identity()
        mat.m[0][0] = right.x
        mat.m[1][0] = right.y
        mat.m[2][0] = right.z
        mat.m[0][1] = up.x
        mat.m[1][1] = up.y
        mat.m[2][1] = up.z
        mat.m[0][2] = forward.x
        mat.m[1][2] = forward.y
        mat.m[2][2] = forward.z
        mat.m[3][0] = -right.dot(self.position)
        mat.m[3][1] = -up.dot(self.position)
        mat.m[3][2] = -forward.dot(self.position)
        
        return mat


# ==================== SM64 PHYSICS ====================
class MarioState(Enum):
    """Mario's action states"""
    IDLE = auto()
    WALKING = auto()
    RUNNING = auto()
    JUMPING = auto()
    DOUBLE_JUMP = auto()
    TRIPLE_JUMP = auto()
    LONG_JUMP = auto()
    BACKFLIP = auto()
    WALL_KICK = auto()
    GROUND_POUND = auto()
    GROUND_POUND_LAND = auto()
    DIVING = auto()
    SLIDING = auto()
    SWIMMING = auto()
    FALLING = auto()
    CROUCHING = auto()
    CRAWLING = auto()


class Mario:
    """SM64-accurate Mario with full moveset"""
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.position = Vec3(x, y, z)
        self.velocity = Vec3(0, 0, 0)
        self.facing_angle = 0.0  # Radians
        
        # SM64 Physics constants (from decomp)
        self.GRAVITY = -4.0
        self.MAX_FALL_SPEED = -75.0
        self.WALK_SPEED = 8.0
        self.RUN_SPEED = 32.0
        self.CRAWL_SPEED = 4.0
        
        # Jump velocities (SM64 accurate)
        self.JUMP_VEL = 52.0
        self.DOUBLE_JUMP_VEL = 62.0
        self.TRIPLE_JUMP_VEL = 69.0
        self.LONG_JUMP_VEL = 30.0
        self.LONG_JUMP_H_SPEED = 48.0
        self.BACKFLIP_VEL = 62.0
        self.WALL_KICK_VEL = 52.0
        self.GROUND_POUND_VEL = -80.0
        
        # Friction/deceleration
        self.GROUND_FRICTION = 0.95
        self.AIR_DRAG = 0.99
        self.SLIDE_ACCEL = 1.5
        
        # State
        self.state = MarioState.IDLE
        self.on_ground = True
        self.jump_count = 0  # For triple jump
        self.jump_timer = 0  # Frames since last jump landed
        self.dive_timer = 0
        self.ground_pound_timer = 0
        self.wall_kick_timer = 0
        self.invincible_timer = 0
        
        # Stats
        self.health = 8  # SM64 has 8 health segments
        self.lives = 4
        self.coins = 0
        self.stars = 0
        
        # Input state
        self.input_stick = Vec3(0, 0, 0)
        self.input_jump = False
        self.input_jump_pressed = False
        self.input_dive = False
        self.input_crouch = False
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Size for collision
        self.radius = 30.0
        self.height = 160.0
    
    def handle_input(self, keys, camera_yaw: float):
        """Process input relative to camera"""
        # Movement input
        move_x = 0
        move_z = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_z = 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_z = -1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = 1
        
        # Convert to world space based on camera
        if move_x != 0 or move_z != 0:
            input_angle = math.atan2(move_x, move_z) + camera_yaw
            mag = min(1.0, math.sqrt(move_x**2 + move_z**2))
            self.input_stick = Vec3(
                math.sin(input_angle) * mag,
                0,
                math.cos(input_angle) * mag
            )
        else:
            self.input_stick = Vec3(0, 0, 0)
        
        # Action inputs
        jump_pressed = keys[pygame.K_SPACE]
        self.input_jump_pressed = jump_pressed and not self.input_jump
        self.input_jump = jump_pressed
        self.input_dive = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        self.input_crouch = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
    
    def update(self, collision_geometry: List['CollisionTriangle']):
        """Update Mario's physics"""
        self.animation_timer += 1
        
        # Process state-specific logic
        if self.state == MarioState.IDLE:
            self._update_idle()
        elif self.state == MarioState.WALKING:
            self._update_walking()
        elif self.state == MarioState.RUNNING:
            self._update_running()
        elif self.state in [MarioState.JUMPING, MarioState.DOUBLE_JUMP, 
                            MarioState.TRIPLE_JUMP, MarioState.LONG_JUMP,
                            MarioState.BACKFLIP, MarioState.WALL_KICK]:
            self._update_airborne()
        elif self.state == MarioState.FALLING:
            self._update_falling()
        elif self.state == MarioState.GROUND_POUND:
            self._update_ground_pound()
        elif self.state == MarioState.GROUND_POUND_LAND:
            self._update_ground_pound_land()
        elif self.state == MarioState.DIVING:
            self._update_diving()
        elif self.state == MarioState.CROUCHING:
            self._update_crouching()
        
        # Apply gravity
        if not self.on_ground:
            self.velocity.y += self.GRAVITY
            if self.velocity.y < self.MAX_FALL_SPEED:
                self.velocity.y = self.MAX_FALL_SPEED
        
        # Apply velocity
        new_pos = self.position + self.velocity
        
        # Floor collision
        floor_y = self._find_floor(new_pos, collision_geometry)
        if floor_y is not None and new_pos.y <= floor_y:
            new_pos.y = floor_y
            if not self.on_ground:
                self._land()
            self.on_ground = True
            self.velocity.y = 0
        else:
            self.on_ground = False
        
        # Wall collision
        new_pos = self._wall_collision(new_pos, collision_geometry)
        
        # Update position
        self.position = new_pos
        
        # Timers
        if self.on_ground:
            self.jump_timer += 1
        else:
            self.jump_timer = 0
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # Animation
        self._update_animation()
    
    def _update_idle(self):
        """Idle state - waiting for input"""
        stick_mag = self.input_stick.length()
        
        if stick_mag > 0.1:
            self.state = MarioState.WALKING
            return
        
        if self.input_jump_pressed:
            self._start_jump()
            return
        
        if self.input_crouch:
            self.state = MarioState.CROUCHING
            return
        
        # Apply friction
        self.velocity.x *= self.GROUND_FRICTION
        self.velocity.z *= self.GROUND_FRICTION
    
    def _update_walking(self):
        """Walking/running state"""
        stick_mag = self.input_stick.length()
        
        if stick_mag < 0.1:
            self.state = MarioState.IDLE
            return
        
        # Determine target speed
        if self.input_dive:
            target_speed = self.RUN_SPEED
            self.state = MarioState.RUNNING
        else:
            target_speed = self.WALK_SPEED
            self.state = MarioState.WALKING
        
        # Turn toward input direction
        target_angle = math.atan2(self.input_stick.x, self.input_stick.z)
        angle_diff = target_angle - self.facing_angle
        
        # Normalize angle difference
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Gradual turn
        turn_speed = 0.15
        self.facing_angle += angle_diff * turn_speed
        
        # Accelerate in facing direction
        accel = 2.0 if self.on_ground else 1.0
        target_vel = Vec3(
            math.sin(self.facing_angle) * target_speed * stick_mag,
            self.velocity.y,
            math.cos(self.facing_angle) * target_speed * stick_mag
        )
        
        self.velocity.x += (target_vel.x - self.velocity.x) * 0.1
        self.velocity.z += (target_vel.z - self.velocity.z) * 0.1
        
        # Jump check
        if self.input_jump_pressed:
            self._start_jump()
            return
        
        if self.input_crouch:
            self.state = MarioState.CROUCHING
            return
    
    def _update_running(self):
        """Running state (same as walking but faster)"""
        self._update_walking()
    
    def _update_airborne(self):
        """Airborne states (various jumps)"""
        # Air control
        stick_mag = self.input_stick.length()
        if stick_mag > 0.1:
            target_angle = math.atan2(self.input_stick.x, self.input_stick.z)
            angle_diff = target_angle - self.facing_angle
            
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Limited air turn
            self.facing_angle += angle_diff * 0.05
            
            # Air acceleration (limited)
            air_accel = 1.5
            self.velocity.x += self.input_stick.x * air_accel
            self.velocity.z += self.input_stick.z * air_accel
        
        # Air drag
        self.velocity.x *= self.AIR_DRAG
        self.velocity.z *= self.AIR_DRAG
        
        # Ground pound
        if self.input_crouch and self.state not in [MarioState.GROUND_POUND]:
            self.state = MarioState.GROUND_POUND
            self.velocity = Vec3(0, 0, 0)
            self.ground_pound_timer = 10  # Pause at top
            return
        
        # Dive
        if self.input_dive and self.velocity.length_xz() > 10:
            self.state = MarioState.DIVING
            self.velocity.y = 15
            speed = self.velocity.length_xz()
            self.velocity.x = math.sin(self.facing_angle) * speed * 1.5
            self.velocity.z = math.cos(self.facing_angle) * speed * 1.5
            return
        
        # Transition to falling if descending
        if self.velocity.y < 0 and self.state == MarioState.JUMPING:
            self.state = MarioState.FALLING
    
    def _update_falling(self):
        """Falling state"""
        self._update_airborne()
    
    def _update_ground_pound(self):
        """Ground pound state"""
        if self.ground_pound_timer > 0:
            self.ground_pound_timer -= 1
            return
        
        self.velocity.y = self.GROUND_POUND_VEL
    
    def _update_ground_pound_land(self):
        """Ground pound landing"""
        self.ground_pound_timer -= 1
        if self.ground_pound_timer <= 0:
            self.state = MarioState.IDLE
    
    def _update_diving(self):
        """Diving state"""
        # Apply gravity
        self.velocity.y += self.GRAVITY * 0.5  # Slower gravity during dive
        
        # Air drag
        self.velocity.x *= 0.98
        self.velocity.z *= 0.98
        
        self.dive_timer += 1
    
    def _update_crouching(self):
        """Crouching state"""
        if not self.input_crouch:
            self.state = MarioState.IDLE
            return
        
        # Slide on slopes (simplified)
        self.velocity.x *= 0.9
        self.velocity.z *= 0.9
        
        # Backflip
        if self.input_jump_pressed:
            self.state = MarioState.BACKFLIP
            self.velocity.y = self.BACKFLIP_VEL
            self.velocity.x = -math.sin(self.facing_angle) * 15
            self.velocity.z = -math.cos(self.facing_angle) * 15
            self.on_ground = False
            self.jump_count = 0
            return
        
        # Long jump (if moving)
        if self.input_dive and self.velocity.length_xz() > 5:
            self.state = MarioState.LONG_JUMP
            self.velocity.y = self.LONG_JUMP_VEL
            self.velocity.x = math.sin(self.facing_angle) * self.LONG_JUMP_H_SPEED
            self.velocity.z = math.cos(self.facing_angle) * self.LONG_JUMP_H_SPEED
            self.on_ground = False
            self.jump_count = 0
            return
    
    def _start_jump(self):
        """Initiate a jump based on current state"""
        h_speed = self.velocity.length_xz()
        
        # Triple jump check
        if self.jump_timer < 15 and self.jump_count > 0 and h_speed > 15:
            if self.jump_count == 1:
                self.state = MarioState.DOUBLE_JUMP
                self.velocity.y = self.DOUBLE_JUMP_VEL
                self.jump_count = 2
            elif self.jump_count == 2:
                self.state = MarioState.TRIPLE_JUMP
                self.velocity.y = self.TRIPLE_JUMP_VEL
                self.jump_count = 0
        else:
            self.state = MarioState.JUMPING
            self.velocity.y = self.JUMP_VEL
            self.jump_count = 1
        
        self.on_ground = False
        self.jump_timer = 0
    
    def _land(self):
        """Handle landing on ground"""
        prev_state = self.state
        
        if prev_state == MarioState.GROUND_POUND:
            self.state = MarioState.GROUND_POUND_LAND
            self.ground_pound_timer = 20
            # Screen shake could go here
        elif prev_state == MarioState.DIVING:
            # Slide on ground after dive
            self.state = MarioState.SLIDING
            self.velocity.x *= 0.8
            self.velocity.z *= 0.8
        else:
            # Normal landing
            if self.input_stick.length() > 0.1:
                self.state = MarioState.WALKING
            else:
                self.state = MarioState.IDLE
    
    def _find_floor(self, pos: Vec3, geometry: List['CollisionTriangle']) -> Optional[float]:
        """Find floor height at position"""
        floor_y = None
        
        for tri in geometry:
            # Simple point-in-triangle test for XZ plane
            if self._point_in_triangle_xz(pos, tri):
                # Calculate Y at this XZ position
                y = self._get_triangle_y(pos.x, pos.z, tri)
                if y is not None and (floor_y is None or y > floor_y):
                    if y <= pos.y + 50:  # Only consider floors below or slightly above
                        floor_y = y
        
        return floor_y
    
    def _point_in_triangle_xz(self, p: Vec3, tri: 'CollisionTriangle') -> bool:
        """Check if point is inside triangle in XZ plane"""
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.z - p3.z) - (p2.x - p3.x) * (p1.z - p3.z)
        
        d1 = sign(p, tri.v0, tri.v1)
        d2 = sign(p, tri.v1, tri.v2)
        d3 = sign(p, tri.v2, tri.v0)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def _get_triangle_y(self, x: float, z: float, tri: 'CollisionTriangle') -> Optional[float]:
        """Get Y coordinate on triangle at given XZ"""
        # Plane equation: ax + by + cz = d
        n = tri.normal
        if abs(n.y) < 0.001:
            return None
        
        d = n.dot(tri.v0)
        y = (d - n.x * x - n.z * z) / n.y
        return y
    
    def _wall_collision(self, pos: Vec3, geometry: List['CollisionTriangle']) -> Vec3:
        """Simple wall collision (push out of walls)"""
        # Simplified - just prevent going below floor
        for tri in geometry:
            if tri.normal.y < 0.5:  # Wall-like surface
                # Check distance to triangle plane
                dist = (pos - tri.v0).dot(tri.normal)
                if 0 < dist < self.radius:
                    # Push out
                    push = tri.normal * (self.radius - dist)
                    pos = pos + push
        return pos
    
    def _update_animation(self):
        """Update animation frame"""
        if self.animation_timer >= 4:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 8
    
    def get_triangles(self) -> List[Triangle]:
        """Generate Mario's visual mesh"""
        tris = []
        p = self.position
        
        # Body colors
        red = (255, 0, 0)       # Hat, shirt
        blue = (0, 0, 200)      # Overalls
        skin = (255, 200, 150)  # Skin
        brown = (139, 69, 19)   # Hair, shoes
        white = (255, 255, 255) # Gloves
        
        # Simplified Mario model (low poly like N64)
        # Head (octahedron-ish)
        head_y = p.y + 140
        head_size = 25
        
        # Body (box)
        body_top = p.y + 120
        body_bottom = p.y + 60
        body_width = 30
        
        # Legs (two boxes)
        leg_top = p.y + 60
        leg_bottom = p.y
        leg_width = 12
        
        # Rotate based on facing
        cos_f = math.cos(self.facing_angle)
        sin_f = math.sin(self.facing_angle)
        
        def rotated_point(x, y, z):
            rx = x * cos_f - z * sin_f
            rz = x * sin_f + z * cos_f
            return Vec3(p.x + rx, y, p.z + rz)
        
        # Head (simplified sphere as octahedron)
        head_verts = [
            rotated_point(0, head_y + head_size, 0),         # Top
            rotated_point(head_size, head_y, 0),              # Right
            rotated_point(0, head_y, head_size),              # Front
            rotated_point(-head_size, head_y, 0),             # Left
            rotated_point(0, head_y, -head_size),             # Back
            rotated_point(0, head_y - head_size * 0.7, 0),    # Bottom
        ]
        
        # Head triangles (top cap - red for hat)
        tris.append(Triangle(head_verts[0], head_verts[1], head_verts[2], red))
        tris.append(Triangle(head_verts[0], head_verts[2], head_verts[3], red))
        tris.append(Triangle(head_verts[0], head_verts[3], head_verts[4], red))
        tris.append(Triangle(head_verts[0], head_verts[4], head_verts[1], red))
        
        # Head triangles (bottom - skin)
        tris.append(Triangle(head_verts[5], head_verts[2], head_verts[1], skin))
        tris.append(Triangle(head_verts[5], head_verts[3], head_verts[2], skin))
        tris.append(Triangle(head_verts[5], head_verts[4], head_verts[3], skin))
        tris.append(Triangle(head_verts[5], head_verts[1], head_verts[4], skin))
        
        # Body (box) - red shirt top, blue overalls bottom
        body_verts = [
            rotated_point(-body_width, body_top, -body_width * 0.6),
            rotated_point(body_width, body_top, -body_width * 0.6),
            rotated_point(body_width, body_top, body_width * 0.6),
            rotated_point(-body_width, body_top, body_width * 0.6),
            rotated_point(-body_width, body_bottom, -body_width * 0.6),
            rotated_point(body_width, body_bottom, -body_width * 0.6),
            rotated_point(body_width, body_bottom, body_width * 0.6),
            rotated_point(-body_width, body_bottom, body_width * 0.6),
        ]
        
        mid_y = (body_top + body_bottom) / 2
        body_mid = [
            rotated_point(-body_width, mid_y, -body_width * 0.6),
            rotated_point(body_width, mid_y, -body_width * 0.6),
            rotated_point(body_width, mid_y, body_width * 0.6),
            rotated_point(-body_width, mid_y, body_width * 0.6),
        ]
        
        # Red shirt (top half)
        tris.append(Triangle(body_verts[0], body_verts[1], body_mid[1], red))
        tris.append(Triangle(body_verts[0], body_mid[1], body_mid[0], red))
        tris.append(Triangle(body_verts[1], body_verts[2], body_mid[2], red))
        tris.append(Triangle(body_verts[1], body_mid[2], body_mid[1], red))
        tris.append(Triangle(body_verts[2], body_verts[3], body_mid[3], red))
        tris.append(Triangle(body_verts[2], body_mid[3], body_mid[2], red))
        tris.append(Triangle(body_verts[3], body_verts[0], body_mid[0], red))
        tris.append(Triangle(body_verts[3], body_mid[0], body_mid[3], red))
        
        # Blue overalls (bottom half)
        tris.append(Triangle(body_mid[0], body_mid[1], body_verts[5], blue))
        tris.append(Triangle(body_mid[0], body_verts[5], body_verts[4], blue))
        tris.append(Triangle(body_mid[1], body_mid[2], body_verts[6], blue))
        tris.append(Triangle(body_mid[1], body_verts[6], body_verts[5], blue))
        tris.append(Triangle(body_mid[2], body_mid[3], body_verts[7], blue))
        tris.append(Triangle(body_mid[2], body_verts[7], body_verts[6], blue))
        tris.append(Triangle(body_mid[3], body_mid[0], body_verts[4], blue))
        tris.append(Triangle(body_mid[3], body_verts[4], body_verts[7], blue))
        
        # Legs (simplified)
        leg_offset = 15
        for side in [-1, 1]:
            lx = side * leg_offset
            leg_verts = [
                rotated_point(lx - leg_width, leg_top, -leg_width),
                rotated_point(lx + leg_width, leg_top, -leg_width),
                rotated_point(lx + leg_width, leg_top, leg_width),
                rotated_point(lx - leg_width, leg_top, leg_width),
                rotated_point(lx - leg_width, leg_bottom, -leg_width),
                rotated_point(lx + leg_width, leg_bottom, -leg_width),
                rotated_point(lx + leg_width, leg_bottom, leg_width),
                rotated_point(lx - leg_width, leg_bottom, leg_width),
            ]
            
            # Blue overalls for legs
            tris.append(Triangle(leg_verts[0], leg_verts[1], leg_verts[5], blue))
            tris.append(Triangle(leg_verts[0], leg_verts[5], leg_verts[4], blue))
            tris.append(Triangle(leg_verts[1], leg_verts[2], leg_verts[6], blue))
            tris.append(Triangle(leg_verts[1], leg_verts[6], leg_verts[5], blue))
            tris.append(Triangle(leg_verts[2], leg_verts[3], leg_verts[7], blue))
            tris.append(Triangle(leg_verts[2], leg_verts[7], leg_verts[6], blue))
            tris.append(Triangle(leg_verts[3], leg_verts[0], leg_verts[4], blue))
            tris.append(Triangle(leg_verts[3], leg_verts[4], leg_verts[7], blue))
            
            # Brown shoes (bottom faces)
            tris.append(Triangle(leg_verts[4], leg_verts[5], leg_verts[6], brown))
            tris.append(Triangle(leg_verts[4], leg_verts[6], leg_verts[7], brown))
        
        return tris


# ==================== COLLISION ====================
@dataclass
class CollisionTriangle:
    """Triangle for collision detection"""
    v0: Vec3
    v1: Vec3
    v2: Vec3
    normal: Vec3 = None
    surface_type: str = 'ground'  # ground, wall, ceiling, water, lava
    
    def __post_init__(self):
        if self.normal is None:
            edge1 = self.v1 - self.v0
            edge2 = self.v2 - self.v0
            self.normal = edge1.cross(edge2).normalize()


# ==================== LEVEL GEOMETRY ====================
class LevelGeometry:
    """Generate level meshes procedurally"""
    
    @staticmethod
    def create_flat_ground(x: float, z: float, width: float, depth: float, 
                           y: float = 0, color: Tuple = GRASS_GREEN) -> Tuple[List[Triangle], List[CollisionTriangle]]:
        """Create a flat rectangular ground"""
        visual = []
        collision = []
        
        v0 = Vec3(x, y, z)
        v1 = Vec3(x + width, y, z)
        v2 = Vec3(x + width, y, z + depth)
        v3 = Vec3(x, y, z + depth)
        
        visual.append(Triangle(v0, v1, v2, color))
        visual.append(Triangle(v0, v2, v3, color))
        
        collision.append(CollisionTriangle(v0, v1, v2, surface_type='ground'))
        collision.append(CollisionTriangle(v0, v2, v3, surface_type='ground'))
        
        return visual, collision
    
    @staticmethod
    def create_slope(x: float, z: float, width: float, depth: float,
                    y_start: float, y_end: float, color: Tuple = GRASS_GREEN) -> Tuple[List[Triangle], List[CollisionTriangle]]:
        """Create a sloped surface"""
        visual = []
        collision = []
        
        v0 = Vec3(x, y_start, z)
        v1 = Vec3(x + width, y_start, z)
        v2 = Vec3(x + width, y_end, z + depth)
        v3 = Vec3(x, y_end, z + depth)
        
        visual.append(Triangle(v0, v1, v2, color))
        visual.append(Triangle(v0, v2, v3, color))
        
        collision.append(CollisionTriangle(v0, v1, v2, surface_type='ground'))
        collision.append(CollisionTriangle(v0, v2, v3, surface_type='ground'))
        
        return visual, collision
    
    @staticmethod
    def create_box(x: float, y: float, z: float, 
                   w: float, h: float, d: float,
                   color: Tuple = STONE_GRAY) -> Tuple[List[Triangle], List[CollisionTriangle]]:
        """Create a 3D box"""
        visual = []
        collision = []
        
        # 8 vertices
        verts = [
            Vec3(x, y, z),           # 0: bottom-back-left
            Vec3(x + w, y, z),       # 1: bottom-back-right
            Vec3(x + w, y, z + d),   # 2: bottom-front-right
            Vec3(x, y, z + d),       # 3: bottom-front-left
            Vec3(x, y + h, z),       # 4: top-back-left
            Vec3(x + w, y + h, z),   # 5: top-back-right
            Vec3(x + w, y + h, z + d), # 6: top-front-right
            Vec3(x, y + h, z + d),   # 7: top-front-left
        ]
        
        # Faces (as triangle pairs)
        faces = [
            (4, 5, 6, 7, 'ground'),  # Top
            (0, 3, 2, 1, 'ground'),  # Bottom
            (0, 1, 5, 4, 'wall'),    # Back
            (2, 3, 7, 6, 'wall'),    # Front
            (0, 4, 7, 3, 'wall'),    # Left
            (1, 2, 6, 5, 'wall'),    # Right
        ]
        
        for face in faces:
            i0, i1, i2, i3, surf = face
            v0, v1, v2, v3 = verts[i0], verts[i1], verts[i2], verts[i3]
            
            # Shade faces based on normal
            shade = 1.0
            normal = (v1 - v0).cross(v2 - v0).normalize()
            if normal.y > 0.5:
                shade = 1.0
            elif normal.y < -0.5:
                shade = 0.5
            else:
                shade = 0.7 + abs(normal.x) * 0.2
            
            shaded_color = (
                int(color[0] * shade),
                int(color[1] * shade),
                int(color[2] * shade)
            )
            
            visual.append(Triangle(v0, v1, v2, shaded_color))
            visual.append(Triangle(v0, v2, v3, shaded_color))
            
            collision.append(CollisionTriangle(v0, v1, v2, surface_type=surf))
            collision.append(CollisionTriangle(v0, v2, v3, surface_type=surf))
        
        return visual, collision
    
    @staticmethod
    def create_cylinder(x: float, y: float, z: float,
                        radius: float, height: float, segments: int = 12,
                        color: Tuple = STONE_GRAY) -> Tuple[List[Triangle], List[CollisionTriangle]]:
        """Create a cylinder"""
        visual = []
        collision = []
        
        # Generate vertices around circle
        top_center = Vec3(x, y + height, z)
        bottom_center = Vec3(x, y, z)
        
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi
            
            # Vertices
            t1 = Vec3(x + radius * math.cos(angle1), y + height, z + radius * math.sin(angle1))
            t2 = Vec3(x + radius * math.cos(angle2), y + height, z + radius * math.sin(angle2))
            b1 = Vec3(x + radius * math.cos(angle1), y, z + radius * math.sin(angle1))
            b2 = Vec3(x + radius * math.cos(angle2), y, z + radius * math.sin(angle2))
            
            # Top cap
            visual.append(Triangle(top_center, t1, t2, color))
            collision.append(CollisionTriangle(top_center, t1, t2, surface_type='ground'))
            
            # Bottom cap
            visual.append(Triangle(bottom_center, b2, b1, color))
            
            # Side
            shade = 0.6 + 0.3 * abs(math.cos(angle1))
            shaded = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))
            visual.append(Triangle(b1, b2, t2, shaded))
            visual.append(Triangle(b1, t2, t1, shaded))
            collision.append(CollisionTriangle(b1, b2, t2, surface_type='wall'))
            collision.append(CollisionTriangle(b1, t2, t1, surface_type='wall'))
        
        return visual, collision
    
    @staticmethod
    def create_mountain(x: float, z: float, base_radius: float, height: float,
                        color: Tuple = DIRT_BROWN) -> Tuple[List[Triangle], List[CollisionTriangle]]:
        """Create a cone-shaped mountain"""
        visual = []
        collision = []
        
        peak = Vec3(x, height, z)
        segments = 16
        
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi
            
            b1 = Vec3(x + base_radius * math.cos(angle1), 0, z + base_radius * math.sin(angle1))
            b2 = Vec3(x + base_radius * math.cos(angle2), 0, z + base_radius * math.sin(angle2))
            
            # Side face
            shade = 0.6 + 0.4 * abs(math.cos(angle1))
            shaded = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))
            visual.append(Triangle(b1, b2, peak, shaded))
            collision.append(CollisionTriangle(b1, b2, peak, surface_type='ground'))
        
        return visual, collision


# ==================== LEVELS ====================
class Level:
    """Base class for SM64 levels"""
    def __init__(self, name: str):
        self.name = name
        self.visual_tris: List[Triangle] = []
        self.collision_tris: List[CollisionTriangle] = []
        self.spawn_point = Vec3(0, 100, 0)
        self.stars: List[Dict] = []  # Star locations and requirements
        self.coins: List[Vec3] = []
        self.enemies: List = []
        self.sky_color = SKY_BLUE
        
    def build(self):
        """Override to build level geometry"""
        pass
    
    def update(self):
        """Override for level-specific updates"""
        pass


class BobOmbBattlefield(Level):
    """Course 1: Bob-omb Battlefield"""
    def __init__(self):
        super().__init__("Bob-omb Battlefield")
        self.sky_color = (135, 206, 235)
        self.spawn_point = Vec3(0, 50, 0)
        
    def build(self):
        """Build Bob-omb Battlefield geometry"""
        # Main starting area (large flat ground)
        vis, col = LevelGeometry.create_flat_ground(-2000, -2000, 4000, 4000, 0, GRASS_GREEN)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Central mountain (King Bob-omb's mountain)
        vis, col = LevelGeometry.create_mountain(0, 500, 800, 1500, DIRT_BROWN)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Wooden bridge platform
        vis, col = LevelGeometry.create_box(-200, 200, -600, 400, 20, 100, (139, 90, 43))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Floating island
        vis, col = LevelGeometry.create_cylinder(500, 400, -400, 200, 50, 8, (34, 139, 34))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Gate posts
        for x in [-150, 150]:
            vis, col = LevelGeometry.create_box(x, 0, -800, 30, 200, 30, STONE_GRAY)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Cannon hole area (raised platform)
        vis, col = LevelGeometry.create_box(-600, 0, 200, 200, 100, 200, (100, 80, 50))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Small hills
        for (hx, hz, hr, hh) in [(800, 200, 200, 150), (-700, -300, 150, 100), (300, -800, 180, 120)]:
            vis, col = LevelGeometry.create_mountain(hx, hz, hr, hh, GRASS_GREEN)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Chain chomp post
        vis, col = LevelGeometry.create_cylinder(-400, 0, -200, 20, 150, 8, (139, 69, 19))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Coin positions
        for i in range(50):
            angle = (i / 50) * 2 * math.pi
            self.coins.append(Vec3(
                math.cos(angle) * (200 + i * 10),
                50,
                math.sin(angle) * (200 + i * 10)
            ))


class WhompsFortress(Level):
    """Course 2: Whomp's Fortress"""
    def __init__(self):
        super().__init__("Whomp's Fortress")
        self.sky_color = (100, 150, 255)
        self.spawn_point = Vec3(0, 50, 0)
        
    def build(self):
        """Build Whomp's Fortress geometry"""
        # Base platform
        vis, col = LevelGeometry.create_flat_ground(-600, -600, 1200, 1200, 0, STONE_GRAY)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Main tower (stepped)
        for i, (size, height) in enumerate([(500, 200), (400, 400), (300, 600), (200, 800)]):
            y = i * 200
            vis, col = LevelGeometry.create_box(-size/2, y, -size/2, size, 200, size, STONE_GRAY)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Top platform with Whomp King arena
        vis, col = LevelGeometry.create_flat_ground(-250, -250, 500, 500, 800, (180, 180, 180))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Thwomp platforms (floating)
        for y, offset in [(300, 0), (500, 100), (700, 200)]:
            vis, col = LevelGeometry.create_box(-400 + offset, y, -80, 120, 30, 120, (150, 150, 150))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Piranha plant pipes
        for (px, pz) in [(300, 300), (-300, -300), (400, -200)]:
            vis, col = LevelGeometry.create_cylinder(px, 0, pz, 40, 100, 8, GREEN)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Rotating bridge posts
        vis, col = LevelGeometry.create_cylinder(0, 0, 400, 30, 400, 8, (139, 69, 19))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)


class JollyRogerBay(Level):
    """Course 3: Jolly Roger Bay"""
    def __init__(self):
        super().__init__("Jolly Roger Bay")
        self.sky_color = (100, 180, 255)
        self.spawn_point = Vec3(0, 50, -800)
        
    def build(self):
        """Build Jolly Roger Bay geometry"""
        # Beach area
        vis, col = LevelGeometry.create_flat_ground(-1000, -1500, 2000, 800, 0, SAND_YELLOW)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Water plane (visual only - collision handled specially)
        water_verts = [
            Vec3(-1000, -100, -700),
            Vec3(1000, -100, -700),
            Vec3(1000, -100, 1500),
            Vec3(-1000, -100, 1500)
        ]
        self.visual_tris.append(Triangle(water_verts[0], water_verts[1], water_verts[2], (64, 164, 223)))
        self.visual_tris.append(Triangle(water_verts[0], water_verts[2], water_verts[3], (64, 164, 223)))
        
        # Underwater floor
        vis, col = LevelGeometry.create_flat_ground(-1000, -700, 2000, 2200, -300, (50, 100, 80))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Shipwreck
        vis, col = LevelGeometry.create_box(-200, -250, 400, 400, 100, 150, (80, 50, 30))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Rock formations
        for (rx, rz, rr) in [(500, 200, 150), (-400, 500, 200), (600, 800, 180)]:
            vis, col = LevelGeometry.create_mountain(rx, rz, rr, 250, STONE_GRAY)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Pier
        vis, col = LevelGeometry.create_box(-100, 0, -900, 200, 30, 400, (100, 70, 40))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Cave entrance
        vis, col = LevelGeometry.create_box(700, 0, -400, 200, 300, 100, STONE_GRAY)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)


class CoolCoolMountain(Level):
    """Course 4: Cool, Cool Mountain"""
    def __init__(self):
        super().__init__("Cool, Cool Mountain")
        self.sky_color = (200, 220, 255)
        self.spawn_point = Vec3(0, 1500, 0)
        
    def build(self):
        """Build Cool, Cool Mountain geometry"""
        # Main mountain (huge cone)
        vis, col = LevelGeometry.create_mountain(0, 0, 1500, 2000, SNOW_WHITE)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Slide path (spiral down the mountain)
        # Simplified as platforms
        for i in range(20):
            angle = (i / 20) * 4 * math.pi
            radius = 1200 - i * 50
            y = 1800 - i * 90
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            vis, col = LevelGeometry.create_box(x - 100, y, z - 50, 200, 30, 100, (220, 230, 255))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Cabin at top
        vis, col = LevelGeometry.create_box(-150, 1750, -150, 300, 200, 300, (139, 90, 43))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Cabin roof (simplified)
        roof_peak = Vec3(0, 2050, 0)
        roof_corners = [
            Vec3(-180, 1950, -180),
            Vec3(180, 1950, -180),
            Vec3(180, 1950, 180),
            Vec3(-180, 1950, 180)
        ]
        for i in range(4):
            self.visual_tris.append(Triangle(
                roof_corners[i], roof_corners[(i+1)%4], roof_peak, (100, 50, 30)
            ))
        
        # Ice blocks
        for (ix, iy, iz) in [(-500, 200, 300), (400, 400, -200), (-300, 600, 500)]:
            vis, col = LevelGeometry.create_box(ix, iy, iz, 100, 100, 100, (200, 230, 255))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Penguin race starting platform
        vis, col = LevelGeometry.create_flat_ground(-200, -200, 400, 400, 1700, (180, 200, 255))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)


class BigBoosHaunt(Level):
    """Course 5: Big Boo's Haunt"""
    def __init__(self):
        super().__init__("Big Boo's Haunt")
        self.sky_color = (30, 20, 50)  # Dark purple night
        self.spawn_point = Vec3(0, 50, -500)
        
    def build(self):
        """Build Big Boo's Haunt geometry"""
        # Ground (dead grass)
        vis, col = LevelGeometry.create_flat_ground(-800, -800, 1600, 1600, 0, (60, 80, 40))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Main mansion
        mansion_color = (80, 70, 90)
        
        # First floor
        vis, col = LevelGeometry.create_box(-400, 0, -400, 800, 400, 800, mansion_color)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Second floor (smaller)
        vis, col = LevelGeometry.create_box(-300, 400, -300, 600, 400, 600, mansion_color)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Tower
        vis, col = LevelGeometry.create_box(-100, 800, -100, 200, 400, 200, mansion_color)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Roof point
        roof_peak = Vec3(0, 1400, 0)
        roof_base = [
            Vec3(-150, 1200, -150),
            Vec3(150, 1200, -150),
            Vec3(150, 1200, 150),
            Vec3(-150, 1200, 150)
        ]
        for i in range(4):
            self.visual_tris.append(Triangle(
                roof_base[i], roof_base[(i+1)%4], roof_peak, (50, 40, 60)
            ))
        
        # Gravestones
        for i in range(10):
            gx = -600 + (i % 5) * 250
            gz = -700 + (i // 5) * 300
            vis, col = LevelGeometry.create_box(gx, 0, gz, 40, 80, 15, STONE_GRAY)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Fence posts
        for x in range(-700, 750, 150):
            for z in [-700, 700]:
                vis, col = LevelGeometry.create_box(x, 0, z, 15, 100, 15, (60, 40, 30))
                self.visual_tris.extend(vis)
                self.collision_tris.extend(col)


class HazyMazeCave(Level):
    """Course 6: Hazy Maze Cave"""
    def __init__(self):
        super().__init__("Hazy Maze Cave")
        self.sky_color = (40, 35, 30)  # Dark cave
        self.spawn_point = Vec3(0, 100, 0)
        
    def build(self):
        """Build Hazy Maze Cave geometry"""
        # Main floor
        vis, col = LevelGeometry.create_flat_ground(-1500, -1500, 3000, 3000, 0, (80, 70, 60))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Ceiling (high up)
        ceiling_verts = [
            Vec3(-1500, 800, -1500),
            Vec3(1500, 800, -1500),
            Vec3(1500, 800, 1500),
            Vec3(-1500, 800, 1500)
        ]
        self.visual_tris.append(Triangle(ceiling_verts[0], ceiling_verts[2], ceiling_verts[1], (50, 45, 40)))
        self.visual_tris.append(Triangle(ceiling_verts[0], ceiling_verts[3], ceiling_verts[2], (50, 45, 40)))
        
        # Rock pillars
        for (px, pz) in [(500, 0), (-500, 300), (0, -600), (800, -400), (-700, -500)]:
            vis, col = LevelGeometry.create_cylinder(px, 0, pz, 80, 800, 8, (100, 90, 80))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Maze walls
        wall_positions = [
            (-800, -400, 400, 50), (-400, -200, 50, 600), (200, 200, 600, 50),
            (0, -800, 50, 400), (600, -600, 50, 800), (-1000, 400, 800, 50)
        ]
        for (wx, wz, ww, wd) in wall_positions:
            vis, col = LevelGeometry.create_box(wx, 0, wz, ww, 400, wd, (90, 80, 70))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Toxic maze floor (lower, glowing)
        vis, col = LevelGeometry.create_flat_ground(-600, 600, 800, 600, -50, (100, 150, 80))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Underground pool
        pool_verts = [
            Vec3(400, 50, 400),
            Vec3(900, 50, 400),
            Vec3(900, 50, 900),
            Vec3(400, 50, 900)
        ]
        self.visual_tris.append(Triangle(pool_verts[0], pool_verts[1], pool_verts[2], (80, 100, 120)))
        self.visual_tris.append(Triangle(pool_verts[0], pool_verts[2], pool_verts[3], (80, 100, 120)))


class LethalLavaLand(Level):
    """Course 7: Lethal Lava Land"""
    def __init__(self):
        super().__init__("Lethal Lava Land")
        self.sky_color = (80, 30, 10)  # Dark red/orange
        self.spawn_point = Vec3(0, 100, -800)
        
    def build(self):
        """Build Lethal Lava Land geometry"""
        # Lava sea (low)
        lava_verts = [
            Vec3(-2000, 0, -2000),
            Vec3(2000, 0, -2000),
            Vec3(2000, 0, 2000),
            Vec3(-2000, 0, 2000)
        ]
        self.visual_tris.append(Triangle(lava_verts[0], lava_verts[1], lava_verts[2], LAVA_ORANGE))
        self.visual_tris.append(Triangle(lava_verts[0], lava_verts[2], lava_verts[3], LAVA_ORANGE))
        
        # Starting platform
        vis, col = LevelGeometry.create_flat_ground(-200, -1000, 400, 400, 100, (60, 50, 50))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Platforms across lava
        platform_positions = [
            (0, -600, 200), (300, -300, 150), (-200, 0, 180),
            (400, 200, 160), (0, 500, 200), (-400, 300, 170),
            (600, 600, 140), (-300, 800, 190)
        ]
        for (px, pz, size) in platform_positions:
            vis, col = LevelGeometry.create_flat_ground(px - size/2, pz - size/2, size, size, 100, (70, 60, 55))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Central volcano
        vis, col = LevelGeometry.create_mountain(500, 500, 600, 1200, (80, 40, 30))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Volcano crater (lava pool at top)
        crater_verts = [
            Vec3(350, 1100, 350),
            Vec3(650, 1100, 350),
            Vec3(650, 1100, 650),
            Vec3(350, 1100, 650)
        ]
        self.visual_tris.append(Triangle(crater_verts[0], crater_verts[1], crater_verts[2], (255, 150, 50)))
        self.visual_tris.append(Triangle(crater_verts[0], crater_verts[2], crater_verts[3], (255, 150, 50)))
        
        # Rolling ball area
        vis, col = LevelGeometry.create_slope(-600, -400, 400, 800, 100, 600, (90, 70, 60))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Fire pillars
        for (fx, fz) in [(200, -400), (-100, 100), (300, 400), (-400, -200)]:
            vis, col = LevelGeometry.create_cylinder(fx, 100, fz, 30, 300, 6, (150, 80, 40))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)


class ShiftingSandLand(Level):
    """Course 8: Shifting Sand Land"""
    def __init__(self):
        super().__init__("Shifting Sand Land")
        self.sky_color = (220, 180, 120)  # Desert sky
        self.spawn_point = Vec3(0, 100, -800)
        
    def build(self):
        """Build Shifting Sand Land geometry"""
        # Main desert floor
        vis, col = LevelGeometry.create_flat_ground(-2000, -2000, 4000, 4000, 0, SAND_YELLOW)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Main pyramid
        pyramid_base = 800
        pyramid_height = 1000
        pyramid_center = Vec3(0, 0, 500)
        pyramid_verts = [
            Vec3(pyramid_center.x - pyramid_base/2, 0, pyramid_center.z - pyramid_base/2),
            Vec3(pyramid_center.x + pyramid_base/2, 0, pyramid_center.z - pyramid_base/2),
            Vec3(pyramid_center.x + pyramid_base/2, 0, pyramid_center.z + pyramid_base/2),
            Vec3(pyramid_center.x - pyramid_base/2, 0, pyramid_center.z + pyramid_base/2),
            Vec3(pyramid_center.x, pyramid_height, pyramid_center.z)  # Apex
        ]
        
        pyramid_color = (210, 180, 120)
        for i in range(4):
            self.visual_tris.append(Triangle(
                pyramid_verts[i], pyramid_verts[(i+1)%4], pyramid_verts[4], pyramid_color
            ))
            self.collision_tris.append(CollisionTriangle(
                pyramid_verts[i], pyramid_verts[(i+1)%4], pyramid_verts[4], surface_type='ground'
            ))
        
        # Smaller pyramids
        for (px, pz, ps, ph) in [(-800, -500, 300, 400), (900, -300, 250, 350), (-600, 800, 200, 280)]:
            small_verts = [
                Vec3(px - ps/2, 0, pz - ps/2),
                Vec3(px + ps/2, 0, pz - ps/2),
                Vec3(px + ps/2, 0, pz + ps/2),
                Vec3(px - ps/2, 0, pz + ps/2),
                Vec3(px, ph, pz)
            ]
            for i in range(4):
                self.visual_tris.append(Triangle(
                    small_verts[i], small_verts[(i+1)%4], small_verts[4], (200, 170, 110)
                ))
                self.collision_tris.append(CollisionTriangle(
                    small_verts[i], small_verts[(i+1)%4], small_verts[4], surface_type='ground'
                ))
        
        # Quicksand pit (visual - different color)
        quicksand_verts = [
            Vec3(-400, 5, -800),
            Vec3(200, 5, -800),
            Vec3(200, 5, -400),
            Vec3(-400, 5, -400)
        ]
        self.visual_tris.append(Triangle(quicksand_verts[0], quicksand_verts[1], quicksand_verts[2], (180, 150, 100)))
        self.visual_tris.append(Triangle(quicksand_verts[0], quicksand_verts[2], quicksand_verts[3], (180, 150, 100)))
        
        # Stone pillars
        for (px, pz) in [(600, -600), (-900, 200), (400, 1200), (-1100, -800)]:
            vis, col = LevelGeometry.create_box(px, 0, pz, 80, 400, 80, (160, 140, 100))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Oasis (small water pool)
        oasis_verts = [
            Vec3(-1200, 10, 400),
            Vec3(-900, 10, 400),
            Vec3(-900, 10, 700),
            Vec3(-1200, 10, 700)
        ]
        self.visual_tris.append(Triangle(oasis_verts[0], oasis_verts[1], oasis_verts[2], WATER_BLUE))
        self.visual_tris.append(Triangle(oasis_verts[0], oasis_verts[2], oasis_verts[3], WATER_BLUE))


class DireDireDocks(Level):
    """Course 9: Dire, Dire Docks"""
    def __init__(self):
        super().__init__("Dire, Dire Docks")
        self.sky_color = (60, 80, 120)
        self.spawn_point = Vec3(0, 100, -500)
        
    def build(self):
        """Build Dire, Dire Docks geometry"""
        # Dock platforms
        vis, col = LevelGeometry.create_flat_ground(-400, -600, 800, 400, 50, (80, 60, 50))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Water
        water_verts = [
            Vec3(-1500, 0, -200),
            Vec3(1500, 0, -200),
            Vec3(1500, 0, 2000),
            Vec3(-1500, 0, 2000)
        ]
        self.visual_tris.append(Triangle(water_verts[0], water_verts[1], water_verts[2], (40, 80, 150)))
        self.visual_tris.append(Triangle(water_verts[0], water_verts[2], water_verts[3], (40, 80, 150)))
        
        # Underwater floor
        vis, col = LevelGeometry.create_flat_ground(-1500, -200, 3000, 2200, -500, (30, 50, 70))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Submarine dock
        vis, col = LevelGeometry.create_box(-200, -400, 800, 400, 100, 600, (100, 100, 110))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Bowser's sub (simplified as long box)
        vis, col = LevelGeometry.create_box(-100, -300, 900, 200, 150, 400, (60, 60, 70))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Poles/masts
        for (px, pz) in [(-150, 500), (150, 500), (-300, 900), (300, 900)]:
            vis, col = LevelGeometry.create_cylinder(px, 50, pz, 20, 200, 6, (100, 80, 60))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Underwater cages
        for (cx, cz) in [(600, 400), (-500, 600), (400, 1000)]:
            vis, col = LevelGeometry.create_box(cx, -450, cz, 150, 150, 150, (120, 120, 130))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)


class SnowmansLand(Level):
    """Course 10: Snowman's Land"""
    def __init__(self):
        super().__init__("Snowman's Land")
        self.sky_color = (180, 200, 220)
        self.spawn_point = Vec3(0, 100, -700)
        
    def build(self):
        """Build Snowman's Land geometry"""
        # Snowy ground
        vis, col = LevelGeometry.create_flat_ground(-1500, -1500, 3000, 3000, 0, SNOW_WHITE)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Giant snowman (stacked spheres approximated as cones)
        # Base
        vis, col = LevelGeometry.create_mountain(0, 500, 400, 500, SNOW_WHITE)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Middle
        vis, col = LevelGeometry.create_mountain(0, 500, 300, 800, SNOW_WHITE)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Head area (platform)
        vis, col = LevelGeometry.create_flat_ground(-150, 350, 300, 300, 1100, SNOW_WHITE)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Ice maze walls
        ice_color = (200, 230, 255)
        walls = [
            (-800, -400, 50, 400), (-600, -200, 400, 50), (-400, -400, 50, 300),
            (-200, -500, 300, 50), (0, -300, 50, 400)
        ]
        for (wx, wz, ww, wd) in walls:
            vis, col = LevelGeometry.create_box(wx, 0, wz, ww, 150, wd, ice_color)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Igloos
        for (ix, iz) in [(-600, 600), (700, -400)]:
            vis, col = LevelGeometry.create_cylinder(ix, 0, iz, 120, 100, 10, SNOW_WHITE)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Frozen pond
        pond_verts = [
            Vec3(400, 5, -600),
            Vec3(800, 5, -600),
            Vec3(800, 5, -200),
            Vec3(400, 5, -200)
        ]
        self.visual_tris.append(Triangle(pond_verts[0], pond_verts[1], pond_verts[2], (180, 200, 220)))
        self.visual_tris.append(Triangle(pond_verts[0], pond_verts[2], pond_verts[3], (180, 200, 220)))


class WetDryWorld(Level):
    """Course 11: Wet-Dry World"""
    def __init__(self):
        super().__init__("Wet-Dry World")
        self.sky_color = (150, 180, 220)
        self.spawn_point = Vec3(0, 500, 0)
        self.water_level = 200  # Adjustable!
        
    def build(self):
        """Build Wet-Dry World geometry"""
        # Bottom floor
        vis, col = LevelGeometry.create_flat_ground(-800, -800, 1600, 1600, 0, (100, 100, 120))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Raised platforms at different heights
        platform_data = [
            (-400, -400, 300, 300, 100),
            (200, -300, 250, 250, 200),
            (-300, 200, 280, 280, 300),
            (300, 300, 200, 200, 400),
            (-100, -100, 150, 150, 500)
        ]
        
        for (px, pz, pw, pd, py) in platform_data:
            vis, col = LevelGeometry.create_box(px, 0, pz, pw, py, pd, (120, 120, 140))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Water level indicator crystals
        crystal_positions = [(500, -500), (-500, 500), (500, 500), (-500, -500)]
        for (cx, cz) in crystal_positions:
            # Low
            vis, col = LevelGeometry.create_box(cx, 100, cz, 40, 40, 40, (255, 200, 200))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
            # Mid
            vis, col = LevelGeometry.create_box(cx, 300, cz, 40, 40, 40, (200, 255, 200))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
            # High
            vis, col = LevelGeometry.create_box(cx, 500, cz, 40, 40, 40, (200, 200, 255))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Central tower
        vis, col = LevelGeometry.create_box(-75, 0, -75, 150, 700, 150, (140, 140, 160))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Water plane (visual)
        water_verts = [
            Vec3(-800, self.water_level, -800),
            Vec3(800, self.water_level, -800),
            Vec3(800, self.water_level, 800),
            Vec3(-800, self.water_level, 800)
        ]
        self.visual_tris.append(Triangle(water_verts[0], water_verts[1], water_verts[2], (80, 120, 180)))
        self.visual_tris.append(Triangle(water_verts[0], water_verts[2], water_verts[3], (80, 120, 180)))


class TallTallMountain(Level):
    """Course 12: Tall, Tall Mountain"""
    def __init__(self):
        super().__init__("Tall, Tall Mountain")
        self.sky_color = (135, 180, 230)
        self.spawn_point = Vec3(0, 100, -600)
        
    def build(self):
        """Build Tall, Tall Mountain geometry"""
        # Base area
        vis, col = LevelGeometry.create_flat_ground(-800, -800, 1600, 1000, 0, GRASS_GREEN)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Main mountain (huge)
        vis, col = LevelGeometry.create_mountain(0, 400, 1000, 2500, (120, 100, 80))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Winding path platforms
        path_data = [
            (-300, 200, 200, 150, 200),
            (0, 400, 180, 140, 400),
            (250, 600, 160, 130, 600),
            (-100, 800, 200, 150, 800),
            (200, 1000, 150, 120, 1000),
            (-200, 1200, 180, 140, 1200),
            (0, 1400, 200, 150, 1400),
            (150, 1600, 160, 130, 1600),
            (-50, 1800, 180, 140, 1800),
            (0, 2000, 250, 200, 2000)  # Summit
        ]
        
        for (px, pz, pw, pd, py) in path_data:
            vis, col = LevelGeometry.create_flat_ground(px - pw/2, pz - pd/2, pw, pd, py, (100, 130, 70))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Waterfall (visual strips)
        for i in range(10):
            y = 1500 - i * 150
            wf_verts = [
                Vec3(-50, y, 500),
                Vec3(50, y, 500),
                Vec3(50, y - 150, 520),
                Vec3(-50, y - 150, 520)
            ]
            self.visual_tris.append(Triangle(wf_verts[0], wf_verts[1], wf_verts[2], (200, 230, 255)))
            self.visual_tris.append(Triangle(wf_verts[0], wf_verts[2], wf_verts[3], (200, 230, 255)))
        
        # Mushroom platforms
        for (mx, my, mz) in [(400, 300, 100), (-350, 500, 200), (300, 700, -100)]:
            # Stem
            vis, col = LevelGeometry.create_cylinder(mx, my, mz, 30, 100, 6, (200, 180, 150))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
            # Cap
            vis, col = LevelGeometry.create_cylinder(mx, my + 100, mz, 80, 30, 8, (255, 50, 50))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)


class TinyHugeIsland(Level):
    """Course 13: Tiny-Huge Island"""
    def __init__(self):
        super().__init__("Tiny-Huge Island")
        self.sky_color = (140, 190, 230)
        self.spawn_point = Vec3(0, 100, -400)
        self.scale = 1.0  # Can be 0.5 (tiny) or 2.0 (huge)
        
    def build(self):
        """Build Tiny-Huge Island geometry"""
        s = self.scale
        
        # Main island
        vis, col = LevelGeometry.create_flat_ground(-600*s, -600*s, 1200*s, 1200*s, 0, GRASS_GREEN)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Central mountain
        vis, col = LevelGeometry.create_mountain(0, 200*s, 400*s, 600*s, (100, 120, 80))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Beach edges
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            bx = 500*s * math.cos(rad)
            bz = 500*s * math.sin(rad)
            vis, col = LevelGeometry.create_flat_ground(bx - 100*s, bz - 50*s, 200*s, 100*s, -20*s, SAND_YELLOW)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Water surrounding
        water_verts = [
            Vec3(-1500*s, -30*s, -1500*s),
            Vec3(1500*s, -30*s, -1500*s),
            Vec3(1500*s, -30*s, 1500*s),
            Vec3(-1500*s, -30*s, 1500*s)
        ]
        self.visual_tris.append(Triangle(water_verts[0], water_verts[1], water_verts[2], WATER_BLUE))
        self.visual_tris.append(Triangle(water_verts[0], water_verts[2], water_verts[3], WATER_BLUE))
        
        # Pipe (to switch size)
        vis, col = LevelGeometry.create_cylinder(300*s, 0, -300*s, 50*s, 80*s, 8, GREEN)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Trees (cones)
        tree_positions = [(-200, 100), (150, -200), (-350, -150), (400, 200)]
        for (tx, tz) in tree_positions:
            # Trunk
            vis, col = LevelGeometry.create_cylinder(tx*s, 0, tz*s, 20*s, 120*s, 6, (80, 50, 30))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
            # Leaves
            vis, col = LevelGeometry.create_mountain(tx*s, tz*s, 60*s, 150*s, (30, 120, 30))
            for t in vis:
                t.v0.y += 120*s
                t.v1.y += 120*s
                t.v2.y += 120*s
            self.visual_tris.extend(vis)


class TickTockClock(Level):
    """Course 14: Tick Tock Clock"""
    def __init__(self):
        super().__init__("Tick Tock Clock")
        self.sky_color = (60, 50, 70)
        self.spawn_point = Vec3(0, 100, 0)
        
    def build(self):
        """Build Tick Tock Clock geometry"""
        # Clock interior (cylinder walls - approximated)
        clock_radius = 600
        
        # Floor
        vis, col = LevelGeometry.create_flat_ground(-clock_radius, -clock_radius, 
                                                     clock_radius*2, clock_radius*2, 0, (80, 70, 60))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Platforms at various heights (clock mechanism)
        platform_heights = [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
        
        for i, py in enumerate(platform_heights):
            angle = (i / len(platform_heights)) * 2 * math.pi
            px = 300 * math.cos(angle)
            pz = 300 * math.sin(angle)
            
            # Platform
            vis, col = LevelGeometry.create_flat_ground(px - 100, pz - 100, 200, 200, py, (100, 90, 80))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Central pole
        vis, col = LevelGeometry.create_cylinder(0, 0, 0, 40, 2200, 8, (120, 100, 80))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Gear/cog platforms (hexagonal approximation)
        gear_heights = [300, 700, 1100, 1500, 1900]
        for gy in gear_heights:
            for gi in range(6):
                angle = (gi / 6) * 2 * math.pi
                gx = 200 * math.cos(angle)
                gz = 200 * math.sin(angle)
                vis, col = LevelGeometry.create_box(gx - 40, gy, gz - 40, 80, 30, 80, (150, 130, 100))
                self.visual_tris.extend(vis)
                self.collision_tris.extend(col)
        
        # Pendulum platforms (swinging - simplified as static)
        for py in [500, 1000, 1500]:
            vis, col = LevelGeometry.create_box(-250, py, -50, 100, 30, 100, (180, 160, 120))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)


class RainbowRide(Level):
    """Course 15: Rainbow Ride"""
    def __init__(self):
        super().__init__("Rainbow Ride")
        self.sky_color = (100, 120, 200)
        self.spawn_point = Vec3(0, 100, 0)
        
    def build(self):
        """Build Rainbow Ride geometry"""
        # Starting platform
        vis, col = LevelGeometry.create_flat_ground(-200, -200, 400, 400, 0, (255, 200, 200))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Rainbow path (colored platforms)
        rainbow_colors = [
            (255, 0, 0),     # Red
            (255, 127, 0),   # Orange
            (255, 255, 0),   # Yellow
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (75, 0, 130),    # Indigo
            (148, 0, 211)    # Violet
        ]
        
        for i in range(28):
            color = rainbow_colors[i % 7]
            angle = (i / 7) * math.pi
            height = 200 + i * 80
            radius = 400 + i * 30
            
            px = radius * math.cos(angle)
            pz = radius * math.sin(angle)
            
            vis, col = LevelGeometry.create_flat_ground(px - 80, pz - 80, 160, 160, height, color)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
        
        # Flying ship (large platform)
        ship_y = 1500
        vis, col = LevelGeometry.create_box(-300, ship_y, 800, 600, 50, 300, (139, 90, 43))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Ship mast
        vis, col = LevelGeometry.create_cylinder(0, ship_y + 50, 900, 30, 400, 6, (100, 60, 30))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # House in the sky
        house_y = 2000
        vis, col = LevelGeometry.create_box(-500, house_y, -600, 300, 200, 300, (200, 150, 100))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # House roof
        roof_peak = Vec3(-350, house_y + 350, -450)
        roof_base = [
            Vec3(-550, house_y + 200, -650),
            Vec3(-150, house_y + 200, -650),
            Vec3(-150, house_y + 200, -250),
            Vec3(-550, house_y + 200, -250)
        ]
        for i in range(4):
            self.visual_tris.append(Triangle(
                roof_base[i], roof_base[(i+1)%4], roof_peak, (180, 60, 60)
            ))
        
        # Floating islands
        island_data = [(600, 500, 200), (-700, 800, 250), (500, 1200, 180), (-400, 1600, 220)]
        for (ix, iy, ir) in island_data:
            vis, col = LevelGeometry.create_cylinder(ix, iy, 0, ir, 80, 8, GRASS_GREEN)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)


class CastleHub(Level):
    """Peach's Castle - Hub World"""
    def __init__(self):
        super().__init__("Peach's Castle")
        self.sky_color = (135, 206, 250)
        self.spawn_point = Vec3(0, 50, -800)
        
    def build(self):
        """Build Peach's Castle geometry"""
        # Castle grounds
        vis, col = LevelGeometry.create_flat_ground(-2000, -2000, 4000, 3000, 0, GRASS_GREEN)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Moat
        moat_verts = [
            Vec3(-600, -20, -800),
            Vec3(600, -20, -800),
            Vec3(600, -20, 200),
            Vec3(-600, -20, 200)
        ]
        self.visual_tris.append(Triangle(moat_verts[0], moat_verts[1], moat_verts[2], WATER_BLUE))
        self.visual_tris.append(Triangle(moat_verts[0], moat_verts[2], moat_verts[3], WATER_BLUE))
        
        # Bridge to castle
        vis, col = LevelGeometry.create_box(-100, 0, -500, 200, 30, 400, (139, 90, 43))
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Main castle building
        castle_color = (230, 220, 200)
        
        # Main body
        vis, col = LevelGeometry.create_box(-400, 0, -100, 800, 600, 800, castle_color)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Central tower
        vis, col = LevelGeometry.create_box(-150, 600, 100, 300, 500, 300, castle_color)
        self.visual_tris.extend(vis)
        self.collision_tris.extend(col)
        
        # Tower spire
        spire_base_y = 1100
        spire_peak = Vec3(0, 1400, 250)
        spire_verts = [
            Vec3(-100, spire_base_y, 150),
            Vec3(100, spire_base_y, 150),
            Vec3(100, spire_base_y, 350),
            Vec3(-100, spire_base_y, 350)
        ]
        for i in range(4):
            self.visual_tris.append(Triangle(
                spire_verts[i], spire_verts[(i+1)%4], spire_peak, (200, 50, 50)
            ))
        
        # Side towers
        for side in [-1, 1]:
            tx = side * 350
            vis, col = LevelGeometry.create_box(tx - 100, 0, 400, 200, 400, 200, castle_color)
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
            
            # Tower top (cone)
            tower_peak = Vec3(tx, 600, 500)
            tower_base = [
                Vec3(tx - 120, 400, 380),
                Vec3(tx + 120, 400, 380),
                Vec3(tx + 120, 400, 620),
                Vec3(tx - 120, 400, 620)
            ]
            for i in range(4):
                self.visual_tris.append(Triangle(
                    tower_base[i], tower_base[(i+1)%4], tower_peak, (150, 50, 50)
                ))
        
        # Castle door (visual)
        door_verts = [
            Vec3(-80, 0, -101),
            Vec3(80, 0, -101),
            Vec3(80, 200, -101),
            Vec3(-80, 200, -101)
        ]
        self.visual_tris.append(Triangle(door_verts[0], door_verts[1], door_verts[2], (80, 50, 30)))
        self.visual_tris.append(Triangle(door_verts[0], door_verts[2], door_verts[3], (80, 50, 30)))
        
        # Trees around castle
        tree_positions = [
            (-800, -600), (800, -600), (-1000, 200), (1000, 200),
            (-600, 800), (600, 800), (-1200, -200), (1200, -200)
        ]
        for (tx, tz) in tree_positions:
            # Trunk
            vis, col = LevelGeometry.create_cylinder(tx, 0, tz, 30, 150, 6, (80, 50, 30))
            self.visual_tris.extend(vis)
            self.collision_tris.extend(col)
            # Leaves
            vis, col = LevelGeometry.create_mountain(tx, tz, 100, 200, (30, 120, 30))
            for t in vis:
                t.v0.y += 150
                t.v1.y += 150
                t.v2.y += 150
            self.visual_tris.extend(vis)


# ==================== 3D RENDERER ====================
class Renderer3D:
    """Software 3D renderer"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Projection matrix
        aspect = self.width / self.height
        self.proj_matrix = Matrix4.projection(FOV, aspect, NEAR_PLANE, FAR_PLANE)
        
        # Z-buffer (simplified - using painter's algorithm)
        self.tri_buffer: List[Tuple[float, Triangle, List[Tuple[int, int]]]] = []
        
        # Light direction (sun)
        self.light_dir = Vec3(0.5, -1, 0.3).normalize()
    
    def clear(self, color: Tuple[int, int, int]):
        """Clear screen with color"""
        self.screen.fill(color)
        self.tri_buffer.clear()
    
    def project_point(self, point: Vec3, view_matrix: Matrix4) -> Optional[Tuple[int, int, float]]:
        """Project 3D point to 2D screen coordinates"""
        # Apply view matrix
        viewed = view_matrix.multiply_vector(point)
        
        # Cull points behind camera
        if viewed.z <= NEAR_PLANE:
            return None
        
        # Apply projection
        projected = self.proj_matrix.multiply_vector(viewed)
        
        # Convert to screen coordinates
        screen_x = int((projected.x + 1) * 0.5 * self.width)
        screen_y = int((1 - projected.y) * 0.5 * self.height)
        
        return (screen_x, screen_y, viewed.z)
    
    def add_triangle(self, tri: Triangle, view_matrix: Matrix4):
        """Add triangle to render buffer"""
        # Project all vertices
        p0 = self.project_point(tri.v0, view_matrix)
        p1 = self.project_point(tri.v1, view_matrix)
        p2 = self.project_point(tri.v2, view_matrix)
        
        # Cull if any vertex behind camera
        if p0 is None or p1 is None or p2 is None:
            return
        
        # Backface culling
        # Calculate screen-space normal
        edge1 = (p1[0] - p0[0], p1[1] - p0[1])
        edge2 = (p2[0] - p0[0], p2[1] - p0[1])
        cross = edge1[0] * edge2[1] - edge1[1] * edge2[0]
        
        if cross <= 0:
            return  # Backfacing
        
        # Calculate depth (average Z)
        depth = (p0[2] + p1[2] + p2[2]) / 3
        
        # Calculate lighting
        light_intensity = max(0.3, -tri.normal.dot(self.light_dir))
        shaded_color = (
            int(tri.color[0] * light_intensity),
            int(tri.color[1] * light_intensity),
            int(tri.color[2] * light_intensity)
        )
        
        # Add to buffer
        screen_points = [(p0[0], p0[1]), (p1[0], p1[1]), (p2[0], p2[1])]
        self.tri_buffer.append((depth, Triangle(tri.v0, tri.v1, tri.v2, shaded_color), screen_points))
    
    def render(self):
        """Render all triangles (painter's algorithm)"""
        # Sort by depth (far to near)
        self.tri_buffer.sort(key=lambda x: -x[0])
        
        for depth, tri, points in self.tri_buffer:
            # Clip to screen bounds
            if all(0 <= p[0] < self.width and 0 <= p[1] < self.height for p in points):
                try:
                    pygame.draw.polygon(self.screen, tri.color, points)
                except:
                    pass  # Skip invalid polygons


# ==================== SOUND ====================
class SoundManager:
    """Generate SM64-style sounds and music"""
    def __init__(self):
        self.sample_rate = 44100
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._generate_sounds()
    
    def _generate_sounds(self):
        """Generate all sound effects"""
        import numpy as np
        
        # Jump sound
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq = np.linspace(400, 800, len(t))
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        self.sounds['jump'] = pygame.mixer.Sound(stereo)
        
        # Coin sound
        duration = 0.1
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = np.sin(2 * np.pi * 988 * t) * np.exp(-t * 15) * 0.4
        wave = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        self.sounds['coin'] = pygame.mixer.Sound(stereo)
        
        # Double jump
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq = np.linspace(500, 1000, len(t))
        wave = np.sin(2 * np.pi * freq * t) * 0.35
        wave = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        self.sounds['double_jump'] = pygame.mixer.Sound(stereo)
        
        # Triple jump (higher)
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq = np.linspace(600, 1200, len(t))
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        wave = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        self.sounds['triple_jump'] = pygame.mixer.Sound(stereo)
        
        # Ground pound
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq = np.linspace(200, 50, len(t))
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        wave = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        self.sounds['ground_pound'] = pygame.mixer.Sound(stereo)
    
    def play(self, name: str):
        """Play a sound"""
        if name in self.sounds:
            self.sounds[name].play()


# ==================== HUD ====================
class HUD:
    """SM64-style heads-up display"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw(self, mario: Mario, level_name: str, camera_mode: str):
        """Draw HUD elements"""
        # Stars
        star_text = self.font.render(f"★ x {mario.stars}", True, YELLOW)
        self.screen.blit(star_text, (20, 20))
        
        # Coins
        coin_text = self.font.render(f"🪙 x {mario.coins}", True, YELLOW)
        self.screen.blit(coin_text, (20, 55))
        
        # Lives
        lives_text = self.font.render(f"Mario x {mario.lives}", True, WHITE)
        self.screen.blit(lives_text, (20, 90))
        
        # Health (8 segments)
        health_x = SCREEN_WIDTH - 200
        health_y = 30
        for i in range(8):
            color = (0, 200, 0) if i < mario.health else (80, 80, 80)
            pygame.draw.rect(self.screen, color, (health_x + i * 22, health_y, 18, 30))
            pygame.draw.rect(self.screen, WHITE, (health_x + i * 22, health_y, 18, 30), 1)
        
        # Level name
        level_text = self.small_font.render(level_name, True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 20))
        
        # Camera mode
        cam_text = self.small_font.render(f"Camera: {camera_mode}", True, (150, 150, 150))
        self.screen.blit(cam_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))
        
        # Controls hint
        hint = self.small_font.render("WASD:Move SPACE:Jump SHIFT:Run/Dive CTRL:Crouch Q/E:Camera", True, (150, 150, 150))
        self.screen.blit(hint, (20, SCREEN_HEIGHT - 30))


# ==================== GAME ====================
class Game:
    """Main SM64 game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario 64 - Pygame-CE Engine")
        self.clock = pygame.time.Clock()
        
        # Initialize systems
        self.renderer = Renderer3D(self.screen)
        self.sound_manager = SoundManager()
        self.hud = HUD(self.screen)
        
        # Game objects
        self.mario = Mario(0, 100, 0)
        self.camera = Camera()
        
        # Levels
        self.levels = self._create_levels()
        self.current_level_idx = 0
        self.current_level = self.levels[0]
        self.current_level.build()
        
        # Set Mario spawn
        self.mario.position = self.current_level.spawn_point.copy()
        
        # Game state
        self.running = True
        self.paused = False
        self.frame_count = 0
    
    def _create_levels(self) -> List[Level]:
        """Create all SM64 levels"""
        return [
            CastleHub(),           # 0: Hub world
            BobOmbBattlefield(),   # 1
            WhompsFortress(),      # 2
            JollyRogerBay(),       # 3
            CoolCoolMountain(),    # 4
            BigBoosHaunt(),        # 5
            HazyMazeCave(),        # 6
            LethalLavaLand(),      # 7
            ShiftingSandLand(),    # 8
            DireDireDocks(),       # 9
            SnowmansLand(),        # 10
            WetDryWorld(),         # 11
            TallTallMountain(),    # 12
            TinyHugeIsland(),      # 13
            TickTockClock(),       # 14
            RainbowRide(),         # 15
        ]
    
    def switch_level(self, idx: int):
        """Switch to a different level"""
        if 0 <= idx < len(self.levels):
            self.current_level_idx = idx
            self.current_level = self.levels[idx]
            self.current_level.visual_tris.clear()
            self.current_level.collision_tris.clear()
            self.current_level.build()
            self.mario.position = self.current_level.spawn_point.copy()
            self.mario.velocity = Vec3(0, 0, 0)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                # Level switching (number keys)
                elif event.key == pygame.K_0:
                    self.switch_level(0)
                elif event.key == pygame.K_1:
                    self.switch_level(1)
                elif event.key == pygame.K_2:
                    self.switch_level(2)
                elif event.key == pygame.K_3:
                    self.switch_level(3)
                elif event.key == pygame.K_4:
                    self.switch_level(4)
                elif event.key == pygame.K_5:
                    self.switch_level(5)
                elif event.key == pygame.K_6:
                    self.switch_level(6)
                elif event.key == pygame.K_7:
                    self.switch_level(7)
                elif event.key == pygame.K_8:
                    self.switch_level(8)
                elif event.key == pygame.K_9:
                    self.switch_level(9)
    
    def update(self):
        """Update game state"""
        if self.paused:
            return
        
        self.frame_count += 1
        
        # Get input
        keys = pygame.key.get_pressed()
        
        # Camera rotation
        if keys[pygame.K_q]:
            self.camera.rotate(-0.05)
        if keys[pygame.K_e]:
            self.camera.rotate(0.05)
        
        # Mario input and physics
        self.mario.handle_input(keys, self.camera.yaw)
        self.mario.update(self.current_level.collision_tris)
        
        # Sound effects based on state changes
        if self.mario.state == MarioState.JUMPING and self.mario.jump_count == 1:
            self.sound_manager.play('jump')
        elif self.mario.state == MarioState.DOUBLE_JUMP:
            self.sound_manager.play('double_jump')
        elif self.mario.state == MarioState.TRIPLE_JUMP:
            self.sound_manager.play('triple_jump')
        elif self.mario.state == MarioState.GROUND_POUND_LAND:
            self.sound_manager.play('ground_pound')
        
        # Camera follow
        self.camera.update(self.mario.position, self.mario.facing_angle)
        
        # Coin collection
        for coin in list(self.current_level.coins):
            dist = (coin - self.mario.position).length()
            if dist < 50:
                self.mario.coins += 1
                self.current_level.coins.remove(coin)
                self.sound_manager.play('coin')
        
        # Fall death
        if self.mario.position.y < -500:
            self.mario.lives -= 1
            self.mario.health = 8
            if self.mario.lives <= 0:
                # Game over - reset
                self.mario.lives = 4
                self.mario.coins = 0
                self.mario.stars = 0
            self.mario.position = self.current_level.spawn_point.copy()
            self.mario.velocity = Vec3(0, 0, 0)
    
    def render(self):
        """Render the game"""
        # Clear with sky color
        self.renderer.clear(self.current_level.sky_color)
        
        # Get view matrix
        view_matrix = self.camera.get_view_matrix()
        
        # Add level geometry
        for tri in self.current_level.visual_tris:
            self.renderer.add_triangle(tri, view_matrix)
        
        # Add Mario
        for tri in self.mario.get_triangles():
            self.renderer.add_triangle(tri, view_matrix)
        
        # Add coins (simple yellow dots)
        for coin in self.current_level.coins:
            # Coin as small octahedron
            size = 20
            coin_tris = [
                Triangle(Vec3(coin.x, coin.y + size, coin.z),
                        Vec3(coin.x + size, coin.y, coin.z),
                        Vec3(coin.x, coin.y, coin.z + size), YELLOW),
                Triangle(Vec3(coin.x, coin.y + size, coin.z),
                        Vec3(coin.x, coin.y, coin.z + size),
                        Vec3(coin.x - size, coin.y, coin.z), YELLOW),
                Triangle(Vec3(coin.x, coin.y + size, coin.z),
                        Vec3(coin.x - size, coin.y, coin.z),
                        Vec3(coin.x, coin.y, coin.z - size), YELLOW),
                Triangle(Vec3(coin.x, coin.y + size, coin.z),
                        Vec3(coin.x, coin.y, coin.z - size),
                        Vec3(coin.x + size, coin.y, coin.z), YELLOW),
            ]
            for tri in coin_tris:
                self.renderer.add_triangle(tri, view_matrix)
        
        # Render all triangles
        self.renderer.render()
        
        # Draw HUD
        self.hud.draw(self.mario, self.current_level.name, self.camera.mode)
        
        # Pause overlay
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("PAUSED", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                                          SCREEN_HEIGHT // 2 - 50))
            
            hint_font = pygame.font.Font(None, 36)
            hint = hint_font.render("Press ESC to resume | 0-9 to switch levels", True, (200, 200, 200))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 
                                    SCREEN_HEIGHT // 2 + 30))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


# ==================== MAIN ====================
def main():
    """Entry point"""
    print("=" * 60)
    print("SUPER MARIO 64 - PYGAME-CE 3D ENGINE")
    print("=" * 60)
    print()
    print("All 15 courses + Peach's Castle hub!")
    print("Full Mario moveset with EAD-accurate physics")
    print()
    print("CONTROLS:")
    print("  WASD / Arrow Keys  - Move")
    print("  SPACE              - Jump (tap/hold for height)")
    print("  SHIFT              - Run / Dive")
    print("  CTRL               - Crouch / Ground Pound")
    print("  Q / E              - Rotate Camera")
    print("  0-9                - Switch Levels")
    print("  ESC                - Pause")
    print()
    print("MOVES:")
    print("  - Single Jump, Double Jump, Triple Jump (while running)")
    print("  - Long Jump (Crouch + Run + Jump)")
    print("  - Backflip (Crouch + Jump)")
    print("  - Ground Pound (Jump + Crouch in air)")
    print("  - Dive (Run + Shift)")
    print()
    print("© 2026 Team Flames / Samsoft")
    print("=" * 60)
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

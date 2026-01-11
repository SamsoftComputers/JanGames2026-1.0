#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║              ULTRA MARIO 3D BROS. — COMPLETE 120 STARS EDITION                    ║
║                         Team Flames / Samsoft / Cat OS                            ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  Legal: No Nintendo/Mario 64 code or assets. Procedural geometry only.            ║
║  Fan project strictly for educational procedural generation demonstration.        ║
╚═══════════════════════════════════════════════════════════════════════════════════╝

All 120 Stars:
- 15 Main Courses (7 stars each = 105 stars)
- 15 Castle Secret Stars
- 3 Bowser Courses (keys to unlock areas)

Controls:
- WASD: Move | SPACE: Jump (triple jump combo) | SHIFT: Run
- Mouse: Camera | E: Interact/Enter | ESC: Pause/Exit course
"""

from __future__ import annotations
import math
import sys
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum, auto

# ═══════════════════════════════════════════════════════════════════════════════════
# PANDA3D CONFIG (BEFORE IMPORTS)
# ═══════════════════════════════════════════════════════════════════════════════════
from panda3d.core import loadPrcFileData
loadPrcFileData("", "window-title Ultra Mario 3D Bros. - 120 Stars Edition")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")
loadPrcFileData("", "show-frame-rate-meter 1")
loadPrcFileData("", "text-encoding utf8")
loadPrcFileData("", "framebuffer-srgb true")
loadPrcFileData("", "audio-library-name null")  # Disable audio for now

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task
from direct.interval.IntervalGlobal import (
    Sequence, Parallel, Func, Wait,
    LerpScaleInterval, LerpColorScaleInterval,
    LerpPosInterval, LerpHprInterval
)

from panda3d.core import (
    Vec3, Vec2, Vec4, Point3, NodePath,
    WindowProperties, TextNode, CardMaker,
    AmbientLight, DirectionalLight, PointLight, Spotlight,
    LColor, BitMask32, TransparencyAttrib,
    Fog, CompassEffect, BillboardEffect,
    CollisionTraverser, CollisionNode, CollisionSphere,
    CollisionHandlerQueue, CollisionRay
)

from panda3d.bullet import (
    BulletWorld, BulletDebugNode,
    BulletRigidBodyNode, BulletGhostNode,
    BulletBoxShape, BulletSphereShape,
    BulletCapsuleShape, BulletCylinderShape,
    BulletCharacterControllerNode,
    BulletTriangleMesh, BulletTriangleMeshShape,
    ZUp
)

FILES_OFF = True  # No external models/assets - everything procedural

# ═══════════════════════════════════════════════════════════════════════════════════
# GAME CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class GameConfig:
    """Master game configuration"""
    # Physics
    gravity: float = 38.0
    max_fall_speed: float = 50.0
    
    # Movement
    walk_speed: float = 12.0
    run_speed: float = 20.0
    swim_speed: float = 8.0
    crawl_speed: float = 4.0
    
    # Acceleration
    ground_accel: float = 65.0
    air_accel: float = 25.0
    ground_friction: float = 40.0
    air_friction: float = 5.0
    water_friction: float = 15.0
    
    # Jumping
    jump_power: float = 15.0
    double_jump_power: float = 18.0
    triple_jump_power: float = 24.0
    wall_jump_power: float = 14.0
    backflip_power: float = 20.0
    sideflip_power: float = 18.0
    longjump_power: float = 12.0
    longjump_forward: float = 18.0
    jump_window: float = 0.3
    
    # Camera
    cam_distance: float = 22.0
    cam_height: float = 8.0
    cam_smooth: float = 6.0
    cam_rotate_speed: float = 120.0
    
    # Game
    total_stars: int = 120
    stars_for_door_1: int = 1
    stars_for_door_2: int = 3
    stars_for_door_3: int = 8
    stars_for_basement: int = 12
    stars_for_upstairs: int = 30
    stars_for_tippy: int = 70

# ═══════════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════════

class GameState(Enum):
    TITLE = auto()
    FILE_SELECT = auto()
    CASTLE = auto()
    COURSE = auto()
    BOWSER = auto()
    STAR_GET = auto()
    PAUSED = auto()
    ENDING = auto()

class MoveState(Enum):
    IDLE = auto()
    WALKING = auto()
    RUNNING = auto()
    JUMPING = auto()
    DOUBLE_JUMP = auto()
    TRIPLE_JUMP = auto()
    FALLING = auto()
    GROUND_POUND = auto()
    DIVING = auto()
    SLIDING = auto()
    SWIMMING = auto()
    CLIMBING = auto()
    HANGING = auto()
    WALL_SLIDE = auto()
    LONG_JUMP = auto()
    BACKFLIP = auto()
    SIDEFLIP = auto()
    KNOCKBACK = auto()

class StarType(Enum):
    MISSION = auto()      # Standard mission star
    RED_COINS = auto()    # Collect 8 red coins
    HUNDRED_COINS = auto() # 100 coin star
    SECRET = auto()       # Hidden star
    BOSS = auto()         # Defeat boss
    RACE = auto()         # Win a race
    SWITCH = auto()       # Cap switch star

@dataclass
class StarData:
    """Information about a single star"""
    id: int
    course_id: int
    name: str
    star_type: StarType
    position: Vec3
    hint: str = ""
    collected: bool = False

@dataclass 
class CourseData:
    """Information about a course/level"""
    id: int
    name: str
    painting_pos: Vec3
    required_stars: int
    star_names: List[str]
    theme: str  # grass, snow, water, lava, sky, desert, cave, haunted
    difficulty: int  # 1-5

@dataclass
class SaveFile:
    """Player save data"""
    slot: int
    name: str
    stars_collected: List[int] = field(default_factory=list)
    total_stars: int = 0
    coins_total: int = 0
    play_time: float = 0.0
    caps_unlocked: Dict[str, bool] = field(default_factory=lambda: {
        "wing": False, "metal": False, "vanish": False
    })
    keys_obtained: List[int] = field(default_factory=list)  # Bowser keys
    cannons_opened: List[int] = field(default_factory=list)

# ═══════════════════════════════════════════════════════════════════════════════════
# COURSE DEFINITIONS - ALL 15 MAIN COURSES + SECRETS
# ═══════════════════════════════════════════════════════════════════════════════════

COURSES = [
    # Floor 1 Courses (Stars 1-15 required range)
    CourseData(1, "BOB-OMB BATTLEFIELD", Vec3(-20, 30, 5), 0,
        ["Big Bob-omb on the Summit", "Footrace with Koopa", "Shoot to the Island",
         "Find the 8 Red Coins", "Mario Wings to the Sky", "Behind Chain Chomp's Gate", "100 Coins"],
        "grass", 1),
    
    CourseData(2, "WHOMP'S FORTRESS", Vec3(-20, 50, 5), 1,
        ["Chip Off Whomp's Block", "To the Top of the Fortress", "Shoot into the Wild Blue",
         "Red Coins on the Floating Isle", "Fall onto the Caged Island", "Blast Away the Wall", "100 Coins"],
        "fortress", 2),
    
    CourseData(3, "JOLLY ROGER BAY", Vec3(20, 30, 5), 3,
        ["Plunder in the Sunken Ship", "Can the Eel Come Out to Play?", "Treasure of the Ocean Cave",
         "Red Coins on the Ship Afloat", "Blast to the Stone Pillar", "Through the Jet Stream", "100 Coins"],
        "water", 2),
    
    CourseData(4, "COOL COOL MOUNTAIN", Vec3(20, 50, 5), 3,
        ["Slip Slidin' Away", "Li'l Penguin Lost", "Big Penguin Race",
         "Frosty Slide for 8 Red Coins", "Snowman's Lost His Head", "Wall Kicks Will Work", "100 Coins"],
        "snow", 2),
    
    CourseData(5, "BIG BOO'S HAUNT", Vec3(0, -30, 0), 12,
        ["Go on a Ghost Hunt", "Ride Big Boo's Merry-Go-Round", "Secret of the Haunted Books",
         "Seek the 8 Red Coins", "Big Boo's Balcony", "Eye to Eye in the Secret Room", "100 Coins"],
        "haunted", 3),
    
    # Floor 2 Courses (Basement - 12+ stars)
    CourseData(6, "HAZY MAZE CAVE", Vec3(-30, 0, -10), 12,
        ["Swimming Beast in the Cavern", "Elevate for 8 Red Coins", "Metal-Head Mario Can Move!",
         "Navigating the Toxic Maze", "A-Maze-Ing Emergency Exit", "Watch for Rolling Rocks", "100 Coins"],
        "cave", 3),
    
    CourseData(7, "LETHAL LAVA LAND", Vec3(0, 0, -10), 12,
        ["Boil the Big Bully", "Bully the Bullies", "8-Coin Puzzle with 15 Pieces",
         "Red-Hot Log Rolling", "Hot-Foot-It into the Volcano", "Elevator Tour in the Volcano", "100 Coins"],
        "lava", 3),
    
    CourseData(8, "SHIFTING SAND LAND", Vec3(30, 0, -10), 12,
        ["In the Talons of the Big Bird", "Shining Atop the Pyramid", "Inside the Ancient Pyramid",
         "Stand Tall on the Four Pillars", "Free Flying for 8 Red Coins", "Pyramid Puzzle", "100 Coins"],
        "desert", 3),
    
    CourseData(9, "DIRE DIRE DOCKS", Vec3(0, -50, -10), 30,
        ["Board Bowser's Sub", "Chests in the Current", "Pole-Jumping for Red Coins",
         "Through the Jet Stream", "The Manta Ray's Reward", "Collect the Caps...", "100 Coins"],
        "water", 4),
    
    # Floor 3 Courses (Upstairs - 30+ stars)
    CourseData(10, "SNOWMAN'S LAND", Vec3(-30, 30, 20), 30,
        ["Snowman's Big Head", "Chill with the Bully", "In the Deep Freeze",
         "Whirl from the Freezing Pond", "Shell Shreddin' for Red Coins", "Into the Igloo", "100 Coins"],
        "snow", 4),
    
    CourseData(11, "WET-DRY WORLD", Vec3(0, 30, 20), 30,
        ["Shocking Arrow Lifts!", "Top o' the Town", "Secrets in the Shallows & Sky",
         "Express Elevator--Hurry Up!", "Go to Town for Red Coins", "Quick Race Through Downtown!", "100 Coins"],
        "mechanical", 4),
    
    CourseData(12, "TALL TALL MOUNTAIN", Vec3(30, 30, 20), 30,
        ["Scale the Mountain", "Mystery of the Monkey Cage", "Scary 'Shrooms, Red Coins",
         "Mysterious Mountainside", "Breathtaking View from Bridge", "Blast to the Lonely Mushroom", "100 Coins"],
        "mountain", 4),
    
    CourseData(13, "TINY-HUGE ISLAND", Vec3(-15, 60, 20), 30,
        ["Pluck the Piranha Flower", "The Tip Top of the Huge Island", "Rematch with Koopa the Quick",
         "Five Itty Bitty Secrets", "Wiggler's Red Coins", "Make Wiggler Squirm", "100 Coins"],
        "grass", 4),
    
    # Tippy Top (70+ stars)
    CourseData(14, "TICK TOCK CLOCK", Vec3(0, 0, 40), 70,
        ["Roll into the Cage", "The Pit and the Pendulums", "Get a Hand",
         "Stomp on the Thwomp", "Timed Jumps on Moving Bars", "Stop Time for Red Coins", "100 Coins"],
        "mechanical", 5),
    
    CourseData(15, "RAINBOW RIDE", Vec3(0, 30, 45), 70,
        ["Cruiser Crossing the Rainbow", "The Big House in the Sky", "Coins Amassed in a Maze",
         "Swingin' in the Breeze", "Tricky Triangles!", "Somewhere Over the Rainbow", "100 Coins"],
        "sky", 5),
]

# Bowser Courses
BOWSER_COURSES = [
    CourseData(101, "BOWSER IN THE DARK WORLD", Vec3(0, 100, 5), 8, ["Defeat Bowser 1"], "dark", 3),
    CourseData(102, "BOWSER IN THE FIRE SEA", Vec3(0, 100, -10), 30, ["Defeat Bowser 2"], "lava", 4),
    CourseData(103, "BOWSER IN THE SKY", Vec3(0, 100, 50), 70, ["Defeat Bowser 3"], "sky", 5),
]

# Castle Secret Stars
CASTLE_SECRETS = [
    StarData(106, 0, "Toad Star 1", StarType.SECRET, Vec3(10, 20, 2)),
    StarData(107, 0, "Toad Star 2", StarType.SECRET, Vec3(-15, 40, 2)),
    StarData(108, 0, "Toad Star 3", StarType.SECRET, Vec3(25, 60, 22)),
    StarData(109, 0, "Princess's Secret Slide 1", StarType.SECRET, Vec3(-40, 20, 15)),
    StarData(110, 0, "Princess's Secret Slide 2", StarType.SECRET, Vec3(-40, 20, 15)),
    StarData(111, 0, "Secret Aquarium", StarType.SECRET, Vec3(30, 55, 8)),
    StarData(112, 0, "Wing Mario Over the Rainbow", StarType.SECRET, Vec3(0, 0, 50)),
    StarData(113, 0, "Tower of the Wing Cap", StarType.SWITCH, Vec3(0, 50, 0)),
    StarData(114, 0, "Cavern of the Metal Cap", StarType.SWITCH, Vec3(-50, 0, -10)),
    StarData(115, 0, "Vanish Cap Under the Moat", StarType.SWITCH, Vec3(50, -30, -5)),
    StarData(116, 0, "Bowser 1 Red Coins", StarType.RED_COINS, Vec3(0, 100, 5)),
    StarData(117, 0, "Bowser 2 Red Coins", StarType.RED_COINS, Vec3(0, 100, -10)),
    StarData(118, 0, "Bowser 3 Red Coins", StarType.RED_COINS, Vec3(0, 100, 50)),
    StarData(119, 0, "MIPS Rabbit 1", StarType.SECRET, Vec3(-20, -20, -8)),
    StarData(120, 0, "MIPS Rabbit 2", StarType.SECRET, Vec3(-20, -20, -8)),
]

# ═══════════════════════════════════════════════════════════════════════════════════
# COLOR PALETTES
# ═══════════════════════════════════════════════════════════════════════════════════

COLORS = {
    # Mario
    "mario_red": (0.9, 0.1, 0.1, 1),
    "mario_blue": (0.1, 0.2, 0.8, 1),
    "mario_skin": (1.0, 0.8, 0.6, 1),
    "mario_brown": (0.4, 0.2, 0.1, 1),
    "mario_yellow": (1.0, 0.9, 0.0, 1),
    
    # Environment
    "grass_green": (0.2, 0.7, 0.2, 1),
    "grass_dark": (0.15, 0.5, 0.15, 1),
    "dirt_brown": (0.5, 0.35, 0.2, 1),
    "stone_gray": (0.5, 0.5, 0.55, 1),
    "stone_dark": (0.35, 0.35, 0.4, 1),
    "brick_red": (0.7, 0.3, 0.2, 1),
    "wood_brown": (0.6, 0.4, 0.2, 1),
    
    # Water/Ice
    "water_blue": (0.2, 0.5, 0.9, 0.7),
    "water_deep": (0.1, 0.3, 0.7, 0.8),
    "ice_blue": (0.7, 0.85, 0.95, 1),
    "snow_white": (0.95, 0.95, 1.0, 1),
    
    # Lava/Fire
    "lava_orange": (1.0, 0.4, 0.1, 1),
    "lava_red": (0.9, 0.2, 0.1, 1),
    "lava_yellow": (1.0, 0.8, 0.2, 1),
    
    # Desert
    "sand_yellow": (0.9, 0.8, 0.5, 1),
    "sand_dark": (0.7, 0.6, 0.4, 1),
    "pyramid_tan": (0.85, 0.75, 0.55, 1),
    
    # Sky
    "sky_blue": (0.5, 0.7, 1.0, 1),
    "cloud_white": (1.0, 1.0, 1.0, 1),
    "rainbow_red": (1.0, 0.3, 0.3, 1),
    "rainbow_orange": (1.0, 0.6, 0.2, 1),
    "rainbow_yellow": (1.0, 1.0, 0.3, 1),
    "rainbow_green": (0.3, 1.0, 0.3, 1),
    "rainbow_blue": (0.3, 0.5, 1.0, 1),
    "rainbow_purple": (0.7, 0.3, 1.0, 1),
    
    # Items
    "coin_gold": (1.0, 0.85, 0.0, 1),
    "star_yellow": (1.0, 0.95, 0.3, 1),
    "red_coin": (1.0, 0.2, 0.2, 1),
    "blue_coin": (0.3, 0.5, 1.0, 1),
    
    # UI
    "ui_white": (1.0, 1.0, 1.0, 1),
    "ui_yellow": (1.0, 0.9, 0.2, 1),
    "ui_red": (1.0, 0.3, 0.3, 1),
    "ui_shadow": (0.0, 0.0, 0.0, 0.8),
}

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def angle_diff(a, b):
    """Shortest angle difference"""
    diff = (b - a) % 360
    if diff > 180:
        diff -= 360
    return diff

def vec3_xz(v: Vec3) -> Vec3:
    """Return vector with Y zeroed (horizontal only)"""
    return Vec3(v.x, v.y, 0)

# ═══════════════════════════════════════════════════════════════════════════════════
# PROCEDURAL GEOMETRY BUILDER
# ═══════════════════════════════════════════════════════════════════════════════════

class ProceduralBuilder:
    """Creates all game geometry procedurally"""
    
    @staticmethod
    def make_box(parent: NodePath, world: BulletWorld, size: Tuple[float, float, float],
                 pos: Point3, color: Tuple = COLORS["stone_gray"], name: str = "box",
                 mass: float = 0.0) -> NodePath:
        """Create a physics-enabled box with visual geometry"""
        sx, sy, sz = size
        shape = BulletBoxShape(Vec3(sx/2, sy/2, sz/2))
        
        body = BulletRigidBodyNode(name)
        body.addShape(shape)
        body.setMass(mass)
        body.setIntoCollideMask(BitMask32.allOn())
        
        np = parent.attachNewNode(body)
        np.setPos(pos)
        world.attachRigidBody(body)
        
        # Visual geometry
        ProceduralBuilder._add_box_visuals(np, size, color)
        
        return np
    
    @staticmethod
    def _add_box_visuals(np: NodePath, size: Tuple[float, float, float], color: Tuple):
        """Add visual cards to represent a box"""
        sx, sy, sz = size
        cm = CardMaker("face")
        
        vis = np.attachNewNode("visuals")
        
        # Colors for shading
        c_top = color
        c_side = (color[0]*0.75, color[1]*0.75, color[2]*0.75, color[3])
        c_dark = (color[0]*0.55, color[1]*0.55, color[2]*0.55, color[3])
        
        # Top face
        cm.setFrame(-sx/2, sx/2, -sy/2, sy/2)
        top = vis.attachNewNode(cm.generate())
        top.setP(-90)
        top.setZ(sz/2)
        top.setColor(c_top)
        
        # Bottom face
        bottom = vis.attachNewNode(cm.generate())
        bottom.setP(90)
        bottom.setZ(-sz/2)
        bottom.setColor(c_dark)
        
        # Front face (Y-)
        cm.setFrame(-sx/2, sx/2, -sz/2, sz/2)
        front = vis.attachNewNode(cm.generate())
        front.setY(-sy/2)
        front.setColor(c_side)
        
        # Back face (Y+)
        back = vis.attachNewNode(cm.generate())
        back.setY(sy/2)
        back.setH(180)
        back.setColor(c_dark)
        
        # Left face (X-)
        cm.setFrame(-sy/2, sy/2, -sz/2, sz/2)
        left = vis.attachNewNode(cm.generate())
        left.setX(-sx/2)
        left.setH(-90)
        left.setColor(c_dark)
        
        # Right face (X+)
        right = vis.attachNewNode(cm.generate())
        right.setX(sx/2)
        right.setH(90)
        right.setColor(c_side)
    
    @staticmethod
    def make_cylinder(parent: NodePath, world: BulletWorld, radius: float, height: float,
                      pos: Point3, color: Tuple = COLORS["stone_gray"], 
                      segments: int = 12, name: str = "cylinder") -> NodePath:
        """Create a cylinder with physics"""
        shape = BulletCylinderShape(radius, height, ZUp)
        
        body = BulletRigidBodyNode(name)
        body.addShape(shape)
        body.setMass(0)
        body.setIntoCollideMask(BitMask32.allOn())
        
        np = parent.attachNewNode(body)
        np.setPos(pos)
        world.attachRigidBody(body)
        
        # Visual - simplified as octagon
        ProceduralBuilder._add_cylinder_visuals(np, radius, height, segments, color)
        
        return np
    
    @staticmethod
    def _add_cylinder_visuals(np: NodePath, radius: float, height: float, 
                               segments: int, color: Tuple):
        """Add visual representation of cylinder"""
        vis = np.attachNewNode("visuals")
        cm = CardMaker("face")
        
        c_top = color
        c_side = (color[0]*0.7, color[1]*0.7, color[2]*0.7, color[3])
        
        # Side faces
        angle_step = 360 / segments
        for i in range(segments):
            angle = math.radians(i * angle_step)
            next_angle = math.radians((i + 1) * angle_step)
            
            # Calculate width of this segment
            x1, y1 = math.cos(angle) * radius, math.sin(angle) * radius
            x2, y2 = math.cos(next_angle) * radius, math.sin(next_angle) * radius
            
            width = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            mid_angle = (i + 0.5) * angle_step
            
            cm.setFrame(-width/2, width/2, -height/2, height/2)
            face = vis.attachNewNode(cm.generate())
            face.setH(mid_angle)
            face.setY(radius * 0.95)  # Slight inset
            face.setColor(c_side)
        
        # Top cap (simplified as polygon approximation)
        cm.setFrame(-radius, radius, -radius, radius)
        top = vis.attachNewNode(cm.generate())
        top.setP(-90)
        top.setZ(height/2)
        top.setColor(c_top)
    
    @staticmethod
    def make_sphere(parent: NodePath, world: BulletWorld, radius: float,
                    pos: Point3, color: Tuple = COLORS["stone_gray"],
                    mass: float = 0.0, name: str = "sphere") -> NodePath:
        """Create a sphere with physics (visual is simplified)"""
        shape = BulletSphereShape(radius)
        
        body = BulletRigidBodyNode(name)
        body.addShape(shape)
        body.setMass(mass)
        body.setIntoCollideMask(BitMask32.allOn())
        
        np = parent.attachNewNode(body)
        np.setPos(pos)
        world.attachRigidBody(body)
        
        # Visual - billboard circle
        cm = CardMaker("sphere_vis")
        cm.setFrame(-radius, radius, -radius, radius)
        vis = np.attachNewNode(cm.generate())
        vis.setColor(color)
        vis.setBillboardPointEye()
        vis.setTransparency(TransparencyAttrib.MAlpha)
        
        return np
    
    @staticmethod
    def make_ramp(parent: NodePath, world: BulletWorld, 
                  width: float, length: float, height: float,
                  pos: Point3, heading: float = 0,
                  color: Tuple = COLORS["stone_gray"], name: str = "ramp") -> NodePath:
        """Create a triangular ramp/slope"""
        # Use a rotated box as approximation
        # Actual triangle mesh would be more accurate but box works for basic slopes
        depth = math.sqrt(length**2 + height**2)
        angle = math.degrees(math.atan2(height, length))
        
        shape = BulletBoxShape(Vec3(width/2, depth/2, 0.5))
        
        body = BulletRigidBodyNode(name)
        body.addShape(shape)
        body.setMass(0)
        
        np = parent.attachNewNode(body)
        np.setPos(pos)
        np.setH(heading)
        np.setP(-angle)
        world.attachRigidBody(body)
        
        # Visual
        cm = CardMaker("ramp_face")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        vis = np.attachNewNode(cm.generate())
        vis.setColor(color)
        
        return np
    
    @staticmethod
    def make_platform(parent: NodePath, world: BulletWorld,
                      size: Tuple[float, float], height: float,
                      pos: Point3, color: Tuple = COLORS["grass_green"],
                      name: str = "platform") -> NodePath:
        """Create a flat platform (thin box)"""
        return ProceduralBuilder.make_box(parent, world, 
                                          (size[0], size[1], height),
                                          pos, color, name)
    
    @staticmethod
    def make_coin(parent: NodePath, pos: Point3, coin_type: str = "yellow") -> NodePath:
        """Create a collectible coin"""
        colors = {
            "yellow": COLORS["coin_gold"],
            "red": COLORS["red_coin"],
            "blue": COLORS["blue_coin"]
        }
        color = colors.get(coin_type, COLORS["coin_gold"])
        
        coin_np = parent.attachNewNode(f"coin_{coin_type}")
        coin_np.setPos(pos)
        
        cm = CardMaker("coin")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        vis = coin_np.attachNewNode(cm.generate())
        vis.setColor(color)
        vis.setBillboardPointEye()
        vis.setTransparency(TransparencyAttrib.MAlpha)
        
        # Add a subtle glow/outline
        glow = coin_np.attachNewNode(cm.generate())
        glow.setColor(color[0], color[1], color[2], 0.3)
        glow.setScale(1.3)
        glow.setBillboardPointEye()
        glow.setTransparency(TransparencyAttrib.MAlpha)
        
        # Spin animation
        spin = LerpHprInterval(coin_np, 2.0, (360, 0, 0), (0, 0, 0))
        spin.loop()
        
        return coin_np
    
    @staticmethod
    def make_star(parent: NodePath, pos: Point3, star_id: int) -> NodePath:
        """Create a power star collectible"""
        star_np = parent.attachNewNode(f"star_{star_id}")
        star_np.setPos(pos)
        
        # Star shape (simplified as rotating card)
        cm = CardMaker("star")
        cm.setFrame(-1, 1, -1, 1)
        
        vis = star_np.attachNewNode(cm.generate())
        vis.setColor(COLORS["star_yellow"])
        vis.setBillboardPointEye()
        vis.setTransparency(TransparencyAttrib.MAlpha)
        
        # Glow
        glow = star_np.attachNewNode(cm.generate())
        glow.setColor(1, 1, 0.5, 0.4)
        glow.setScale(1.5)
        glow.setBillboardPointEye()
        glow.setTransparency(TransparencyAttrib.MAlpha)
        
        # Bobbing animation
        bob = Sequence(
            LerpPosInterval(star_np, 1.0, pos + Vec3(0, 0, 0.5), pos),
            LerpPosInterval(star_np, 1.0, pos, pos + Vec3(0, 0, 0.5))
        )
        bob.loop()
        
        # Spin
        spin = LerpHprInterval(vis, 3.0, (360, 0, 0), (0, 0, 0))
        spin.loop()
        
        return star_np
    
    @staticmethod
    def make_enemy_goomba(parent: NodePath, world: BulletWorld, pos: Point3) -> NodePath:
        """Create a Goomba-like enemy"""
        enemy_np = parent.attachNewNode("goomba")
        enemy_np.setPos(pos)
        
        # Body (brown mushroom shape)
        cm = CardMaker("body")
        cm.setFrame(-0.6, 0.6, 0, 1.2)
        body = enemy_np.attachNewNode(cm.generate())
        body.setColor(0.6, 0.4, 0.2, 1)
        body.setBillboardPointEye()
        
        # Feet
        cm.setFrame(-0.3, 0.3, -0.2, 0.2)
        feet = enemy_np.attachNewNode(cm.generate())
        feet.setColor(0.3, 0.2, 0.1, 1)
        feet.setZ(-0.1)
        feet.setBillboardPointEye()
        
        # Simple physics body
        shape = BulletSphereShape(0.6)
        body_node = BulletGhostNode("goomba_trigger")
        body_node.addShape(shape)
        trig_np = enemy_np.attachNewNode(body_node)
        trig_np.setZ(0.6)
        world.attachGhost(body_node)
        
        return enemy_np

# ═══════════════════════════════════════════════════════════════════════════════════
# LEVEL GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════════

class LevelGenerator:
    """Generates complete levels procedurally"""
    
    def __init__(self, parent: NodePath, world: BulletWorld):
        self.parent = parent
        self.world = world
        self.builder = ProceduralBuilder()
        self.coins: List[NodePath] = []
        self.stars: List[NodePath] = []
        self.enemies: List[NodePath] = []
    
    def clear_level(self):
        """Remove all level geometry"""
        for child in self.parent.getChildren():
            child.removeNode()
        self.coins.clear()
        self.stars.clear()
        self.enemies.clear()
    
    def generate_castle(self) -> Vec3:
        """Generate Peach's Castle hub world"""
        self.clear_level()
        
        # Ground/courtyard
        self.builder.make_box(self.parent, self.world, (200, 200, 2),
                              Point3(0, 0, -1), COLORS["grass_green"], "ground")
        
        # Castle main building
        self.builder.make_box(self.parent, self.world, (40, 30, 25),
                              Point3(0, 50, 12.5), COLORS["stone_gray"], "castle_main")
        
        # Castle towers
        for x_off in [-25, 25]:
            self.builder.make_box(self.parent, self.world, (10, 10, 35),
                                  Point3(x_off, 50, 17.5), COLORS["stone_gray"], "tower")
            # Tower top
            self.builder.make_box(self.parent, self.world, (12, 12, 3),
                                  Point3(x_off, 50, 36.5), COLORS["brick_red"], "tower_top")
        
        # Castle entrance
        self.builder.make_box(self.parent, self.world, (15, 10, 20),
                              Point3(0, 35, 10), COLORS["stone_dark"], "entrance")
        
        # Front steps
        for i in range(5):
            self.builder.make_box(self.parent, self.world, (20 - i*2, 4, 1),
                                  Point3(0, 28 - i*3, i*1), COLORS["stone_gray"], f"step_{i}")
        
        # Bridge over moat
        self.builder.make_box(self.parent, self.world, (12, 20, 1),
                              Point3(0, 10, 0.5), COLORS["wood_brown"], "bridge")
        
        # Moat (visual only - water plane)
        self.builder.make_box(self.parent, self.world, (80, 80, 0.1),
                              Point3(0, 30, -0.5), COLORS["water_blue"], "moat")
        
        # Painting frames (course entrances) - Floor 1
        self._make_painting_frame(Vec3(-20, 48, 5), 1)  # Bob-omb Battlefield
        self._make_painting_frame(Vec3(-20, 48, 12), 2)  # Whomp's Fortress
        self._make_painting_frame(Vec3(20, 48, 5), 3)   # Jolly Roger Bay
        self._make_painting_frame(Vec3(20, 48, 12), 4)  # Cool Cool Mountain
        
        # Courtyard elements
        self._add_courtyard_decorations()
        
        # Scatter some coins
        for i in range(20):
            angle = random.random() * 6.28
            dist = random.uniform(10, 40)
            pos = Point3(math.cos(angle)*dist, math.sin(angle)*dist + 20, 1)
            coin = self.builder.make_coin(self.parent, pos)
            self.coins.append(coin)
        
        return Vec3(0, 0, 2)  # Spawn position
    
    def _make_painting_frame(self, pos: Vec3, course_id: int):
        """Create a painting frame for course entrance"""
        # Frame
        self.builder.make_box(self.parent, self.world, (6, 0.5, 5),
                              Point3(pos.x, pos.y, pos.z), COLORS["wood_brown"], f"frame_{course_id}")
        # Canvas (colored by course)
        course = COURSES[course_id - 1] if course_id <= len(COURSES) else None
        color = self._get_theme_color(course.theme if course else "grass")
        self.builder.make_box(self.parent, self.world, (5, 0.2, 4),
                              Point3(pos.x, pos.y - 0.2, pos.z), color, f"painting_{course_id}")
    
    def _get_theme_color(self, theme: str) -> Tuple:
        """Get primary color for a level theme"""
        themes = {
            "grass": COLORS["grass_green"],
            "fortress": COLORS["stone_gray"],
            "water": COLORS["water_blue"],
            "snow": COLORS["snow_white"],
            "haunted": (0.3, 0.2, 0.4, 1),
            "cave": COLORS["stone_dark"],
            "lava": COLORS["lava_orange"],
            "desert": COLORS["sand_yellow"],
            "mechanical": (0.6, 0.6, 0.7, 1),
            "mountain": COLORS["dirt_brown"],
            "sky": COLORS["sky_blue"],
            "dark": (0.2, 0.1, 0.3, 1),
        }
        return themes.get(theme, COLORS["grass_green"])
    
    def _add_courtyard_decorations(self):
        """Add trees, bushes, etc to castle courtyard"""
        # Trees (simple cylinders with green tops)
        tree_positions = [
            (-30, 10), (30, 10), (-40, 30), (40, 30),
            (-25, -10), (25, -10), (-35, 50), (35, 50)
        ]
        for x, y in tree_positions:
            # Trunk
            self.builder.make_cylinder(self.parent, self.world, 0.8, 5,
                                       Point3(x, y, 2.5), COLORS["wood_brown"], 8, "trunk")
            # Foliage (simplified as box)
            self.builder.make_box(self.parent, self.world, (4, 4, 5),
                                  Point3(x, y, 7), COLORS["grass_dark"], "foliage")
    
    def generate_course(self, course_id: int) -> Vec3:
        """Generate a specific course"""
        self.clear_level()
        
        if course_id <= 0 or course_id > len(COURSES):
            return self.generate_test_level()
        
        course = COURSES[course_id - 1]
        
        # Generate based on theme
        generators = {
            "grass": self._gen_grass_level,
            "fortress": self._gen_fortress_level,
            "water": self._gen_water_level,
            "snow": self._gen_snow_level,
            "haunted": self._gen_haunted_level,
            "cave": self._gen_cave_level,
            "lava": self._gen_lava_level,
            "desert": self._gen_desert_level,
            "mechanical": self._gen_mechanical_level,
            "mountain": self._gen_mountain_level,
            "sky": self._gen_sky_level,
        }
        
        generator = generators.get(course.theme, self._gen_grass_level)
        spawn_pos = generator(course)
        
        # Add stars for this course
        self._add_course_stars(course)
        
        return spawn_pos
    
    def _gen_grass_level(self, course: CourseData) -> Vec3:
        """Generate Bob-omb Battlefield style grass level"""
        # Main ground
        self.builder.make_box(self.parent, self.world, (150, 150, 3),
                              Point3(0, 0, -1.5), COLORS["grass_green"], "ground")
        
        # Central mountain
        for i in range(6):
            size = 40 - i * 5
            height = 6
            self.builder.make_box(self.parent, self.world, (size, size, height),
                                  Point3(0, 40, i * height + height/2), 
                                  COLORS["dirt_brown"], f"mountain_{i}")
        
        # Summit platform
        self.builder.make_box(self.parent, self.world, (12, 12, 2),
                              Point3(0, 40, 37), COLORS["stone_gray"], "summit")
        
        # Star at summit (Star 1)
        star = self.builder.make_star(self.parent, Point3(0, 40, 40), 1)
        self.stars.append(star)
        
        # Paths and platforms
        # Bridge
        self.builder.make_box(self.parent, self.world, (8, 25, 1),
                              Point3(-20, 20, 2), COLORS["wood_brown"], "bridge")
        
        # Chain chomp area
        self.builder.make_box(self.parent, self.world, (15, 15, 1),
                              Point3(30, 10, 0.5), COLORS["grass_dark"], "chomp_area")
        
        # Floating island (cannon target)
        self.builder.make_box(self.parent, self.world, (10, 10, 2),
                              Point3(-40, 60, 20), COLORS["grass_green"], "floating_island")
        star = self.builder.make_star(self.parent, Point3(-40, 60, 23), 3)
        self.stars.append(star)
        
        # Red coin locations
        red_coin_positions = [
            Point3(10, 10, 1), Point3(-10, 15, 1), Point3(20, 30, 5),
            Point3(-15, 45, 12), Point3(5, 55, 18), Point3(-25, 35, 1),
            Point3(35, 25, 1), Point3(0, 20, 1)
        ]
        for pos in red_coin_positions:
            coin = self.builder.make_coin(self.parent, pos, "red")
            self.coins.append(coin)
        
        # Regular coins scattered
        for i in range(50):
            x = random.uniform(-60, 60)
            y = random.uniform(-30, 80)
            coin = self.builder.make_coin(self.parent, Point3(x, y, 1))
            self.coins.append(coin)
        
        # Enemies
        enemy_positions = [
            Point3(15, 5, 1), Point3(-10, 25, 1), Point3(25, 40, 8),
            Point3(-20, 50, 1), Point3(40, 20, 1)
        ]
        for pos in enemy_positions:
            enemy = self.builder.make_enemy_goomba(self.parent, self.world, pos)
            self.enemies.append(enemy)
        
        return Vec3(0, -40, 2)  # Spawn
    
    def _gen_fortress_level(self, course: CourseData) -> Vec3:
        """Generate Whomp's Fortress style level"""
        # Base platform
        self.builder.make_box(self.parent, self.world, (60, 60, 3),
                              Point3(0, 0, -1.5), COLORS["stone_gray"], "base")
        
        # Main fortress tower
        self.builder.make_box(self.parent, self.world, (20, 20, 30),
                              Point3(0, 20, 15), COLORS["stone_gray"], "tower")
        
        # Spiral ramp around tower
        for i in range(12):
            angle = i * 30
            rad = math.radians(angle)
            x = math.cos(rad) * 15
            y = math.sin(rad) * 15 + 20
            z = i * 2.5 + 1
            self.builder.make_box(self.parent, self.world, (6, 6, 1),
                                  Point3(x, y, z), COLORS["stone_dark"], f"ramp_{i}")
        
        # Top platform with star
        self.builder.make_box(self.parent, self.world, (12, 12, 1),
                              Point3(0, 20, 31), COLORS["stone_gray"], "top")
        star = self.builder.make_star(self.parent, Point3(0, 20, 34), 1)
        self.stars.append(star)
        
        # Thwomp platforms
        for i in range(3):
            self.builder.make_box(self.parent, self.world, (5, 5, 1),
                                  Point3(-20 + i*10, -10, 5 + i*3), 
                                  COLORS["stone_dark"], f"thwomp_platform_{i}")
        
        # Floating platforms
        self.builder.make_box(self.parent, self.world, (8, 8, 1),
                              Point3(25, 30, 15), COLORS["stone_gray"], "float1")
        self.builder.make_box(self.parent, self.world, (8, 8, 1),
                              Point3(30, 40, 20), COLORS["stone_gray"], "float2")
        
        # Coins
        for i in range(40):
            x = random.uniform(-25, 25)
            y = random.uniform(-20, 50)
            z = random.uniform(1, 25)
            coin = self.builder.make_coin(self.parent, Point3(x, y, z))
            self.coins.append(coin)
        
        return Vec3(0, -25, 2)
    
    def _gen_water_level(self, course: CourseData) -> Vec3:
        """Generate Jolly Roger Bay style underwater level"""
        # Ocean floor
        self.builder.make_box(self.parent, self.world, (120, 120, 2),
                              Point3(0, 0, -20), COLORS["sand_yellow"], "seafloor")
        
        # Water volume (visual)
        self.builder.make_box(self.parent, self.world, (120, 120, 18),
                              Point3(0, 0, -10), COLORS["water_blue"], "water")
        
        # Beach/shore
        self.builder.make_box(self.parent, self.world, (40, 20, 3),
                              Point3(0, -50, 0), COLORS["sand_yellow"], "beach")
        
        # Sunken ship
        self.builder.make_box(self.parent, self.world, (15, 30, 8),
                              Point3(20, 20, -16), COLORS["wood_brown"], "ship_hull")
        self.builder.make_box(self.parent, self.world, (2, 20, 12),
                              Point3(20, 20, -10), COLORS["wood_brown"], "mast")
        
        # Star in ship
        star = self.builder.make_star(self.parent, Point3(20, 20, -12), 1)
        self.stars.append(star)
        
        # Underwater cave
        self.builder.make_box(self.parent, self.world, (20, 20, 10),
                              Point3(-30, 30, -18), COLORS["stone_dark"], "cave")
        
        # Pillars
        for i in range(4):
            x = -20 + i * 15
            self.builder.make_cylinder(self.parent, self.world, 2, 25,
                                       Point3(x, 40, -7), COLORS["stone_gray"], 8, f"pillar_{i}")
        
        # Clams with coins
        for i in range(5):
            x = random.uniform(-40, 40)
            y = random.uniform(-20, 50)
            coin = self.builder.make_coin(self.parent, Point3(x, y, -18))
            self.coins.append(coin)
        
        return Vec3(0, -45, 2)
    
    def _gen_snow_level(self, course: CourseData) -> Vec3:
        """Generate Cool Cool Mountain style snow level"""
        # Mountain base
        self.builder.make_box(self.parent, self.world, (100, 100, 3),
                              Point3(0, 0, -1.5), COLORS["snow_white"], "base")
        
        # Mountain peak (stacked)
        heights = [0, 8, 18, 30, 44]
        sizes = [80, 60, 40, 25, 12]
        for i, (h, s) in enumerate(zip(heights, sizes)):
            self.builder.make_box(self.parent, self.world, (s, s, 10),
                                  Point3(0, 20, h + 5), COLORS["snow_white"], f"peak_{i}")
        
        # Slide (series of ramps)
        slide_points = [
            (0, 20, 50), (-10, 10, 40), (-20, 0, 30), (-15, -15, 20),
            (0, -25, 10), (15, -30, 5), (20, -35, 2)
        ]
        for i, (x, y, z) in enumerate(slide_points[:-1]):
            nx, ny, nz = slide_points[i+1]
            length = math.sqrt((nx-x)**2 + (ny-y)**2)
            heading = math.degrees(math.atan2(ny-y, nx-x))
            self.builder.make_box(self.parent, self.world, (5, length, 0.5),
                                  Point3((x+nx)/2, (y+ny)/2, (z+nz)/2),
                                  COLORS["ice_blue"], f"slide_{i}")
        
        # Cabin at top
        self.builder.make_box(self.parent, self.world, (8, 8, 6),
                              Point3(0, 20, 53), COLORS["wood_brown"], "cabin")
        
        # Penguin area
        self.builder.make_box(self.parent, self.world, (15, 15, 1),
                              Point3(-30, -20, 0.5), COLORS["ice_blue"], "penguin_area")
        
        # Star at summit
        star = self.builder.make_star(self.parent, Point3(0, 20, 58), 1)
        self.stars.append(star)
        
        # Snowmen
        for i in range(3):
            x = random.uniform(-30, 30)
            y = random.uniform(-10, 40)
            self.builder.make_sphere(self.parent, self.world, 2,
                                     Point3(x, y, 2), COLORS["snow_white"], 0, f"snowman_{i}")
        
        # Coins
        for i in range(40):
            x = random.uniform(-40, 40)
            y = random.uniform(-30, 50)
            z = random.uniform(1, 45)
            coin = self.builder.make_coin(self.parent, Point3(x, y, z))
            self.coins.append(coin)
        
        return Vec3(0, -40, 2)
    
    def _gen_haunted_level(self, course: CourseData) -> Vec3:
        """Generate Big Boo's Haunt style haunted house"""
        # Courtyard ground
        self.builder.make_box(self.parent, self.world, (80, 80, 2),
                              Point3(0, 0, -1), COLORS["grass_dark"], "ground")
        
        # Main mansion
        self.builder.make_box(self.parent, self.world, (35, 25, 20),
                              Point3(0, 30, 10), (0.4, 0.35, 0.45, 1), "mansion")
        
        # Roof
        self.builder.make_box(self.parent, self.world, (40, 30, 3),
                              Point3(0, 30, 21.5), (0.3, 0.25, 0.35, 1), "roof")
        
        # Tower
        self.builder.make_box(self.parent, self.world, (8, 8, 30),
                              Point3(-12, 35, 15), (0.35, 0.3, 0.4, 1), "tower")
        
        # Entrance
        self.builder.make_box(self.parent, self.world, (10, 5, 12),
                              Point3(0, 18, 6), (0.3, 0.25, 0.35, 1), "entrance")
        
        # Graveyard
        for i in range(8):
            x = -25 + (i % 4) * 12
            y = -15 + (i // 4) * 10
            self.builder.make_box(self.parent, self.world, (1.5, 0.5, 3),
                                  Point3(x, y, 1.5), COLORS["stone_gray"], f"tombstone_{i}")
        
        # Merry-go-round platform (basement)
        self.builder.make_cylinder(self.parent, self.world, 12, 2,
                                   Point3(0, 30, -8), (0.5, 0.4, 0.5, 1), 12, "merry_go_round")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(0, 30, 25), 1)  # Rooftop
        self.stars.append(star)
        
        # Coins
        for i in range(30):
            x = random.uniform(-35, 35)
            y = random.uniform(-25, 45)
            coin = self.builder.make_coin(self.parent, Point3(x, y, 1))
            self.coins.append(coin)
        
        return Vec3(0, -30, 2)
    
    def _gen_cave_level(self, course: CourseData) -> Vec3:
        """Generate Hazy Maze Cave style underground level"""
        # Cave floor
        self.builder.make_box(self.parent, self.world, (150, 150, 3),
                              Point3(0, 0, -1.5), COLORS["stone_dark"], "floor")
        
        # Ceiling (far above)
        self.builder.make_box(self.parent, self.world, (150, 150, 3),
                              Point3(0, 0, 40), COLORS["stone_dark"], "ceiling")
        
        # Maze walls
        maze_walls = [
            ((4, 40, 8), (20, 0, 4)),
            ((4, 40, 8), (-20, 0, 4)),
            ((40, 4, 8), (0, 20, 4)),
            ((40, 4, 8), (0, -20, 4)),
            ((4, 30, 8), (40, 10, 4)),
            ((30, 4, 8), (10, 40, 4)),
            ((4, 25, 8), (-35, -15, 4)),
        ]
        for i, (size, pos) in enumerate(maze_walls):
            self.builder.make_box(self.parent, self.world, size,
                                  Point3(*pos), COLORS["stone_gray"], f"wall_{i}")
        
        # Toxic maze area (colored differently)
        self.builder.make_box(self.parent, self.world, (40, 40, 0.5),
                              Point3(-30, 40, 0.25), (0.4, 0.6, 0.3, 0.8), "toxic_floor")
        
        # Underground lake with Dorrie
        self.builder.make_box(self.parent, self.world, (50, 50, 8),
                              Point3(40, 40, -4), COLORS["water_deep"], "lake")
        
        # Elevator shafts
        self.builder.make_box(self.parent, self.world, (6, 6, 35),
                              Point3(-50, -30, 17.5), COLORS["stone_dark"], "shaft")
        
        # Metal cap area entrance
        self.builder.make_box(self.parent, self.world, (8, 8, 1),
                              Point3(-50, 0, 5), COLORS["stone_gray"], "metal_entrance")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(40, 40, 2), 1)  # Lake area
        self.stars.append(star)
        
        # Coins throughout maze
        for i in range(60):
            x = random.uniform(-60, 60)
            y = random.uniform(-40, 60)
            coin = self.builder.make_coin(self.parent, Point3(x, y, 1))
            self.coins.append(coin)
        
        return Vec3(0, -60, 2)
    
    def _gen_lava_level(self, course: CourseData) -> Vec3:
        """Generate Lethal Lava Land style volcanic level"""
        # Lava sea
        self.builder.make_box(self.parent, self.world, (150, 150, 5),
                              Point3(0, 0, -2.5), COLORS["lava_orange"], "lava")
        
        # Safe platforms scattered
        platform_data = [
            ((15, 15, 3), (0, 0, 1.5)),
            ((10, 10, 3), (25, 10, 1.5)),
            ((10, 10, 3), (-25, 15, 1.5)),
            ((12, 8, 3), (10, 30, 1.5)),
            ((8, 12, 3), (-15, -20, 1.5)),
            ((20, 6, 3), (0, -35, 1.5)),
            ((6, 20, 3), (40, 0, 1.5)),
        ]
        for i, (size, pos) in enumerate(platform_data):
            self.builder.make_box(self.parent, self.world, size,
                                  Point3(*pos), COLORS["stone_dark"], f"platform_{i}")
        
        # Volcano
        for i in range(5):
            size = 30 - i * 5
            self.builder.make_box(self.parent, self.world, (size, size, 6),
                                  Point3(0, 50, i * 6 + 3), COLORS["stone_dark"], f"volcano_{i}")
        
        # Volcano crater (top)
        self.builder.make_box(self.parent, self.world, (8, 8, 2),
                              Point3(0, 50, 32), COLORS["lava_red"], "crater")
        
        # Bully arena
        self.builder.make_cylinder(self.parent, self.world, 15, 2,
                                   Point3(-35, 35, 1), COLORS["stone_gray"], 12, "bully_arena")
        
        # Rolling log
        self.builder.make_cylinder(self.parent, self.world, 2, 20,
                                   Point3(30, 30, 3), COLORS["wood_brown"], 8, "log")
        
        # Puzzle platform (8 piece puzzle ref)
        self.builder.make_box(self.parent, self.world, (20, 20, 1),
                              Point3(-40, -30, 1), COLORS["stone_gray"], "puzzle")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(-35, 35, 5), 1)  # Bully arena
        self.stars.append(star)
        star2 = self.builder.make_star(self.parent, Point3(0, 50, 35), 5)  # Volcano top
        self.stars.append(star2)
        
        # Coins on platforms
        for i in range(35):
            plat = random.choice(platform_data)
            px, py, pz = plat[1]
            sx, sy, _ = plat[0]
            x = px + random.uniform(-sx/3, sx/3)
            y = py + random.uniform(-sy/3, sy/3)
            coin = self.builder.make_coin(self.parent, Point3(x, y, pz + 2))
            self.coins.append(coin)
        
        return Vec3(0, 0, 4)
    
    def _gen_desert_level(self, course: CourseData) -> Vec3:
        """Generate Shifting Sand Land style desert level"""
        # Sand ground
        self.builder.make_box(self.parent, self.world, (200, 200, 3),
                              Point3(0, 0, -1.5), COLORS["sand_yellow"], "sand")
        
        # Quicksand pit (visual - darker sand)
        self.builder.make_box(self.parent, self.world, (30, 30, 0.5),
                              Point3(0, 0, 0.3), COLORS["sand_dark"], "quicksand")
        
        # Main pyramid
        for i in range(8):
            size = 50 - i * 5
            self.builder.make_box(self.parent, self.world, (size, size, 5),
                                  Point3(0, 40, i * 5 + 2.5), COLORS["pyramid_tan"], f"pyramid_{i}")
        
        # Pyramid entrance
        self.builder.make_box(self.parent, self.world, (6, 3, 8),
                              Point3(0, 15, 4), COLORS["stone_dark"], "pyramid_entrance")
        
        # Oasis
        self.builder.make_cylinder(self.parent, self.world, 10, 1,
                                   Point3(-40, -30, 0.5), COLORS["water_blue"], 12, "oasis")
        # Palm trees at oasis
        for angle in [0, 120, 240]:
            rad = math.radians(angle)
            x = -40 + math.cos(rad) * 12
            y = -30 + math.sin(rad) * 12
            self.builder.make_cylinder(self.parent, self.world, 0.8, 8,
                                       Point3(x, y, 4), COLORS["wood_brown"], 6, "palm_trunk")
            self.builder.make_box(self.parent, self.world, (5, 5, 1),
                                  Point3(x, y, 9), COLORS["grass_green"], "palm_top")
        
        # Four pillars
        pillar_positions = [(30, 30), (-30, 30), (30, -30), (-30, -30)]
        for i, (x, y) in enumerate(pillar_positions):
            self.builder.make_box(self.parent, self.world, (4, 4, 15),
                                  Point3(x, y, 7.5), COLORS["pyramid_tan"], f"pillar_{i}")
        
        # Flying carpet path (platforms)
        carpet_y = [-20, -10, 0, 10, 20]
        for i, cy in enumerate(carpet_y):
            self.builder.make_box(self.parent, self.world, (5, 5, 0.5),
                                  Point3(50, cy, 8 + i), COLORS["mario_red"], f"carpet_{i}")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(0, 40, 45), 2)  # Pyramid top
        self.stars.append(star)
        
        # Coins scattered
        for i in range(50):
            x = random.uniform(-70, 70)
            y = random.uniform(-50, 80)
            # Avoid quicksand center
            if abs(x) < 12 and abs(y) < 12:
                continue
            coin = self.builder.make_coin(self.parent, Point3(x, y, 1))
            self.coins.append(coin)
        
        return Vec3(0, -60, 2)
    
    def _gen_mechanical_level(self, course: CourseData) -> Vec3:
        """Generate Tick Tock Clock / Wet Dry World style mechanical level"""
        # Base platform
        self.builder.make_box(self.parent, self.world, (80, 80, 3),
                              Point3(0, 0, -1.5), (0.5, 0.5, 0.55, 1), "base")
        
        # Central clock tower / mechanism
        self.builder.make_cylinder(self.parent, self.world, 8, 50,
                                   Point3(0, 0, 25), COLORS["stone_gray"], 12, "tower")
        
        # Rotating platforms around tower
        for i in range(8):
            angle = i * 45
            rad = math.radians(angle)
            x = math.cos(rad) * 15
            y = math.sin(rad) * 15
            z = 5 + i * 5
            self.builder.make_box(self.parent, self.world, (8, 4, 1),
                                  Point3(x, y, z), (0.6, 0.55, 0.5, 1), f"rot_plat_{i}")
        
        # Moving bars / pendulums (static for now)
        self.builder.make_box(self.parent, self.world, (2, 15, 2),
                              Point3(20, 0, 20), COLORS["stone_dark"], "pendulum1")
        self.builder.make_box(self.parent, self.world, (2, 15, 2),
                              Point3(-20, 0, 30), COLORS["stone_dark"], "pendulum2")
        
        # Conveyor belt platform
        self.builder.make_box(self.parent, self.world, (30, 6, 1),
                              Point3(0, 25, 15), (0.4, 0.4, 0.45, 1), "conveyor")
        
        # Cage at top
        self.builder.make_box(self.parent, self.world, (10, 10, 8),
                              Point3(0, 0, 54), COLORS["stone_gray"], "cage")
        
        # Water level markers (for Wet Dry World style)
        for h in [5, 15, 25, 35]:
            self.builder.make_box(self.parent, self.world, (60, 60, 0.3),
                                  Point3(0, 0, h), (*COLORS["water_blue"][:3], 0.3), f"water_{h}")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(0, 0, 58), 1)
        self.stars.append(star)
        
        # Coins on platforms
        for i in range(8):
            angle = i * 45
            rad = math.radians(angle)
            x = math.cos(rad) * 15
            y = math.sin(rad) * 15
            z = 6 + i * 5
            coin = self.builder.make_coin(self.parent, Point3(x, y, z))
            self.coins.append(coin)
        
        return Vec3(0, -35, 2)
    
    def _gen_mountain_level(self, course: CourseData) -> Vec3:
        """Generate Tall Tall Mountain style vertical level"""
        # Base ground
        self.builder.make_box(self.parent, self.world, (100, 100, 3),
                              Point3(0, 0, -1.5), COLORS["grass_green"], "ground")
        
        # Mountain core
        heights = [0, 10, 22, 36, 52, 70]
        sizes = [60, 50, 38, 28, 18, 10]
        for i, (h, s) in enumerate(zip(heights, sizes)):
            self.builder.make_box(self.parent, self.world, (s, s, 12),
                                  Point3(0, 0, h + 6), COLORS["dirt_brown"], f"mountain_{i}")
        
        # Summit platform
        self.builder.make_box(self.parent, self.world, (12, 12, 2),
                              Point3(0, 0, 83), COLORS["stone_gray"], "summit")
        
        # Winding path/ledges
        path_points = [
            ((-25, 0, 5), (8, 4)),
            ((-20, 15, 12), (6, 6)),
            ((0, 25, 20), (8, 4)),
            ((20, 15, 28), (6, 6)),
            ((15, -5, 38), (8, 4)),
            ((-5, -20, 48), (6, 6)),
            ((-15, 0, 58), (8, 4)),
            ((5, 10, 68), (6, 6)),
        ]
        for i, (pos, size) in enumerate(path_points):
            self.builder.make_box(self.parent, self.world, (*size, 2),
                                  Point3(*pos), COLORS["stone_gray"], f"ledge_{i}")
        
        # Mushroom platforms
        mushroom_positions = [(-30, 20, 25), (30, -15, 35), (-25, -25, 50)]
        for i, pos in enumerate(mushroom_positions):
            # Stem
            self.builder.make_cylinder(self.parent, self.world, 1.5, 6,
                                       Point3(pos[0], pos[1], pos[2] - 3), 
                                       COLORS["snow_white"], 8, f"stem_{i}")
            # Cap
            self.builder.make_cylinder(self.parent, self.world, 5, 2,
                                       Point3(pos[0], pos[1], pos[2] + 1),
                                       COLORS["mario_red"], 8, f"cap_{i}")
        
        # Waterfall (visual)
        self.builder.make_box(self.parent, self.world, (4, 1, 40),
                              Point3(20, 0, 40), COLORS["water_blue"], "waterfall")
        
        # Log bridge
        self.builder.make_cylinder(self.parent, self.world, 1, 20,
                                   Point3(-10, 30, 65), COLORS["wood_brown"], 6, "log_bridge")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(0, 0, 87), 1)  # Summit
        self.stars.append(star)
        star2 = self.builder.make_star(self.parent, Point3(-30, 20, 28), 6)  # Mushroom
        self.stars.append(star2)
        
        # Coins along path
        for pos, _ in path_points:
            coin = self.builder.make_coin(self.parent, Point3(pos[0], pos[1], pos[2] + 2))
            self.coins.append(coin)
        
        return Vec3(0, -40, 2)
    
    def _gen_sky_level(self, course: CourseData) -> Vec3:
        """Generate Rainbow Ride style sky level"""
        # No ground - sky void
        # Just floating platforms and rainbow paths
        
        # Starting platform
        self.builder.make_box(self.parent, self.world, (15, 15, 2),
                              Point3(0, 0, 0), COLORS["cloud_white"], "start")
        
        # Rainbow bridge sections
        rainbow_colors = [
            COLORS["rainbow_red"], COLORS["rainbow_orange"], COLORS["rainbow_yellow"],
            COLORS["rainbow_green"], COLORS["rainbow_blue"], COLORS["rainbow_purple"]
        ]
        for i in range(12):
            x = i * 8
            y = math.sin(i * 0.5) * 10
            z = 5 + i * 2
            color = rainbow_colors[i % 6]
            self.builder.make_box(self.parent, self.world, (6, 4, 0.5),
                                  Point3(x, y, z), color, f"rainbow_{i}")
        
        # Flying ship
        self.builder.make_box(self.parent, self.world, (20, 8, 3),
                              Point3(60, 30, 35), COLORS["wood_brown"], "ship_hull")
        self.builder.make_box(self.parent, self.world, (2, 2, 15),
                              Point3(55, 30, 42), COLORS["wood_brown"], "mast")
        self.builder.make_box(self.parent, self.world, (8, 1, 8),
                              Point3(55, 30, 50), COLORS["cloud_white"], "sail")
        
        # Big house in the sky
        self.builder.make_box(self.parent, self.world, (25, 20, 15),
                              Point3(-50, 50, 45), COLORS["brick_red"], "house")
        self.builder.make_box(self.parent, self.world, (28, 23, 3),
                              Point3(-50, 50, 54), COLORS["wood_brown"], "roof")
        
        # Swing platforms
        swing_positions = [(20, -20, 15), (35, -15, 20), (50, -10, 25)]
        for i, pos in enumerate(swing_positions):
            self.builder.make_box(self.parent, self.world, (5, 5, 1),
                                  Point3(*pos), COLORS["wood_brown"], f"swing_{i}")
        
        # Cloud platforms
        cloud_positions = [
            (-20, 20, 10), (-30, 35, 18), (40, 40, 25), 
            (20, 60, 40), (-40, 10, 30), (0, 45, 50)
        ]
        for i, pos in enumerate(cloud_positions):
            self.builder.make_box(self.parent, self.world, (10, 8, 2),
                                  Point3(*pos), COLORS["cloud_white"], f"cloud_{i}")
        
        # Maze of clouds
        for i in range(5):
            for j in range(5):
                if random.random() > 0.3:
                    x = -60 + i * 12
                    y = 70 + j * 10
                    z = 30 + random.uniform(-3, 3)
                    self.builder.make_box(self.parent, self.world, (8, 6, 1),
                                          Point3(x, y, z), COLORS["cloud_white"], f"maze_{i}_{j}")
        
        # Stars
        star = self.builder.make_star(self.parent, Point3(60, 30, 42), 1)  # Ship
        self.stars.append(star)
        star2 = self.builder.make_star(self.parent, Point3(-50, 50, 58), 2)  # House
        self.stars.append(star2)
        
        # Coins on rainbow
        for i in range(12):
            x = i * 8
            y = math.sin(i * 0.5) * 10
            z = 6 + i * 2
            coin = self.builder.make_coin(self.parent, Point3(x, y, z))
            self.coins.append(coin)
        
        return Vec3(0, 0, 3)
    
    def _add_course_stars(self, course: CourseData):
        """Add star spawns for a course (7 stars per course)"""
        # Stars are placed by the individual level generators
        # This adds any remaining star logic
        pass
    
    def generate_test_level(self) -> Vec3:
        """Generate a simple test level"""
        # Ground
        self.builder.make_box(self.parent, self.world, (100, 100, 2),
                              Point3(0, 0, -1), COLORS["grass_green"], "ground")
        
        # Test platforms
        self.builder.make_box(self.parent, self.world, (10, 10, 2),
                              Point3(20, 0, 2), COLORS["stone_gray"], "plat1")
        self.builder.make_box(self.parent, self.world, (10, 10, 2),
                              Point3(35, 5, 5), COLORS["stone_gray"], "plat2")
        self.builder.make_box(self.parent, self.world, (10, 10, 2),
                              Point3(45, 15, 9), COLORS["stone_gray"], "plat3")
        
        # Ramp
        self.builder.make_box(self.parent, self.world, (10, 20, 1),
                              Point3(-20, 10, 3), COLORS["dirt_brown"], "ramp")
        
        # Tower
        self.builder.make_box(self.parent, self.world, (8, 8, 20),
                              Point3(0, 30, 10), COLORS["stone_gray"], "tower")
        
        # Test star
        star = self.builder.make_star(self.parent, Point3(0, 30, 22), 1)
        self.stars.append(star)
        
        # Coins
        for i in range(20):
            x = random.uniform(-30, 30)
            y = random.uniform(-20, 40)
            coin = self.builder.make_coin(self.parent, Point3(x, y, 1))
            self.coins.append(coin)
        
        return Vec3(0, -20, 2)

# ═══════════════════════════════════════════════════════════════════════════════════
# PLAYER CHARACTER
# ═══════════════════════════════════════════════════════════════════════════════════

class Player:
    """Mario player character with full moveset"""
    
    def __init__(self, parent: NodePath, world: BulletWorld, config: GameConfig):
        self.config = config
        self.world = world
        
        # Physics
        self.radius = 0.5
        self.height = 1.0
        shape = BulletCapsuleShape(self.radius, self.height, ZUp)
        
        self.char = BulletCharacterControllerNode(shape, 0.4, "mario")
        self.char.setGravity(config.gravity)
        self.char.setMaxSlope(50.0)
        self.char.setJumpSpeed(config.jump_power)
        
        self.node = parent.attachNewNode(self.char)
        self.node.setCollideMask(BitMask32.allOn())
        world.attachCharacter(self.char)
        
        # State
        self.velocity = Vec3(0, 0, 0)
        self.vertical_vel = 0.0
        self.move_state = MoveState.IDLE
        self.facing_angle = 0.0
        
        # Jump tracking
        self.jump_count = 0
        self.jump_timer = 0.0
        self.last_ground_time = 0.0
        self.coyote_time = 0.1
        self.jump_buffer = 0.0
        self.jump_buffer_time = 0.15
        
        # Movement input
        self.input_dir = Vec3(0, 0, 0)
        self.want_jump = False
        self.want_dive = False
        self.want_ground_pound = False
        self.is_running = False
        
        # Stats
        self.health = 8
        self.max_health = 8
        self.coins = 0
        self.lives = 4
        
        # Caps
        self.has_wing_cap = False
        self.has_metal_cap = False
        self.has_vanish_cap = False
        self.cap_timer = 0.0
        
        # Create visuals
        self._create_visuals()
    
    def _create_visuals(self):
        """Create Mario visual representation"""
        self.vis = self.node.attachNewNode("mario_vis")
        self.vis.setZ(-1.0)  # Offset to align with feet
        
        cm = CardMaker("part")
        
        # Colors
        c_red = COLORS["mario_red"]
        c_blue = COLORS["mario_blue"]
        c_skin = COLORS["mario_skin"]
        c_brown = COLORS["mario_brown"]
        c_yellow = COLORS["mario_yellow"]
        
        # Shoes
        cm.setFrame(-0.15, 0.15, -0.15, 0.15)
        for x_off in [-0.2, 0.2]:
            shoe = self.vis.attachNewNode(cm.generate())
            shoe.setColor(c_brown)
            shoe.setPos(x_off, 0, 0.1)
            shoe.setScale(1, 1, 0.6)
        
        # Blue overalls/pants
        cm.setFrame(-0.3, 0.3, -0.15, 0.15)
        pants = self.vis.attachNewNode(cm.generate())
        pants.setColor(c_blue)
        pants.setPos(0, 0, 0.4)
        pants.setP(-90)
        pants.setScale(1, 1, 0.8)
        
        # Red shirt
        cm.setFrame(-0.35, 0.35, -0.15, 0.15)
        shirt = self.vis.attachNewNode(cm.generate())
        shirt.setColor(c_red)
        shirt.setPos(0, 0, 0.8)
        shirt.setP(-90)
        shirt.setScale(1, 1, 0.6)
        
        # Arms
        cm.setFrame(-0.1, 0.1, -0.2, 0.2)
        for x_off, color in [(-0.4, c_red), (0.4, c_red)]:
            arm = self.vis.attachNewNode(cm.generate())
            arm.setColor(color)
            arm.setPos(x_off, 0, 0.8)
            arm.setScale(0.8, 1, 0.6)
        
        # Hands
        cm.setFrame(-0.08, 0.08, -0.08, 0.08)
        for x_off in [-0.45, 0.45]:
            hand = self.vis.attachNewNode(cm.generate())
            hand.setColor(c_skin)
            hand.setPos(x_off, 0, 0.6)
        
        # Head
        cm.setFrame(-0.25, 0.25, -0.2, 0.2)
        head = self.vis.attachNewNode(cm.generate())
        head.setColor(c_skin)
        head.setPos(0, 0, 1.2)
        head.setP(-90)
        head.setScale(1, 1, 0.6)
        
        # Cap
        cm.setFrame(-0.28, 0.28, -0.15, 0.15)
        cap = self.vis.attachNewNode(cm.generate())
        cap.setColor(c_red)
        cap.setPos(0, 0.05, 1.45)
        cap.setP(-90)
        cap.setScale(1, 1, 0.3)
        self.cap_vis = cap
        
        # Cap emblem (M)
        cm.setFrame(-0.1, 0.1, -0.1, 0.1)
        emblem = self.vis.attachNewNode(cm.generate())
        emblem.setColor(c_skin)  # White-ish
        emblem.setPos(0, -0.2, 1.35)
        
        # Nose
        cm.setFrame(-0.08, 0.08, -0.08, 0.08)
        nose = self.vis.attachNewNode(cm.generate())
        nose.setColor(c_skin)
        nose.setPos(0, -0.25, 1.25)
        
        # Mustache
        cm.setFrame(-0.15, 0.15, -0.05, 0.05)
        stache = self.vis.attachNewNode(cm.generate())
        stache.setColor(c_brown)
        stache.setPos(0, -0.22, 1.15)
        
        # Eyes (simple dots)
        cm.setFrame(-0.04, 0.04, -0.04, 0.04)
        for x_off in [-0.08, 0.08]:
            eye = self.vis.attachNewNode(cm.generate())
            eye.setColor(0.2, 0.4, 0.8, 1)  # Blue eyes
            eye.setPos(x_off, -0.2, 1.3)
    
    def set_position(self, pos: Vec3):
        """Teleport player to position"""
        self.node.setPos(pos)
        self.velocity = Vec3(0, 0, 0)
        self.vertical_vel = 0.0
    
    def get_position(self) -> Vec3:
        return self.node.getPos()
    
    def update(self, dt: float, camera_heading: float):
        """Update player physics and state"""
        # Ground check
        is_grounded = self.char.isOnGround()
        current_time = globalClock.getFrameTime()
        
        if is_grounded:
            self.last_ground_time = current_time
            if self.move_state in (MoveState.FALLING, MoveState.JUMPING, 
                                   MoveState.DOUBLE_JUMP, MoveState.TRIPLE_JUMP):
                self._land()
        
        # Coyote time check
        can_jump = is_grounded or (current_time - self.last_ground_time < self.coyote_time)
        
        # Jump buffer
        if self.want_jump:
            self.jump_buffer = self.jump_buffer_time
        self.jump_buffer = max(0, self.jump_buffer - dt)
        
        # Process movement input
        self._process_movement(dt, camera_heading, is_grounded)
        
        # Process jump
        if self.jump_buffer > 0 and can_jump and is_grounded:
            self._perform_jump()
            self.jump_buffer = 0
        
        # Gravity when airborne
        if not is_grounded:
            self.vertical_vel -= self.config.gravity * dt
            self.vertical_vel = max(self.vertical_vel, -self.config.max_fall_speed)
            
            if self.vertical_vel < 0 and self.move_state not in (MoveState.GROUND_POUND,):
                self.move_state = MoveState.FALLING
        else:
            self.vertical_vel = 0
        
        # Apply movement
        final_vel = Vec3(self.velocity.x, self.velocity.y, self.vertical_vel)
        self.char.setLinearMovement(final_vel, True)
        
        # Update visual rotation
        if self.velocity.length() > 0.5:
            target_angle = math.degrees(math.atan2(self.velocity.y, self.velocity.x)) - 90
            angle_delta = angle_diff(self.facing_angle, target_angle)
            self.facing_angle += angle_delta * min(1, dt * 10)
        self.vis.setH(self.facing_angle)
        
        # Update state
        self._update_move_state(is_grounded)
        
        # Cap timers
        if self.cap_timer > 0:
            self.cap_timer -= dt
            if self.cap_timer <= 0:
                self.has_wing_cap = False
                self.has_metal_cap = False
                self.has_vanish_cap = False
        
        # Reset input flags
        self.want_jump = False
        self.want_dive = False
    
    def _process_movement(self, dt: float, camera_heading: float, is_grounded: bool):
        """Process movement input and update velocity"""
        # Rotate input by camera
        if self.input_dir.lengthSquared() > 0.01:
            self.input_dir.normalize()
            rad = math.radians(camera_heading)
            sin_a, cos_a = math.sin(rad), math.cos(rad)
            rot_x = self.input_dir.x * cos_a - self.input_dir.y * sin_a
            rot_y = self.input_dir.x * sin_a + self.input_dir.y * cos_a
            target_dir = Vec3(rot_x, rot_y, 0)
        else:
            target_dir = Vec3(0, 0, 0)
        
        # Determine target speed
        if is_grounded:
            target_speed = self.config.run_speed if self.is_running else self.config.walk_speed
            accel = self.config.ground_accel
            friction = self.config.ground_friction
        else:
            target_speed = self.config.walk_speed * 0.8
            accel = self.config.air_accel
            friction = self.config.air_friction
        
        # Calculate target velocity
        if target_dir.lengthSquared() > 0.01:
            target_vel = target_dir * target_speed
            
            # Accelerate towards target
            diff = target_vel - Vec3(self.velocity.x, self.velocity.y, 0)
            change_mag = diff.length()
            if change_mag > 0.001:
                dir_change = diff / change_mag
                actual_change = min(change_mag, accel * dt)
                self.velocity.x += dir_change.x * actual_change
                self.velocity.y += dir_change.y * actual_change
        else:
            # Apply friction
            speed = Vec3(self.velocity.x, self.velocity.y, 0).length()
            if speed > 0.01:
                drop = friction * dt
                new_speed = max(0, speed - drop)
                ratio = new_speed / speed
                self.velocity.x *= ratio
                self.velocity.y *= ratio
            else:
                self.velocity.x = 0
                self.velocity.y = 0
    
    def _perform_jump(self):
        """Execute a jump based on current combo"""
        current_time = globalClock.getFrameTime()
        speed = Vec3(self.velocity.x, self.velocity.y, 0).length()
        
        # Check for jump combo continuation
        if current_time - self.jump_timer < self.config.jump_window and speed > 5:
            self.jump_count += 1
        else:
            self.jump_count = 1
        
        self.jump_timer = current_time
        
        # Determine jump power based on combo
        if self.jump_count >= 3:
            power = self.config.triple_jump_power
            self.move_state = MoveState.TRIPLE_JUMP
            self.jump_count = 0  # Reset
        elif self.jump_count == 2:
            power = self.config.double_jump_power
            self.move_state = MoveState.DOUBLE_JUMP
        else:
            power = self.config.jump_power
            self.move_state = MoveState.JUMPING
        
        self.vertical_vel = power
    
    def _land(self):
        """Called when landing on ground"""
        self.move_state = MoveState.IDLE
        self.vertical_vel = 0
    
    def _update_move_state(self, is_grounded: bool):
        """Update movement state based on conditions"""
        if is_grounded:
            speed = Vec3(self.velocity.x, self.velocity.y, 0).length()
            if speed < 0.5:
                self.move_state = MoveState.IDLE
            elif self.is_running and speed > 10:
                self.move_state = MoveState.RUNNING
            else:
                self.move_state = MoveState.WALKING
    
    def collect_coin(self, value: int = 1):
        """Collect a coin"""
        self.coins += value
        # Heal on certain thresholds
        if self.coins % 50 == 0:
            self.health = min(self.health + 1, self.max_health)
    
    def take_damage(self, amount: int = 1):
        """Take damage"""
        if self.has_metal_cap:
            return  # Invincible
        
        self.health -= amount
        if self.health <= 0:
            self._die()
    
    def _die(self):
        """Handle player death"""
        self.lives -= 1
        self.health = self.max_health
        self.coins = 0
        # Respawn handled by game

# ═══════════════════════════════════════════════════════════════════════════════════
# CAMERA CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════════

class CameraController:
    """Lakitu-style camera system"""
    
    def __init__(self, camera: NodePath, config: GameConfig):
        self.camera = camera
        self.config = config
        
        self.target: Optional[NodePath] = None
        self.pivot = NodePath("cam_pivot")
        
        self.distance = config.cam_distance
        self.height = config.cam_height
        self.heading = 0.0
        self.pitch = -15.0
        
        self.smooth_pos = Vec3(0, 0, 0)
        self.mouse_sensitivity = 0.15
    
    def set_target(self, target: NodePath):
        """Set camera follow target"""
        self.target = target
        self.smooth_pos = target.getPos()
    
    def update(self, dt: float, mouse_delta: Vec2 = Vec2(0, 0)):
        """Update camera position and rotation"""
        if not self.target:
            return
        
        # Mouse rotation
        self.heading -= mouse_delta.x * self.config.cam_rotate_speed * dt
        self.pitch = clamp(self.pitch - mouse_delta.y * 50 * dt, -60, 30)
        
        # Smooth follow position
        target_pos = self.target.getPos()
        diff = target_pos - self.smooth_pos
        self.smooth_pos += diff * (self.config.cam_smooth * dt)
        
        # Calculate camera position
        rad_h = math.radians(self.heading)
        rad_p = math.radians(self.pitch)
        
        # Offset from target
        cam_offset = Vec3(
            -math.sin(rad_h) * math.cos(rad_p) * self.distance,
            -math.cos(rad_h) * math.cos(rad_p) * self.distance,
            -math.sin(rad_p) * self.distance + self.height
        )
        
        cam_pos = self.smooth_pos + cam_offset
        
        # Apply to camera
        self.camera.setPos(cam_pos)
        self.camera.lookAt(self.smooth_pos + Vec3(0, 0, 1))
    
    def get_heading(self) -> float:
        return self.heading

# ═══════════════════════════════════════════════════════════════════════════════════
# UI SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════

class UIManager:
    """Handles all UI elements"""
    
    def __init__(self, aspect2d: NodePath):
        self.root = aspect2d.attachNewNode("ui_root")
        
        # UI layers
        self.title_layer = self.root.attachNewNode("title")
        self.file_layer = self.root.attachNewNode("files")
        self.hud_layer = self.root.attachNewNode("hud")
        self.pause_layer = self.root.attachNewNode("pause")
        self.star_layer = self.root.attachNewNode("star_get")
        
        # Initially hide non-title layers
        self.file_layer.hide()
        self.hud_layer.hide()
        self.pause_layer.hide()
        self.star_layer.hide()
        
        # HUD elements
        self.coin_text: Optional[NodePath] = None
        self.star_text: Optional[NodePath] = None
        self.health_display: Optional[NodePath] = None
        self.lives_text: Optional[NodePath] = None
        self.course_text: Optional[NodePath] = None
        self.combo_text: Optional[NodePath] = None
        
        # File select state
        self.selected_file = 0
        self.file_cursor: Optional[NodePath] = None
        
        self._build_all_ui()
    
    def _build_all_ui(self):
        """Build all UI screens"""
        self._build_title()
        self._build_file_select()
        self._build_hud()
        self._build_pause()
        self._build_star_get()
    
    def _create_text(self, text: str, pos: Tuple[float, float], scale: float = 0.07,
                     color: Tuple = COLORS["ui_white"], align: int = TextNode.ACenter,
                     parent: Optional[NodePath] = None) -> NodePath:
        """Create a text node"""
        tn = TextNode("text")
        tn.setText(text)
        tn.setTextColor(*color)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(*COLORS["ui_shadow"])
        tn.setAlign(align)
        
        np = NodePath(tn)
        np.setScale(scale)
        np.setPos(pos[0], 0, pos[1])
        
        if parent:
            np.reparentTo(parent)
        
        return np
    
    def _build_title(self):
        """Build title screen"""
        # Main title
        self._create_text("ULTRA MARIO", (0, 0.5), 0.2, COLORS["mario_red"], parent=self.title_layer)
        self._create_text("3D BROS.", (0, 0.3), 0.15, COLORS["mario_blue"], parent=self.title_layer)
        self._create_text("120 STARS EDITION", (0, 0.12), 0.06, COLORS["ui_yellow"], parent=self.title_layer)
        
        # Press start blink
        self.start_text = self._create_text("— PRESS SPACE —", (0, -0.4), 0.07, parent=self.title_layer)
        
        # Animate
        blink = Sequence(
            LerpColorScaleInterval(self.start_text, 0.5, Vec4(1, 1, 0.3, 1)),
            LerpColorScaleInterval(self.start_text, 0.5, Vec4(1, 1, 1, 1))
        )
        blink.loop()
        
        # Credits
        self._create_text("Team Flames / Samsoft", (0, -0.8), 0.04, COLORS["ui_white"], parent=self.title_layer)
    
    def _build_file_select(self):
        """Build file select screen"""
        self._create_text("— SELECT FILE —", (0, 0.7), 0.1, COLORS["ui_yellow"], parent=self.file_layer)
        
        # File slots
        for i in range(4):
            y = 0.4 - i * 0.25
            letter = chr(65 + i)
            
            # File box background would go here
            self._create_text(f"MARIO {letter}", (-0.4, y), 0.07, 
                            align=TextNode.ALeft, parent=self.file_layer)
            
            # Star count (placeholder)
            stars = random.randint(0, 120)
            self._create_text(f"★ {stars}", (0.2, y), 0.07, COLORS["ui_yellow"],
                            align=TextNode.ALeft, parent=self.file_layer)
        
        # Cursor
        self.file_cursor = self._create_text("▶", (-0.55, 0.4), 0.08, COLORS["mario_red"],
                                             parent=self.file_layer)
        
        # Controls hint
        self._create_text("[W/S] Select   [SPACE] Start   [DEL] Erase", (0, -0.8), 0.05,
                         parent=self.file_layer)
    
    def _build_hud(self):
        """Build in-game HUD"""
        # Top left: Lives
        self.lives_text = self._create_text("× 4", (-1.15, 0.85), 0.06,
                                           align=TextNode.ALeft, parent=self.hud_layer)
        self._create_text("MARIO", (-1.3, 0.85), 0.05, COLORS["mario_red"],
                         align=TextNode.ALeft, parent=self.hud_layer)
        
        # Top middle: Stars
        self.star_text = self._create_text("★ × 0", (0, 0.85), 0.06, COLORS["ui_yellow"],
                                          parent=self.hud_layer)
        
        # Top right: Coins
        self.coin_text = self._create_text("¢ × 0", (1.0, 0.85), 0.06, COLORS["coin_gold"],
                                          align=TextNode.ARight, parent=self.hud_layer)
        
        # Health meter (pie segments)
        self.health_segments = []
        for i in range(8):
            angle = i * 45
            x = -1.2 + math.cos(math.radians(angle)) * 0.08
            y = 0.7 + math.sin(math.radians(angle)) * 0.08
            seg = self._create_text("●", (x, y), 0.04, COLORS["mario_blue"],
                                   parent=self.hud_layer)
            self.health_segments.append(seg)
        
        # Course name
        self.course_text = self._create_text("", (0, -0.85), 0.05, parent=self.hud_layer)
        
        # Combo display
        self.combo_text = self._create_text("", (0, 0.6), 0.08, COLORS["ui_yellow"],
                                           parent=self.hud_layer)
        
        # Controls hint
        self._create_text("WASD: Move | SPACE: Jump | SHIFT: Run | ESC: Exit", 
                         (0, -0.95), 0.035, parent=self.hud_layer)
    
    def _build_pause(self):
        """Build pause menu"""
        self._create_text("PAUSED", (0, 0.3), 0.15, parent=self.pause_layer)
        self._create_text("SPACE: Resume", (0, 0), 0.06, parent=self.pause_layer)
        self._create_text("ESC: Exit Course", (0, -0.15), 0.06, parent=self.pause_layer)
    
    def _build_star_get(self):
        """Build star get celebration screen"""
        self._create_text("STAR GET!", (0, 0.3), 0.2, COLORS["ui_yellow"], parent=self.star_layer)
        self.star_name_text = self._create_text("", (0, 0), 0.08, parent=self.star_layer)
    
    def show_title(self):
        self.title_layer.show()
        self.file_layer.hide()
        self.hud_layer.hide()
    
    def show_file_select(self):
        self.title_layer.hide()
        self.file_layer.show()
        self.hud_layer.hide()
    
    def show_hud(self):
        self.title_layer.hide()
        self.file_layer.hide()
        self.hud_layer.show()
    
    def show_pause(self, show: bool):
        if show:
            self.pause_layer.show()
        else:
            self.pause_layer.hide()
    
    def show_star_get(self, star_name: str):
        """Show star collection screen"""
        self.star_layer.show()
        if hasattr(self, 'star_name_text'):
            self.star_name_text.node().setText(star_name)
    
    def hide_star_get(self):
        self.star_layer.hide()
    
    def update_hud(self, coins: int, stars: int, health: int, lives: int, course_name: str = ""):
        """Update HUD values"""
        if self.coin_text:
            self.coin_text.node().setText(f"¢ × {coins}")
        if self.star_text:
            self.star_text.node().setText(f"★ × {stars}")
        if self.lives_text:
            self.lives_text.node().setText(f"× {lives}")
        if self.course_text:
            self.course_text.node().setText(course_name)
        
        # Update health display
        for i, seg in enumerate(self.health_segments):
            if i < health:
                seg.node().setTextColor(*COLORS["mario_blue"])
            else:
                seg.node().setTextColor(0.3, 0.3, 0.3, 1)
    
    def show_combo(self, text: str):
        """Show combo text briefly"""
        if self.combo_text:
            self.combo_text.node().setText(text)
            # Fade out after delay
            Sequence(
                Wait(0.8),
                LerpColorScaleInterval(self.combo_text, 0.3, Vec4(1, 1, 1, 0)),
                Func(lambda: self.combo_text.node().setText(""))
            ).start()
            self.combo_text.setColorScale(1, 1, 1, 1)
    
    def move_file_cursor(self, direction: int):
        """Move file select cursor"""
        self.selected_file = (self.selected_file + direction) % 4
        if self.file_cursor:
            y = 0.4 - self.selected_file * 0.25
            self.file_cursor.setZ(y)

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════════════════════════════

class UltraMario3DBros(ShowBase):
    """Main game application"""
    
    def __init__(self):
        super().__init__()
        self.disableMouse()
        
        print("╔═══════════════════════════════════════════════════════════════════════════════════╗")
        print("║              ULTRA MARIO 3D BROS. — COMPLETE 120 STARS EDITION                    ║")
        print("║                         Team Flames / Samsoft / Cat OS                            ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════════╝")
        
        # Configuration
        self.config = GameConfig()
        
        # Game state
        self.state = GameState.TITLE
        self.current_course = 0
        self.collected_stars: List[int] = []
        self.total_coins = 0
        
        # Save data
        self.save_files = [SaveFile(i, f"MARIO {chr(65+i)}") for i in range(4)]
        self.current_save: Optional[SaveFile] = None
        
        # Setup systems
        self._setup_window()
        self._setup_physics()
        self._setup_lighting()
        self._setup_input()
        
        # Create game objects
        self.level_generator = LevelGenerator(self.render.attachNewNode("level"), self.world)
        self.player = Player(self.render.attachNewNode("player"), self.world, self.config)
        self.camera_ctrl = CameraController(self.camera, self.config)
        self.ui = UIManager(self.aspect2d)
        
        # Generate initial level (title screen backdrop)
        self._load_castle()
        
        # Camera setup
        self.camera_ctrl.set_target(self.player.node)
        
        # Start update tasks
        self.taskMgr.add(self._update, "update")
        self.taskMgr.add(self._physics_update, "physics")
        
        # Mouse tracking
        self.last_mouse = Vec2(0, 0)
        self.mouse_locked = False
    
    def _setup_window(self):
        """Configure window properties"""
        props = WindowProperties()
        props.setTitle(f"Ultra Mario 3D Bros. - 120 Stars Edition")
        self.win.requestProperties(props)
    
    def _setup_physics(self):
        """Initialize Bullet physics world"""
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -self.config.gravity))
    
    def _setup_lighting(self):
        """Setup scene lighting"""
        # Ambient
        amb = AmbientLight("ambient")
        amb.setColor(Vec4(0.4, 0.4, 0.5, 1))
        self.render.setLight(self.render.attachNewNode(amb))
        
        # Sun
        sun = DirectionalLight("sun")
        sun.setColor(Vec4(0.9, 0.85, 0.8, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -50, 0)
        self.render.setLight(sun_np)
        
        # Fill light
        fill = DirectionalLight("fill")
        fill.setColor(Vec4(0.3, 0.35, 0.5, 1))
        fill_np = self.render.attachNewNode(fill)
        fill_np.setHpr(120, 30, 0)
        self.render.setLight(fill_np)
    
    def _setup_input(self):
        """Setup input handling"""
        # Movement keys
        self.keys = {k: False for k in ["w", "a", "s", "d", "shift"]}
        
        for key in self.keys:
            self.accept(key, self._set_key, [key, True])
            self.accept(f"{key}-up", self._set_key, [key, False])
        
        # Action keys
        self.accept("space", self._on_space)
        self.accept("escape", self._on_escape)
        self.accept("e", self._on_interact)
        
        # Camera control
        self.accept("arrow_left", self._rotate_camera, [-1])
        self.accept("arrow_right", self._rotate_camera, [1])
        self.accept("arrow_up", self._rotate_camera_pitch, [1])
        self.accept("arrow_down", self._rotate_camera_pitch, [-1])
    
    def _set_key(self, key: str, value: bool):
        """Handle key press/release"""
        self.keys[key] = value
        
        # File select navigation
        if self.state == GameState.FILE_SELECT:
            if value:
                if key == "w":
                    self.ui.move_file_cursor(-1)
                elif key == "s":
                    self.ui.move_file_cursor(1)
    
    def _on_space(self):
        """Handle space key"""
        if self.state == GameState.TITLE:
            self.state = GameState.FILE_SELECT
            self.ui.show_file_select()
        
        elif self.state == GameState.FILE_SELECT:
            self._start_game()
        
        elif self.state == GameState.CASTLE:
            self.player.want_jump = True
        
        elif self.state == GameState.COURSE:
            self.player.want_jump = True
        
        elif self.state == GameState.PAUSED:
            self.state = GameState.COURSE
            self.ui.show_pause(False)
        
        elif self.state == GameState.STAR_GET:
            self._return_to_castle()
    
    def _on_escape(self):
        """Handle escape key"""
        if self.state == GameState.COURSE:
            self.state = GameState.PAUSED
            self.ui.show_pause(True)
        
        elif self.state == GameState.PAUSED:
            self._return_to_castle()
        
        elif self.state == GameState.CASTLE:
            # Could show pause menu or exit
            pass
    
    def _on_interact(self):
        """Handle interact key (enter paintings, etc)"""
        if self.state == GameState.CASTLE:
            # Check for nearby painting
            course = self._check_painting_collision()
            if course:
                self._enter_course(course)
    
    def _rotate_camera(self, direction: int):
        """Rotate camera with arrow keys"""
        self.camera_ctrl.heading += direction * self.config.cam_rotate_speed * 0.016
    
    def _rotate_camera_pitch(self, direction: int):
        """Pitch camera with arrow keys"""
        self.camera_ctrl.pitch = clamp(
            self.camera_ctrl.pitch + direction * 30 * 0.016,
            -60, 30
        )
    
    def _start_game(self):
        """Start game with selected file"""
        self.current_save = self.save_files[self.ui.selected_file]
        self.collected_stars = self.current_save.stars_collected.copy()
        self.state = GameState.CASTLE
        self.ui.show_hud()
        self._load_castle()
        self._lock_mouse()
    
    def _load_castle(self):
        """Load castle hub world"""
        spawn = self.level_generator.generate_castle()
        self.player.set_position(spawn)
        self.current_course = 0
    
    def _enter_course(self, course_id: int):
        """Enter a course"""
        if course_id < 1 or course_id > len(COURSES):
            return
        
        course = COURSES[course_id - 1]
        
        # Check star requirement
        if len(self.collected_stars) < course.required_stars:
            # Could show message
            return
        
        self.state = GameState.COURSE
        self.current_course = course_id
        spawn = self.level_generator.generate_course(course_id)
        self.player.set_position(spawn)
        self.player.coins = 0
    
    def _return_to_castle(self):
        """Return to castle from course"""
        self.state = GameState.CASTLE
        self.ui.hide_star_get()
        self.ui.show_pause(False)
        self._load_castle()
    
    def _collect_star(self, star_id: int, star_name: str):
        """Collect a power star"""
        if star_id not in self.collected_stars:
            self.collected_stars.append(star_id)
            if self.current_save:
                self.current_save.stars_collected.append(star_id)
                self.current_save.total_stars = len(self.collected_stars)
        
        self.state = GameState.STAR_GET
        self.ui.show_star_get(star_name)
    
    def _check_painting_collision(self) -> int:
        """Check if player is near a painting entrance"""
        player_pos = self.player.get_position()
        
        for course in COURSES:
            dist = (player_pos - course.painting_pos).length()
            if dist < 5:
                return course.id
        
        return 0
    
    def _check_star_collision(self):
        """Check if player collected a star"""
        player_pos = self.player.get_position()
        
        for star_np in self.level_generator.stars:
            if star_np.isEmpty():
                continue
            star_pos = star_np.getPos()
            dist = (player_pos - star_pos).length()
            if dist < 2:
                # Get star info
                star_name = star_np.getName()
                star_id = int(star_name.split("_")[1]) if "_" in star_name else 1
                
                # Remove star
                star_np.removeNode()
                
                # Collect
                if self.current_course > 0:
                    course = COURSES[self.current_course - 1]
                    full_star_id = (self.current_course - 1) * 7 + star_id
                    star_display_name = course.star_names[star_id - 1] if star_id <= len(course.star_names) else f"Star {star_id}"
                    self._collect_star(full_star_id, star_display_name)
    
    def _check_coin_collision(self):
        """Check if player collected coins"""
        player_pos = self.player.get_position()
        
        coins_to_remove = []
        for coin_np in self.level_generator.coins:
            if coin_np.isEmpty():
                continue
            coin_pos = coin_np.getPos()
            dist = (player_pos - coin_pos).length()
            if dist < 1.5:
                coins_to_remove.append(coin_np)
                
                # Determine coin value
                if "red" in coin_np.getName():
                    self.player.collect_coin(2)
                elif "blue" in coin_np.getName():
                    self.player.collect_coin(5)
                else:
                    self.player.collect_coin(1)
        
        for coin in coins_to_remove:
            coin.removeNode()
            self.level_generator.coins.remove(coin)
    
    def _lock_mouse(self):
        """Lock mouse for camera control"""
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        self.mouse_locked = True
    
    def _unlock_mouse(self):
        """Unlock mouse"""
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        self.mouse_locked = False
    
    def _physics_update(self, task):
        """Physics update task"""
        dt = clamp(globalClock.getDt(), 0, 0.05)
        
        # Step physics
        self.world.doPhysics(dt)
        
        return Task.cont
    
    def _update(self, task):
        """Main update task"""
        dt = clamp(globalClock.getDt(), 0, 0.05)
        
        # Title/File select - orbit camera
        if self.state in (GameState.TITLE, GameState.FILE_SELECT):
            angle = task.time * 0.15
            radius = 80
            self.camera.setPos(
                math.sin(angle) * radius,
                math.cos(angle) * radius,
                40
            )
            self.camera.lookAt(0, 30, 15)
            return Task.cont
        
        # Paused - no updates
        if self.state == GameState.PAUSED:
            return Task.cont
        
        # Star get - minimal updates
        if self.state == GameState.STAR_GET:
            return Task.cont
        
        # Active gameplay
        if self.state in (GameState.CASTLE, GameState.COURSE):
            # Gather input
            input_dir = Vec3(0, 0, 0)
            if self.keys["w"]: input_dir.y += 1
            if self.keys["s"]: input_dir.y -= 1
            if self.keys["a"]: input_dir.x -= 1
            if self.keys["d"]: input_dir.x += 1
            
            self.player.input_dir = input_dir
            self.player.is_running = self.keys["shift"]
            
            # Mouse delta for camera (when locked)
            mouse_delta = Vec2(0, 0)
            if self.mouse_locked and self.mouseWatcherNode.hasMouse():
                mx = self.mouseWatcherNode.getMouseX()
                my = self.mouseWatcherNode.getMouseY()
                mouse_delta = Vec2(mx * 100, my * 100)
                # Reset mouse to center
                self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)
            
            # Update player
            self.player.update(dt, self.camera_ctrl.get_heading())
            
            # Update camera
            self.camera_ctrl.update(dt, mouse_delta)
            
            # Check collisions
            self._check_coin_collision()
            self._check_star_collision()
            
            # Update combo display
            if self.player.move_state == MoveState.DOUBLE_JUMP:
                self.ui.show_combo("DOUBLE JUMP!")
            elif self.player.move_state == MoveState.TRIPLE_JUMP:
                self.ui.show_combo("YAHOO!")
            
            # Update HUD
            course_name = ""
            if self.current_course > 0 and self.current_course <= len(COURSES):
                course_name = COURSES[self.current_course - 1].name
            
            self.ui.update_hud(
                self.player.coins,
                len(self.collected_stars),
                self.player.health,
                self.player.lives,
                course_name
            )
            
            # Check for death (fell off level)
            if self.player.get_position().z < -50:
                self.player.take_damage(1)
                if self.state == GameState.COURSE:
                    spawn = self.level_generator.generate_course(self.current_course)
                else:
                    spawn = self.level_generator.generate_castle()
                self.player.set_position(spawn)
        
        return Task.cont

# ═══════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    game = UltraMario3DBros()
    game.run()

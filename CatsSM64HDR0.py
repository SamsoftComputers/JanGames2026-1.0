#!/usr/bin/env python3
"""
Super Mario 64 Recreation - pygame-ce
All 15 Courses + Castle Hub + Pseudo-3D Mode7 Rendering
By Team Flames / Samsoft

Controls: WASD/Arrows=Move, Space=Jump, Shift=Run, Z=Crouch/GroundPound
          C=Attack, Q/E=Camera, ESC=Pause, Enter=Select
"""

import pygame
import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum, auto

pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except:
    AUDIO_AVAILABLE = False
    print("Note: Audio not available, running without sound")

# Constants
WIDTH, HEIGHT, FPS = 800, 600, 60
GRAVITY, MAX_FALL = 0.8, 20
WALK_SPEED, RUN_SPEED = 3, 7
JUMP_FORCE, DOUBLE_JUMP, TRIPLE_JUMP = 12, 14, 18

COLORS = {
    'sky': (135, 206, 250), 'grass': (34, 139, 34), 'sand': (238, 214, 175),
    'snow': (255, 250, 250), 'lava': (255, 69, 0), 'water': (64, 164, 223),
    'stone': (128, 128, 128), 'coin': (255, 215, 0), 'star': (255, 255, 100),
    'mario_red': (255, 0, 0), 'mario_blue': (0, 0, 200), 'skin': (255, 200, 150),
}

class State(Enum):
    TITLE = auto(); FILE_SELECT = auto(); CASTLE = auto(); COURSE = auto()
    PAUSE = auto(); STAR_GET = auto(); GAME_OVER = auto()

class MarioState(Enum):
    IDLE = auto(); WALK = auto(); RUN = auto(); JUMP = auto()
    DOUBLE_JUMP = auto(); TRIPLE_JUMP = auto(); FALL = auto()
    CROUCH = auto(); GROUND_POUND = auto(); LONG_JUMP = auto()
    DIVE = auto(); SWIM = auto(); PUNCH = auto(); KICK = auto()
    HURT = auto(); DEATH = auto(); STAR_DANCE = auto()

@dataclass
class Vec3:
    x: float = 0; y: float = 0; z: float = 0
    def __add__(s, o): return Vec3(s.x+o.x, s.y+o.y, s.z+o.z)
    def __sub__(s, o): return Vec3(s.x-o.x, s.y-o.y, s.z-o.z)
    def __mul__(s, n): return Vec3(s.x*n, s.y*n, s.z*n)
    def mag(s): return math.sqrt(s.x**2 + s.y**2 + s.z**2)
    def xz_mag(s): return math.sqrt(s.x**2 + s.z**2)
    def norm(s): m = s.mag(); return Vec3(s.x/m, s.y/m, s.z/m) if m > 0 else Vec3()

@dataclass
class Course:
    id: int; name: str; spawn: Vec3; terrain: str; sky: Tuple[int,int,int]
    music: str; water_level: float = -9999; stars: List[str] = field(default_factory=list)

# All 15 Courses
COURSES = [
    Course(1, "Bob-omb Battlefield", Vec3(0,0,0), "grass", (135,206,250), "adventure",
           stars=["Big Bob-omb on Summit", "Footrace with Koopa", "Shoot to Island",
                  "Find 8 Red Coins", "Mario Wings to Sky", "Behind Chain Chomp's Gate", "100 Coins"]),
    Course(2, "Whomp's Fortress", Vec3(0,0,0), "stone", (135,206,250), "adventure",
           stars=["Chip Off Whomp's Block", "To the Top", "Shoot into Wild Blue",
                  "Red Coins on Isle", "Fall onto Caged Island", "Blast Away Wall", "100 Coins"]),
    Course(3, "Jolly Roger Bay", Vec3(0,50,0), "grass", (135,206,250), "water", -50,
           stars=["Plunder Sunken Ship", "Can the Eel Come Out", "Treasure of Ocean Cave",
                  "Red Coins on Ship", "Blast to Stone Pillar", "Through Jet Stream", "100 Coins"]),
    Course(4, "Cool, Cool Mountain", Vec3(0,400,0), "snow", (200,220,255), "snow",
           stars=["Slip Slidin' Away", "Li'l Penguin Lost", "Big Penguin Race",
                  "Frosty Slide Red Coins", "Snowman's Lost Head", "Wall Kicks Will Work", "100 Coins"]),
    Course(5, "Big Boo's Haunt", Vec3(0,0,200), "stone", (25,25,50), "spooky",
           stars=["Go on a Ghost Hunt", "Ride Big Boo's Merry-Go-Round", "Secret of Haunted Books",
                  "Seek 8 Red Coins", "Big Boo's Balcony", "Eye to Eye in Secret Room", "100 Coins"]),
    Course(6, "Hazy Maze Cave", Vec3(0,0,0), "stone", (60,40,40), "cave",
           stars=["Swimming Beast in Cavern", "Elevate for Red Coins", "Metal-Head Mario",
                  "Navigating Toxic Maze", "A-Maze-ing Emergency Exit", "Watch for Rolling Rocks", "100 Coins"]),
    Course(7, "Lethal Lava Land", Vec3(0,100,0), "lava", (80,20,0), "lava",
           stars=["Boil the Big Bully", "Bully the Bullies", "8-Coin Puzzle",
                  "Red-Hot Log Rolling", "Hot-Foot-It into Volcano", "Elevator Tour in Volcano", "100 Coins"]),
    Course(8, "Shifting Sand Land", Vec3(0,0,300), "sand", (255,200,150), "desert",
           stars=["In Talons of Big Bird", "Shining Atop Pyramid", "Inside Ancient Pyramid",
                  "Stand Tall on Four Pillars", "Free Flying for Red Coins", "Pyramid Puzzle", "100 Coins"]),
    Course(9, "Dire, Dire Docks", Vec3(0,-50,0), "stone", (20,40,80), "water", 100,
           stars=["Board Bowser's Sub", "Chests in Current", "Pole-Jumping for Red Coins",
                  "Through Jet Stream", "Manta Ray's Reward", "Collect the Caps", "100 Coins"]),
    Course(10, "Snowman's Land", Vec3(0,0,200), "snow", (180,200,220), "snow",
           stars=["Snowman's Big Head", "Chill with the Bully", "In the Deep Freeze",
                  "Whirl from Freezing Pond", "Shell Shreddin' for Red Coins", "Into the Igloo", "100 Coins"]),
    Course(11, "Wet-Dry World", Vec3(0,100,0), "stone", (150,180,200), "mechanical", 0,
           stars=["Shocking Arrow Lifts!", "Top o' the Town", "Secrets in Shallows & Sky",
                  "Express Elevator", "Go to Town for Red Coins", "Quick Race Through Downtown!", "100 Coins"]),
    Course(12, "Tall, Tall Mountain", Vec3(0,0,200), "grass", (135,206,250), "adventure",
           stars=["Scale the Mountain", "Mystery of Monkey Cage", "Scary 'Shrooms Red Coins",
                  "Mysterious Mountainside", "Breathtaking View from Bridge", "Blast to Lonely Mushroom", "100 Coins"]),
    Course(13, "Tiny-Huge Island", Vec3(0,0,0), "grass", (135,206,250), "adventure",
           stars=["Pluck the Piranha Flower", "Tip Top of Huge Island", "Rematch with Koopa",
                  "Five Itty Bitty Secrets", "Wiggler's Red Coins", "Make Wiggler Squirm", "100 Coins"]),
    Course(14, "Tick Tock Clock", Vec3(0,0,0), "stone", (50,30,30), "mechanical",
           stars=["Roll into the Cage", "Pit and the Pendulums", "Get a Hand",
                  "Stomp on the Thwomp", "Timed Jumps on Moving Bars", "Stop Time for Red Coins", "100 Coins"]),
    Course(15, "Rainbow Ride", Vec3(0,0,0), "stone", (100,150,255), "sky",
           stars=["Cruiser Crossing Rainbow", "Big House in the Sky", "Coins Amassed in Maze",
                  "Swingin' in the Breeze", "Tricky Triangles!", "Somewhere Over Rainbow", "100 Coins"]),
]

# Sound Generator
class Sounds:
    def __init__(self):
        self.sounds = {}
        if not AUDIO_AVAILABLE:
            return
        self._gen('jump', 440, 0.15); self._gen('double_jump', 550, 0.15)
        self._gen('triple_jump', 660, 0.2); self._gen('land', 100, 0.1)
        self._gen('coin', 988, 0.12); self._gen('star', 523, 0.5)
        self._gen('hurt', 200, 0.3); self._gen('punch', 150, 0.1)
        
    def _gen(self, name, freq, dur, vol=0.25):
        if not AUDIO_AVAILABLE:
            return
        samples = []
        for i in range(int(44100 * dur)):
            t = i / 44100
            v = math.sin(2 * math.pi * freq * t) * vol * math.exp(-t * 10)
            samples.append(int(max(-1, min(1, v)) * 32767))
        buf = b''.join(s.to_bytes(2, 'little', signed=True) * 2 for s in samples)
        self.sounds[name] = pygame.mixer.Sound(buffer=buf)
    
    def play(self, name):
        if AUDIO_AVAILABLE and name in self.sounds: 
            self.sounds[name].play()

# Sprite Generator  
class Sprites:
    def __init__(self):
        self.cache = {}
        
    def mario(self, state):
        key = f'mario_{state}'
        if key in self.cache: return self.cache[key]
        
        s = pygame.Surface((32, 48), pygame.SRCALPHA)
        red, blue, skin = COLORS['mario_red'], COLORS['mario_blue'], COLORS['skin']
        
        # Hat
        pygame.draw.ellipse(s, red, (6, 0, 20, 12))
        pygame.draw.rect(s, red, (4, 6, 24, 6))
        # Face  
        pygame.draw.ellipse(s, skin, (8, 10, 16, 14))
        pygame.draw.circle(s, (0,0,0), (12, 16), 2)
        pygame.draw.circle(s, (0,0,0), (20, 16), 2)
        pygame.draw.ellipse(s, (139,69,19), (8, 19, 16, 6))
        # Body
        pygame.draw.rect(s, red, (8, 24, 16, 12))
        pygame.draw.rect(s, blue, (6, 30, 20, 10))
        # Arms
        pygame.draw.ellipse(s, red, (2, 26, 8, 12))
        pygame.draw.ellipse(s, red, (22, 26, 8, 12))
        pygame.draw.circle(s, skin, (4, 36), 4)
        pygame.draw.circle(s, skin, (28, 36), 4)
        # Legs
        pygame.draw.rect(s, blue, (8, 38, 6, 8))
        pygame.draw.rect(s, blue, (18, 38, 6, 8))
        pygame.draw.ellipse(s, (139,69,19), (6, 44, 8, 4))
        pygame.draw.ellipse(s, (139,69,19), (18, 44, 8, 4))
        
        self.cache[key] = s
        return s
    
    def enemy(self, etype):
        if etype in self.cache: return self.cache[etype]
        s = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        if etype == 'goomba':
            pygame.draw.ellipse(s, (139,69,19), (2, 4, 20, 16))
            pygame.draw.ellipse(s, (210,180,140), (4, 6, 16, 10))
            pygame.draw.circle(s, (0,0,0), (8, 9), 2)
            pygame.draw.circle(s, (0,0,0), (16, 9), 2)
            pygame.draw.ellipse(s, (139,69,19), (0, 18, 10, 6))
            pygame.draw.ellipse(s, (139,69,19), (14, 18, 10, 6))
        elif etype == 'bob_omb':
            pygame.draw.ellipse(s, (20,20,20), (2, 6, 20, 16))
            pygame.draw.ellipse(s, (255,255,255), (5, 10, 6, 6))
            pygame.draw.ellipse(s, (255,255,255), (13, 10, 6, 6))
            pygame.draw.circle(s, (255,100,0), (12, 2), 3)
        elif etype == 'koopa':
            pygame.draw.ellipse(s, (0,200,0), (2, 8, 20, 14))
            pygame.draw.ellipse(s, (0,200,0), (6, 0, 12, 12))
            pygame.draw.ellipse(s, (255,255,100), (0, 18, 10, 6))
            pygame.draw.ellipse(s, (255,255,100), (14, 18, 10, 6))
        elif etype == 'boo':
            pygame.draw.ellipse(s, (255,255,255), (0, 0, 24, 22))
            pygame.draw.ellipse(s, (0,0,0), (4, 6, 6, 8))
            pygame.draw.ellipse(s, (0,0,0), (14, 6, 6, 8))
            pygame.draw.ellipse(s, (0,0,0), (8, 16, 8, 4))
            
        self.cache[etype] = s
        return s
    
    def item(self, itype):
        if itype in self.cache: return self.cache[itype]
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        
        if itype == 'coin':
            pygame.draw.ellipse(s, COLORS['coin'], (2, 0, 12, 16))
            pygame.draw.ellipse(s, (255,235,50), (4, 2, 8, 12))
        elif itype == 'star':
            pts = []
            for i in range(10):
                a = math.pi/2 + i * math.pi/5
                r = 7 if i % 2 == 0 else 3
                pts.append((8 + r*math.cos(a), 8 - r*math.sin(a)))
            pygame.draw.polygon(s, COLORS['star'], pts)
            
        self.cache[itype] = s
        return s

# Camera
class Camera:
    def __init__(self):
        self.pos = Vec3(0, 80, -200)
        self.target = Vec3()
        self.angle = 0
        self.pitch = 0.3
        self.dist = 200
        
    def update(self, target):
        self.target = self.target + (target - self.target) * 0.1
        self.pos.x = self.target.x + math.sin(self.angle) * self.dist
        self.pos.z = self.target.z + math.cos(self.angle) * self.dist
        self.pos.y = self.target.y + self.dist * math.sin(self.pitch)
    
    def project(self, p):
        rel = p - self.pos
        ca, sa = math.cos(-self.angle), math.sin(-self.angle)
        x = rel.x * ca - rel.z * sa
        z = rel.x * sa + rel.z * ca
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y = rel.y * cp - z * sp
        z = rel.y * sp + z * cp
        if z < 0.1: z = 0.1
        scale = 400 / z
        return (int(WIDTH/2 + x*scale), int(HEIGHT/2 - y*scale), z)

# Mario
class Mario:
    def __init__(self):
        self.pos = Vec3()
        self.vel = Vec3()
        self.state = MarioState.IDLE
        self.facing = 0
        self.speed = 0
        self.grounded = True
        self.jump_count = 0
        self.health = 8
        self.lives = 4
        self.coins = 0
        self.stars = 0
        self.inv_timer = 0
        self.anim = 0
        
    def update(self, dt, inp, water_level, sounds):
        self.anim += dt
        if self.inv_timer > 0: self.inv_timer -= dt
        
        in_water = self.pos.y < water_level
        mx, mz = inp.get('mx', 0), inp.get('mz', 0)
        
        if in_water:
            self._swim(dt, mx, mz, inp.get('jump_held'), sounds)
        elif self.grounded:
            self._ground_move(dt, mx, mz, inp, sounds)
        else:
            self._air_move(dt, mx, mz, inp, sounds)
        
        # Gravity
        if not self.grounded and not in_water:
            self.vel.y -= GRAVITY
            self.vel.y = max(self.vel.y, -MAX_FALL)
        
        self.pos = self.pos + self.vel * dt * 60
        
        # Ground collision
        if self.pos.y <= 0:
            self.pos.y = 0
            if not self.grounded:
                sounds.play('land')
            self.grounded = True
            self.vel.y = 0
        else:
            self.grounded = False
        
        self.pos.x = max(-500, min(500, self.pos.x))
        self.pos.z = max(-500, min(500, self.pos.z))
    
    def _ground_move(self, dt, mx, mz, inp, sounds):
        if inp.get('jump'):
            self._jump(sounds)
        elif inp.get('crouch') and self.speed > RUN_SPEED * 0.8:
            self._long_jump(sounds)
        elif inp.get('crouch'):
            self.state = MarioState.CROUCH
            self.speed *= 0.9
        elif inp.get('attack'):
            self.state = MarioState.PUNCH
            sounds.play('punch')
        elif mx != 0 or mz != 0:
            target_ang = math.atan2(mx, mz)
            diff = target_ang - self.facing
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            self.facing += diff * 0.2
            
            target_spd = RUN_SPEED if inp.get('run') else WALK_SPEED
            self.speed += 0.5 if self.speed < target_spd else -0.3
            self.state = MarioState.RUN if inp.get('run') else MarioState.WALK
            
            self.vel.x = math.sin(self.facing) * self.speed
            self.vel.z = math.cos(self.facing) * self.speed
        else:
            self.speed *= 0.85
            if self.speed < 0.1:
                self.speed = 0
                self.state = MarioState.IDLE
            self.vel.x = math.sin(self.facing) * self.speed
            self.vel.z = math.cos(self.facing) * self.speed
    
    def _air_move(self, dt, mx, mz, inp, sounds):
        if mx != 0 or mz != 0:
            target_ang = math.atan2(mx, mz)
            diff = target_ang - self.facing
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            self.facing += diff * 0.05
            self.vel.x += math.sin(target_ang) * 0.15
            self.vel.z += math.cos(target_ang) * 0.15
            spd = self.vel.xz_mag()
            if spd > RUN_SPEED * 1.2:
                self.vel.x *= RUN_SPEED * 1.2 / spd
                self.vel.z *= RUN_SPEED * 1.2 / spd
        
        if inp.get('crouch') and self.state not in [MarioState.GROUND_POUND, MarioState.LONG_JUMP]:
            self.vel.x = self.vel.z = 0
            self.vel.y = -25
            self.state = MarioState.GROUND_POUND
            sounds.play('land')
        
        self.state = MarioState.JUMP if self.vel.y > 0 else MarioState.FALL
    
    def _swim(self, dt, mx, mz, swim, sounds):
        if swim:
            self.vel.y = 4
            sounds.play('jump')
        if mx != 0 or mz != 0:
            self.facing = math.atan2(mx, mz)
            self.vel.x = math.sin(self.facing) * 4
            self.vel.z = math.cos(self.facing) * 4
        else:
            self.vel.x *= 0.95
            self.vel.z *= 0.95
        self.vel.y -= 0.1
        self.vel.y = max(self.vel.y, -4)
        self.state = MarioState.SWIM
    
    def _jump(self, sounds):
        if self.jump_count == 0:
            self.vel.y = JUMP_FORCE
            self.jump_count = 1
            sounds.play('jump')
        elif self.jump_count == 1:
            self.vel.y = DOUBLE_JUMP
            self.jump_count = 2
            sounds.play('double_jump')
        else:
            self.vel.y = TRIPLE_JUMP if self.speed > WALK_SPEED else JUMP_FORCE
            self.jump_count = 0
            sounds.play('triple_jump')
        self.grounded = False
        self.state = MarioState.JUMP
    
    def _long_jump(self, sounds):
        self.vel.y = 8
        self.vel.x = math.sin(self.facing) * 12
        self.vel.z = math.cos(self.facing) * 12
        self.grounded = False
        self.state = MarioState.LONG_JUMP
        sounds.play('jump')
    
    def damage(self, amt, sounds):
        if self.inv_timer > 0: return
        self.health -= amt
        self.inv_timer = 2
        self.state = MarioState.HURT
        self.vel.y = 5
        sounds.play('hurt')
        if self.health <= 0:
            self.lives -= 1
            self.state = MarioState.DEATH
    
    def collect_coin(self, sounds):
        self.coins += 1
        if self.coins >= 100:
            self.coins -= 100
            self.lives += 1
        sounds.play('coin')
        if self.health < 8: self.health += 1
    
    def collect_star(self, sounds):
        self.stars += 1
        self.state = MarioState.STAR_DANCE
        sounds.play('star')

# Entities
class Entity:
    def __init__(self, etype, pos):
        self.type = etype
        self.pos = Vec3(pos.x, pos.y, pos.z)
        self.vel = Vec3()
        self.active = True
        self.facing = random.uniform(0, 6.28)
        self.timer = 0
        
    def update(self, dt, mario, sounds):
        self.timer += dt
        
        if self.type == 'goomba':
            self.pos.x += math.sin(self.facing) * dt * 60
            self.pos.z += math.cos(self.facing) * dt * 60
            if self.timer > 3:
                self.timer = 0
                self.facing += math.pi
        elif self.type == 'koopa':
            self.pos.x += math.sin(self.facing) * 1.2 * dt * 60
            if self.timer > 2:
                self.timer = 0
                self.facing += math.pi
        elif self.type == 'boo':
            to_mario = mario.pos - self.pos
            ang = math.atan2(to_mario.x, to_mario.z)
            diff = abs(mario.facing - ang)
            if diff > math.pi/3:  # Not looking
                d = to_mario.norm()
                self.pos = self.pos + d * 2 * dt * 60
        elif self.type in ['coin', 'star']:
            self.pos.y += math.sin(self.timer * 3) * 0.05
        
        # Collision with Mario
        dist = (self.pos - mario.pos).mag()
        if dist < 25:
            if self.type == 'coin':
                mario.collect_coin(sounds)
                self.active = False
            elif self.type == 'star':
                mario.collect_star(sounds)
                self.active = False
            elif self.type in ['goomba', 'koopa', 'boo']:
                if mario.vel.y < -2 and mario.pos.y > self.pos.y + 10:
                    mario.vel.y = 8
                    sounds.play('punch')
                    self.active = False
                elif mario.state == MarioState.PUNCH:
                    self.active = False
                    sounds.play('punch')
                else:
                    mario.damage(1, sounds)

# Level Generator
def generate_level(course):
    entities = []
    # Enemies based on terrain
    for i in range(8):
        x, z = random.randint(-300, 300), random.randint(-300, 300)
        if course.terrain in ['grass', 'sand']:
            entities.append(Entity('goomba', Vec3(x, 0, z)))
        elif course.terrain == 'stone':
            entities.append(Entity(random.choice(['goomba', 'boo']), Vec3(x, random.randint(0, 100), z)))
        elif course.terrain == 'snow':
            entities.append(Entity('goomba', Vec3(x, 0, z)))
    
    # Koopas
    for i in range(3):
        entities.append(Entity('koopa', Vec3(random.randint(-200, 200), 0, random.randint(-200, 200))))
    
    # Coins
    for i in range(40):
        entities.append(Entity('coin', Vec3(random.randint(-300, 300), random.randint(10, 80), random.randint(-300, 300))))
    
    # Stars (one for demo)
    entities.append(Entity('star', Vec3(random.randint(-100, 100), 50, random.randint(-200, -100))))
    
    return entities

# Renderer
class Renderer:
    def __init__(self, screen, sprites):
        self.screen = screen
        self.sprites = sprites
        self.font = pygame.font.Font(None, 36)
        self.small = pygame.font.Font(None, 24)
        self.big = pygame.font.Font(None, 72)
    
    def game(self, mario, cam, entities, course, state):
        sky = course.sky if course else COLORS['sky']
        self.screen.fill(sky)
        
        # Ground
        self._ground(cam, course)
        
        # Water
        if course and course.water_level > -9000:
            wy = HEIGHT//2 + int(course.water_level * 2)
            if wy < HEIGHT:
                ws = pygame.Surface((WIDTH, HEIGHT - wy), pygame.SRCALPHA)
                ws.fill((64, 164, 223, 128))
                self.screen.blit(ws, (0, wy))
        
        # Collect renderables
        items = []
        for e in entities:
            if e.active:
                sp = cam.project(e.pos)
                items.append(('entity', e, sp))
        sp = cam.project(mario.pos)
        items.append(('mario', mario, sp))
        
        # Sort by depth
        items.sort(key=lambda x: x[2][2], reverse=True)
        
        # Render
        for typ, obj, (x, y, z) in items:
            if z < 1: continue
            scale = max(0.3, min(2.5, 80/z))
            
            if typ == 'mario':
                spr = self.sprites.mario(obj.state.name.lower())
                w, h = int(spr.get_width() * scale), int(spr.get_height() * scale)
                if w > 4 and h > 4:
                    s = pygame.transform.scale(spr, (w, h))
                    if math.sin(obj.facing - cam.angle) < 0:
                        s = pygame.transform.flip(s, True, False)
                    if obj.inv_timer > 0 and int(obj.inv_timer * 10) % 2:
                        s.set_alpha(128)
                    self.screen.blit(s, (x - w//2, y - h))
            else:
                if obj.type in ['coin', 'star']:
                    spr = self.sprites.item(obj.type)
                else:
                    spr = self.sprites.enemy(obj.type)
                w, h = int(spr.get_width() * scale), int(spr.get_height() * scale)
                if w > 2 and h > 2:
                    s = pygame.transform.scale(spr, (w, h))
                    self.screen.blit(s, (x - w//2, y - h))
        
        # HUD
        self._hud(mario, course)
        
        # Overlays
        if state == State.PAUSE:
            self._pause()
        elif state == State.STAR_GET:
            self._star_get()
    
    def _ground(self, cam, course):
        if not course: return
        colors = {
            'grass': ((34,139,34), (45,160,45)),
            'sand': ((238,214,175), (220,200,160)),
            'snow': ((255,250,250), (240,240,255)),
            'stone': ((128,128,128), (100,100,100)),
            'lava': ((255,69,0), (255,100,50)),
        }
        c1, c2 = colors.get(course.terrain, colors['grass'])
        
        hz = HEIGHT // 3
        for sy in range(hz, HEIGHT, 2):
            depth = (sy - hz) / (HEIGHT - hz)
            if depth < 0.01: continue
            wz = 50 / depth
            
            for sx in range(0, WIDTH, 8):
                wx = (sx - WIDTH//2) * wz / 200
                ca, sa = math.cos(cam.angle), math.sin(cam.angle)
                rx = wx * ca + wz * sa + cam.target.x
                rz = -wx * sa + wz * ca + cam.target.z
                
                col = c1 if (int(rx/20) + int(rz/20)) % 2 == 0 else c2
                pygame.draw.rect(self.screen, col, (sx, sy, 8, 2))
    
    def _hud(self, mario, course):
        # Health
        pygame.draw.circle(self.screen, (50,50,50), (50, 50), 30)
        if mario.health > 0:
            pts = [(50, 50)]
            for a in range(90, 90 - int(mario.health/8*360) - 1, -10):
                pts.append((50 + 26*math.cos(math.radians(a)), 50 - 26*math.sin(math.radians(a))))
            if len(pts) > 2:
                col = (100,200,100) if mario.health > 4 else (255,200,50) if mario.health > 2 else (255,50,50)
                pygame.draw.polygon(self.screen, col, pts)
        t = self.small.render(str(mario.health), True, (255,255,255))
        self.screen.blit(t, (44, 42))
        
        # Coins
        self.screen.blit(self.sprites.item('coin'), (100, 38))
        t = self.font.render(f"x {mario.coins}", True, (255,255,255))
        self.screen.blit(t, (120, 38))
        
        # Stars
        self.screen.blit(self.sprites.item('star'), (200, 38))
        t = self.font.render(f"x {mario.stars}", True, (255,255,255))
        self.screen.blit(t, (220, 38))
        
        # Lives
        t = self.font.render(f"x {mario.lives}", True, (255,255,255))
        self.screen.blit(t, (WIDTH - 70, 38))
        
        # Course name
        if course:
            t = self.small.render(course.name, True, (255,255,255))
            r = t.get_rect(center=(WIDTH//2, 20))
            self.screen.blit(t, r)
    
    def _pause(self):
        o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 150))
        self.screen.blit(o, (0, 0))
        t = self.big.render("PAUSED", True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
        t = self.font.render("ESC to continue, Q to quit", True, (200,200,200))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
    
    def _star_get(self):
        for i in range(10, 0, -1):
            r = i * 40
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 100, 25 - i*2), (r, r), r)
            self.screen.blit(s, (WIDTH//2 - r, HEIGHT//2 - r))
        star = pygame.transform.scale(pygame.Surface((32,32), pygame.SRCALPHA), (128, 128))
        pts = []
        for i in range(10):
            a = math.pi/2 + i * math.pi/5
            rad = 60 if i % 2 == 0 else 25
            pts.append((64 + rad*math.cos(a), 64 - rad*math.sin(a)))
        pygame.draw.polygon(star, COLORS['star'], pts)
        self.screen.blit(star, star.get_rect(center=(WIDTH//2, HEIGHT//2)))
        t = self.big.render("STAR GET!", True, (255, 255, 100))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))
    
    def title(self, time):
        self.screen.fill((0, 50, 100))
        for i in range(20):
            x = (i * 50 + int(time * 30)) % (WIDTH + 100) - 50
            y = 100 + math.sin(time + i) * 30
            pygame.draw.circle(self.screen, (0, 80, 150), (int(x), int(y)), 20)
        
        y = 150 + math.sin(time * 2) * 10
        t = self.big.render("SUPER MARIO 64", True, (255, 215, 0))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, int(y))))
        t = self.font.render("pygame-ce Recreation", True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, int(y) + 60)))
        
        if int(time * 2) % 2:
            t = self.font.render("Press SPACE to start", True, (255,255,255))
            self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT - 100)))
        
        t = self.small.render("By Team Flames / Samsoft", True, (150,150,150))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT - 30)))
    
    def file_select(self, sel):
        self.screen.fill((40, 60, 100))
        t = self.big.render("SELECT FILE", True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, 80)))
        
        for i in range(4):
            x, y = WIDTH//2, 180 + i * 90
            col = (100, 150, 200) if i == sel else (60, 80, 100)
            pygame.draw.rect(self.screen, col, (x-150, y-25, 300, 50), border_radius=10)
            pygame.draw.rect(self.screen, (200,200,200) if i == sel else (100,100,100),
                           (x-150, y-25, 300, 50), 3, border_radius=10)
            t = self.font.render(f"File {chr(65+i)}", True, (255,255,255))
            self.screen.blit(t, (x - 120, y - 15))
        
        t = self.small.render("UP/DOWN Select  ENTER Confirm  ESC Back", True, (150,150,150))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT - 40)))
    
    def course_select(self, courses, sel):
        self.screen.fill((30, 50, 80))
        t = self.big.render("SELECT COURSE", True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, 60)))
        
        # Show 5 courses at a time
        start = max(0, sel - 2)
        end = min(len(courses), start + 5)
        
        for i, c in enumerate(courses[start:end]):
            idx = start + i
            x, y = WIDTH//2, 140 + i * 80
            col = (100, 150, 200) if idx == sel else (50, 70, 90)
            pygame.draw.rect(self.screen, col, (x-200, y-30, 400, 60), border_radius=8)
            t = self.font.render(f"{c.id}. {c.name}", True, (255,255,255))
            self.screen.blit(t, (x - 180, y - 10))
        
        # Show stars for selected course
        c = courses[sel]
        y = 520
        t = self.small.render("Stars:", True, (255,215,0))
        self.screen.blit(t, (50, y))
        for i, star in enumerate(c.stars[:3]):
            t = self.small.render(f"★ {star}", True, (200,200,200))
            self.screen.blit(t, (120 + i * 220, y))
        
        t = self.small.render("UP/DOWN Select  ENTER Play  ESC Back", True, (150,150,150))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT - 20)))
    
    def game_over(self, mario):
        self.screen.fill((20, 0, 0))
        t = self.big.render("GAME OVER", True, (200, 0, 0))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
        t = self.font.render(f"Stars: {mario.stars}  Coins: {mario.coins}", True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        t = self.small.render("Press SPACE to continue", True, (150,150,150))
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT - 80)))

# Main Game
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Super Mario 64 - pygame-ce")
        self.clock = pygame.time.Clock()
        
        self.sounds = Sounds()
        self.sprites = Sprites()
        self.renderer = Renderer(self.screen, self.sprites)
        
        self.mario = Mario()
        self.camera = Camera()
        self.course = None
        self.entities = []
        
        self.state = State.TITLE
        self.running = True
        self.time = 0
        self.sel_file = 0
        self.sel_course = 0
        self.star_timer = 0
        
        self.inp = {}
        self.keys = set()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.time += dt
            
            self._events()
            self._update(dt)
            self._render()
            pygame.display.flip()
        
        pygame.quit()
    
    def _events(self):
        self.inp['jump'] = False
        self.inp['attack'] = False
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                self.keys.add(ev.key)
                self._key_down(ev.key)
            elif ev.type == pygame.KEYUP:
                self.keys.discard(ev.key)
        
        # Continuous input
        self.inp['mx'] = (pygame.K_d in self.keys or pygame.K_RIGHT in self.keys) - \
                         (pygame.K_a in self.keys or pygame.K_LEFT in self.keys)
        self.inp['mz'] = (pygame.K_s in self.keys or pygame.K_DOWN in self.keys) - \
                         (pygame.K_w in self.keys or pygame.K_UP in self.keys)
        self.inp['jump_held'] = pygame.K_SPACE in self.keys
        self.inp['run'] = pygame.K_LSHIFT in self.keys
        self.inp['crouch'] = pygame.K_z in self.keys
        
        if self.inp['mx'] and self.inp['mz']:
            self.inp['mx'] *= 0.707
            self.inp['mz'] *= 0.707
    
    def _key_down(self, key):
        if self.state == State.TITLE:
            if key == pygame.K_SPACE:
                self.state = State.FILE_SELECT
                self.sounds.play('coin')
        
        elif self.state == State.FILE_SELECT:
            if key == pygame.K_UP:
                self.sel_file = (self.sel_file - 1) % 4
            elif key == pygame.K_DOWN:
                self.sel_file = (self.sel_file + 1) % 4
            elif key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.state = State.CASTLE
                self.mario = Mario()
                self.sel_course = 0
                self.sounds.play('star')
            elif key == pygame.K_ESCAPE:
                self.state = State.TITLE
        
        elif self.state == State.CASTLE:
            if key == pygame.K_UP:
                self.sel_course = (self.sel_course - 1) % len(COURSES)
            elif key == pygame.K_DOWN:
                self.sel_course = (self.sel_course + 1) % len(COURSES)
            elif key in [pygame.K_RETURN, pygame.K_SPACE]:
                self._enter_course(self.sel_course)
            elif key == pygame.K_ESCAPE:
                self.state = State.FILE_SELECT
        
        elif self.state == State.COURSE:
            if key == pygame.K_ESCAPE:
                self.state = State.PAUSE
            elif key == pygame.K_SPACE:
                self.inp['jump'] = True
            elif key == pygame.K_c:
                self.inp['attack'] = True
        
        elif self.state == State.PAUSE:
            if key == pygame.K_ESCAPE:
                self.state = State.COURSE
            elif key == pygame.K_q:
                self.state = State.CASTLE
                self.course = None
        
        elif self.state == State.STAR_GET:
            if key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.state = State.CASTLE
                self.course = None
        
        elif self.state == State.GAME_OVER:
            if key == pygame.K_SPACE:
                self.state = State.TITLE
    
    def _enter_course(self, idx):
        self.course = COURSES[idx]
        self.entities = generate_level(self.course)
        self.mario.pos = Vec3(self.course.spawn.x, self.course.spawn.y, self.course.spawn.z)
        self.mario.vel = Vec3()
        self.state = State.COURSE
        self.sounds.play('star')
    
    def _update(self, dt):
        if self.state == State.COURSE:
            wl = self.course.water_level if self.course else -9999
            self.mario.update(dt, self.inp, wl, self.sounds)
            
            for e in self.entities[:]:
                e.update(dt, self.mario, self.sounds)
                if not e.active:
                    self.entities.remove(e)
            
            # Camera rotation
            if pygame.K_q in self.keys:
                self.camera.angle += 0.03
            if pygame.K_e in self.keys:
                self.camera.angle -= 0.03
            
            self.camera.update(self.mario.pos)
            
            # Star dance
            if self.mario.state == MarioState.STAR_DANCE:
                self.star_timer += dt
                if self.star_timer > 2:
                    self.state = State.STAR_GET
                    self.star_timer = 0
            
            # Death
            if self.mario.pos.y < -200 or self.mario.state == MarioState.DEATH:
                if self.mario.lives <= 0:
                    self.state = State.GAME_OVER
                else:
                    self.mario.pos = Vec3(self.course.spawn.x, self.course.spawn.y, self.course.spawn.z)
                    self.mario.vel = Vec3()
                    self.mario.health = 8
                    self.mario.state = MarioState.IDLE
    
    def _render(self):
        if self.state == State.TITLE:
            self.renderer.title(self.time)
        elif self.state == State.FILE_SELECT:
            self.renderer.file_select(self.sel_file)
        elif self.state == State.CASTLE:
            self.renderer.course_select(COURSES, self.sel_course)
        elif self.state in [State.COURSE, State.PAUSE, State.STAR_GET]:
            self.renderer.game(self.mario, self.camera, self.entities, self.course, self.state)
        elif self.state == State.GAME_OVER:
            self.renderer.game_over(self.mario)

def main():
    print("=" * 50)
    print("SUPER MARIO 64 - pygame-ce Recreation")
    print("By Team Flames / Samsoft")
    print("=" * 50)
    print("\nControls:")
    print("  WASD/Arrows = Move")
    print("  SPACE = Jump (hold in water to swim)")
    print("  SHIFT = Run")
    print("  Z = Crouch / Ground Pound")
    print("  C = Attack")
    print("  Q/E = Rotate Camera")
    print("  ESC = Pause")
    print("\nStarting game...")
    
    Game().run()

if __name__ == "__main__":
    main()

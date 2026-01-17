import pygame
import json
import sys
import os
import math
from enum import Enum
from collections import defaultdict

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
TOOLBAR_HEIGHT = 200
GRID_SIZE = 32  # SMBX standard grid size
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
DARK_GRAY = (40, 40, 40)
BACKGROUND_GRAY = (60, 60, 70)

# SMBX2 Layer System
class Layer(Enum):
    BACKGROUND = 0
    DESTRUCTIBLE = 1
    MAIN = 2
    FOREGROUND = 3
    FGBACKGROUND = 4

# Editor Modes
class EditorMode(Enum):
    TILE = 0
    BLOCK = 1
    NPC = 2
    BACKGROUND = 3
    PATH = 4
    SECTION = 5
    LEVEL_SETTINGS = 6

# Create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SMBX2 Level Editor")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.Font(None, 20)
font_medium = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 32)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_x = 0
        self.target_y = 0
        self.speed = 10
        self.drag_start = None
        
    def update(self, keys, mouse_pos, mouse_buttons, drag_rect=None):
        # Keyboard movement
        move_speed = self.speed / self.zoom
        if keys[pygame.K_a]:
            self.x -= move_speed
        if keys[pygame.K_d]:
            self.x += move_speed
        if keys[pygame.K_w]:
            self.y -= move_speed
        if keys[pygame.K_s]:
            self.y += move_speed
        
        # Mouse drag
        if mouse_buttons[2]:  # Right click
            if self.drag_start is None:
                self.drag_start = mouse_pos
            else:
                dx, dy = mouse_pos[0] - self.drag_start[0], mouse_pos[1] - self.drag_start[1]
                self.x -= dx / self.zoom
                self.y -= dy / self.zoom
                self.drag_start = mouse_pos
        else:
            self.drag_start = None
            
        # Zoom with mouse wheel
        for event in pygame.event.get(pygame.MOUSEWHEEL):
            if event.y > 0:
                self.zoom = min(self.zoom * 1.1, 4.0)
            elif event.y < 0:
                self.zoom = max(self.zoom / 1.1, 0.25)
                
        # Center camera on selection
        if drag_rect:
            self.x = drag_rect.centerx - SCREEN_WIDTH // 2
            self.y = drag_rect.centery - SCREEN_HEIGHT // 2
            
    def screen_to_world(self, screen_pos):
        x, y = screen_pos
        return (
            int((x) / self.zoom + self.x),
            int((y) / self.zoom + self.y)
        )
        
    def world_to_screen(self, world_pos):
        x, y = world_pos
        return (
            int((x - self.x) * self.zoom),
            int((y - self.y) * self.zoom)
        )

class Tile:
    def __init__(self, x, y, tile_id, layer=Layer.MAIN, foreground=False):
        self.x = x
        self.y = y
        self.tile_id = tile_id
        self.layer = layer
        self.foreground = foreground
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.color = self.get_color_by_id(tile_id)
        
    def get_color_by_id(self, tile_id):
        # Color coding by tile type
        if tile_id < 100:
            return (100, 100, 200)  # Basic blocks
        elif tile_id < 200:
            return (200, 150, 100)  # Platforms
        elif tile_id < 300:
            return (100, 200, 100)  # Background
        elif tile_id < 400:
            return (200, 100, 100)  # Dangerous
        elif tile_id < 500:
            return (200, 200, 100)  # Interactive
        else:
            return (150, 150, 150)  # Special
            
    def draw(self, surface, camera, selected=False):
        screen_x, screen_y = camera.world_to_screen((self.x, self.y))
        screen_width = int(self.width * camera.zoom)
        screen_height = int(self.height * camera.zoom)
        
        if screen_x + screen_width < 0 or screen_x > SCREEN_WIDTH or screen_y + screen_height < 0 or screen_y > SCREEN_HEIGHT:
            return
            
        # Draw tile
        rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        pygame.draw.rect(surface, self.color, rect)
        
        # Draw border
        border_color = YELLOW if selected else (self.color[0]//2, self.color[1]//2, self.color[2]//2)
        pygame.draw.rect(surface, border_color, rect, 1)
        
        # Draw tile ID if zoomed in enough
        if camera.zoom > 0.8:
            id_text = font_small.render(str(self.tile_id), True, WHITE)
            surface.blit(id_text, (screen_x + 2, screen_y + 2))
            
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "id": self.tile_id,
            "layer": self.layer.value,
            "foreground": self.foreground
        }

class Block:
    def __init__(self, x, y, block_id, layer=Layer.MAIN):
        self.x = x
        self.y = y
        self.block_id = block_id
        self.layer = layer
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.contains = []  # Contents (coins, powerups)
        self.slippery = False
        self.invisible = False
        self.color = self.get_color_by_id(block_id)
        
    def get_color_by_id(self, block_id):
        # SMBX block color coding
        if block_id == 1:  # Question block
            return (255, 200, 0)
        elif block_id == 2:  # Brick
            return (180, 100, 50)
        elif block_id == 3:  # Empty block
            return (100, 100, 100)
        elif block_id == 4:  # Invisible
            return (100, 100, 100, 128)
        elif block_id == 5:  # Note block
            return (255, 100, 100)
        else:
            return (150, 150, 150)
            
    def draw(self, surface, camera, selected=False):
        screen_x, screen_y = camera.world_to_screen((self.x, self.y))
        screen_width = int(self.width * camera.zoom)
        screen_height = int(self.height * camera.zoom)
        
        if screen_x + screen_width < 0 or screen_x > SCREEN_WIDTH or screen_y + screen_height < 0 or screen_y > SCREEN_HEIGHT:
            return
            
        rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        
        # Draw block with pattern based on type
        if self.block_id == 1:  # Question block
            # Animated question mark
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.2
            size_mod = 1 + pulse
            inner_rect = pygame.Rect(
                screen_x + screen_width * (1 - size_mod) / 2,
                screen_y + screen_height * (1 - size_mod) / 2,
                screen_width * size_mod,
                screen_height * size_mod
            )
            pygame.draw.rect(surface, self.color, inner_rect, border_radius=int(4 * camera.zoom))
            pygame.draw.rect(surface, (255, 255, 200), inner_rect, int(2 * camera.zoom), border_radius=int(4 * camera.zoom))
            
            # Question mark
            if camera.zoom > 0.5:
                q_text = font_medium.render("?", True, (100, 50, 0))
                q_rect = q_text.get_rect(center=inner_rect.center)
                surface.blit(q_text, q_rect)
                
        elif self.block_id == 2:  # Brick
            # Brick pattern
            pygame.draw.rect(surface, self.color, rect)
            for i in range(0, int(screen_width), int(8 * camera.zoom)):
                for j in range(0, int(screen_height), int(8 * camera.zoom)):
                    if (i // (8 * camera.zoom) + j // (8 * camera.zoom)) % 2 == 0:
                        brick_rect = pygame.Rect(screen_x + i, screen_y + j, 
                                                int(8 * camera.zoom), int(8 * camera.zoom))
                        pygame.draw.rect(surface, (self.color[0] - 40, self.color[1] - 40, self.color[2] - 40), 
                                       brick_rect, 1)
                        
        elif self.block_id == 4:  # Invisible
            # Draw as semi-transparent
            if self.invisible:
                s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                s.fill((100, 100, 100, 100))
                surface.blit(s, (screen_x, screen_y))
            else:
                pygame.draw.rect(surface, self.color, rect, 1, border_radius=2)
                
        else:
            pygame.draw.rect(surface, self.color, rect)
            
        # Draw border
        if selected:
            pygame.draw.rect(surface, YELLOW, rect, int(2 * camera.zoom))
            
        # Draw contents indicator
        if self.contains:
            content_color = (0, 255, 0) if "mushroom" in str(self.contains).lower() else (255, 255, 0)
            pygame.draw.circle(surface, content_color, 
                             (screen_x + screen_width // 2, screen_y + screen_height // 2),
                             int(4 * camera.zoom))
            
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "id": self.block_id,
            "layer": self.layer.value,
            "contents": self.contains,
            "slippery": self.slippery,
            "invisible": self.invisible
        }

class NPC:
    def __init__(self, x, y, npc_id, direction=1):
        self.x = x
        self.y = y
        self.npc_id = npc_id
        self.direction = direction  # -1: left, 1: right
        self.width = GRID_SIZE
        self.height = GRID_SIZE * 2  # Most NPCs are 2 blocks tall
        self.generator = False
        self.color = self.get_color_by_id(npc_id)
        
    def get_color_by_id(self, npc_id):
        # NPC color coding
        if npc_id == 1:  # Goomba
            return (150, 100, 50)
        elif npc_id == 2:  # Koopa
            return (50, 150, 50)
        elif npc_id == 3:  # Piranha
            return (150, 50, 50)
        elif npc_id == 4:  # Cheep Cheep
            return (50, 100, 150)
        elif npc_id == 5:  # Boo
            return (200, 200, 200)
        else:
            return (200, 100, 200)
            
    def draw(self, surface, camera, selected=False):
        screen_x, screen_y = camera.world_to_screen((self.x, self.y))
        screen_width = int(self.width * camera.zoom)
        screen_height = int(self.height * camera.zoom)
        
        if screen_x + screen_width < 0 or screen_x > SCREEN_WIDTH or screen_y + screen_height < 0 or screen_y > SCREEN_HEIGHT:
            return
            
        rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        
        # Draw NPC body
        if self.npc_id == 1:  # Goomba
            pygame.draw.ellipse(surface, self.color, rect)
            # Eyes
            eye_y = screen_y + screen_height // 3
            pygame.draw.circle(surface, WHITE, 
                             (screen_x + screen_width // 3, eye_y), 
                             int(4 * camera.zoom))
            pygame.draw.circle(surface, WHITE, 
                             (screen_x + 2 * screen_width // 3, eye_y), 
                             int(4 * camera.zoom))
            # Pupils
            pupil_offset = 2 if self.direction > 0 else -2
            pygame.draw.circle(surface, BLACK, 
                             (screen_x + screen_width // 3 + pupil_offset, eye_y), 
                             int(2 * camera.zoom))
            pygame.draw.circle(surface, BLACK, 
                             (screen_x + 2 * screen_width // 3 + pupil_offset, eye_y), 
                             int(2 * camera.zoom))
                             
        elif self.npc_id == 2:  # Koopa
            # Shell
            shell_rect = pygame.Rect(screen_x, screen_y + screen_height // 2, 
                                   screen_width, screen_height // 2)
            pygame.draw.ellipse(surface, self.color, shell_rect)
            # Body
            body_rect = pygame.Rect(screen_x + screen_width // 4, screen_y,
                                  screen_width // 2, screen_height // 2)
            pygame.draw.ellipse(surface, (self.color[0] - 30, self.color[1] - 30, self.color[2] - 30), 
                              body_rect)
            
        else:
            # Generic NPC
            pygame.draw.rect(surface, self.color, rect)
            
        # Draw direction indicator
        dir_x = screen_x + screen_width // 2 + (self.direction * screen_width // 3)
        pygame.draw.line(surface, RED,
                        (screen_x + screen_width // 2, screen_y + screen_height // 2),
                        (dir_x, screen_y + screen_height // 2),
                        int(2 * camera.zoom))
                        
        # Draw selection border
        if selected:
            pygame.draw.rect(surface, YELLOW, rect, int(2 * camera.zoom))
            
        # Draw NPC ID
        if camera.zoom > 0.8:
            id_text = font_small.render(str(self.npc_id), True, WHITE)
            surface.blit(id_text, (screen_x + 2, screen_y + 2))
            
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "id": self.npc_id,
            "direction": self.direction,
            "generator": self.generator
        }

class Background:
    def __init__(self, x, y, bg_id, layer=Layer.BACKGROUND):
        self.x = x
        self.y = y
        self.bg_id = bg_id
        self.layer = layer
        self.width = GRID_SIZE * 2
        self.height = GRID_SIZE * 2
        self.repeated = True
        self.color = self.get_color_by_id(bg_id)
        
    def get_color_by_id(self, bg_id):
        # Background object color coding
        if bg_id < 10:
            return (100, 200, 100)  # Plants
        elif bg_id < 20:
            return (150, 150, 100)  # Clouds
        elif bg_id < 30:
            return (100, 150, 200)  # Hills
        else:
            return (200, 150, 100)  # Structures
            
    def draw(self, surface, camera, selected=False):
        screen_x, screen_y = camera.world_to_screen((self.x, self.y))
        screen_width = int(self.width * camera.zoom)
        screen_height = int(self.height * camera.zoom)
        
        rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        
        # Draw background object
        if self.bg_id < 10:  # Plant
            pygame.draw.polygon(surface, self.color, [
                (screen_x + screen_width // 2, screen_y),
                (screen_x, screen_y + screen_height),
                (screen_x + screen_width, screen_y + screen_height)
            ])
        elif self.bg_id < 20:  # Cloud
            pygame.draw.ellipse(surface, self.color, rect)
            # Additional cloud parts
            small_rect1 = pygame.Rect(screen_x - screen_width // 3, screen_y + screen_height // 3,
                                     screen_width // 2, screen_height // 2)
            small_rect2 = pygame.Rect(screen_x + 2 * screen_width // 3, screen_y + screen_height // 4,
                                     screen_width // 2, screen_height // 2)
            pygame.draw.ellipse(surface, self.color, small_rect1)
            pygame.draw.ellipse(surface, self.color, small_rect2)
        else:
            pygame.draw.rect(surface, self.color, rect)
            
        # Draw border
        border_color = YELLOW if selected else (self.color[0]//2, self.color[1]//2, self.color[2]//2)
        pygame.draw.rect(surface, border_color, rect, int(2 * camera.zoom))
        
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "id": self.bg_id,
            "layer": self.layer.value,
            "repeated": self.repeated
        }

class Section:
    def __init__(self, x, y, width, height, section_id=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = section_id
        self.music_id = 0
        self.background_id = 0
        self.is_underwater = False
        self.is_warp_zone = False
        self.warp_dest = None
        self.color = self.get_color_by_id(section_id)
        
    def get_color_by_id(self, section_id):
        colors = [
            (255, 200, 200, 50),  # Section 0
            (200, 255, 200, 50),  # Section 1
            (200, 200, 255, 50),  # Section 2
            (255, 255, 200, 50),  # Section 3
            (255, 200, 255, 50),  # Section 4
            (200, 255, 255, 50),  # Section 5
        ]
        return colors[section_id % len(colors)]
        
    def draw(self, surface, camera, selected=False):
        screen_x, screen_y = camera.world_to_screen((self.x, self.y))
        screen_width = int(self.width * camera.zoom)
        screen_height = int(self.height * camera.zoom)
        
        # Draw section area
        s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        s.fill(self.color)
        surface.blit(s, (screen_x, screen_y))
        
        # Draw border
        border_color = YELLOW if selected else (255, 255, 255, 100)
        pygame.draw.rect(surface, border_color, 
                        (screen_x, screen_y, screen_width, screen_height), 
                        int(2 * camera.zoom))
                        
        # Draw section info
        if camera.zoom > 0.5:
            info_text = font_small.render(f"Section {self.id}", True, WHITE)
            surface.blit(info_text, (screen_x + 5, screen_y + 5))
            
            if self.is_underwater:
                water_text = font_small.render("Water", True, CYAN)
                surface.blit(water_text, (screen_x + 5, screen_y + 20))
                
            if self.is_warp_zone:
                warp_text = font_small.render("Warp", True, PURPLE)
                surface.blit(warp_text, (screen_x + 5, screen_y + 35))
                
    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "music": self.music_id,
            "background": self.background_id,
            "underwater": self.is_underwater,
            "warp_zone": self.is_warp_zone,
            "warp_destination": self.warp_dest
        }

class PathNode:
    def __init__(self, x, y, node_id=0):
        self.x = x
        self.y = y
        self.id = node_id
        self.linked_nodes = []
        
    def draw(self, surface, camera, all_nodes, selected=False):
        screen_x, screen_y = camera.world_to_screen((self.x, self.y))
        radius = int(8 * camera.zoom)
        
        # Draw connections
        for linked_id in self.linked_nodes:
            if linked_id in all_nodes:
                linked = all_nodes[linked_id]
                lx, ly = camera.world_to_screen((linked.x, linked.y))
                pygame.draw.line(surface, (100, 200, 255), 
                               (screen_x, screen_y), (lx, ly), 
                               int(2 * camera.zoom))
        
        # Draw node
        color = YELLOW if selected else (100, 200, 255)
        pygame.draw.circle(surface, color, (screen_x, screen_y), radius)
        pygame.draw.circle(surface, WHITE, (screen_x, screen_y), radius, int(2 * camera.zoom))
        
        # Draw ID
        if camera.zoom > 0.8:
            id_text = font_small.render(str(self.id), True, WHITE)
            surface.blit(id_text, (screen_x - 5, screen_y - 10))
            
    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "links": self.linked_nodes
        }

class Editor:
    def __init__(self):
        self.camera = Camera()
        self.mode = EditorMode.TILE
        self.selected_layer = Layer.MAIN
        self.selected_id = 1
        self.brush_size = 1
        
        # Level data
        self.tiles = []
        self.blocks = []
        self.npcs = []
        self.backgrounds = []
        self.sections = []
        self.path_nodes = {}
        self.next_node_id = 0
        
        # Level settings
        self.level_settings = {
            "name": "New Level",
            "width": 100 * GRID_SIZE,
            "height": 20 * GRID_SIZE,
            "music": 1,
            "background": 1,
            "stars_required": 0,
            "time_limit": 300,
            "start_pos": (2 * GRID_SIZE, 15 * GRID_SIZE)
        }
        
        # Selection
        self.selection = None
        self.selection_rect = None
        self.select_start = None
        self.selecting = False
        
        # UI state
        self.show_grid = True
        self.show_sections = True
        self.show_paths = True
        self.show_layers = [True] * 5
        
        # Undo/Redo
        self.history = []
        self.history_index = -1
        self.max_history = 50
        
        # File
        self.filename = None
        self.unsaved_changes = False
        
        # Initialize default section
        self.add_section(0, 0, self.level_settings["width"], self.level_settings["height"])
        
    def add_section(self, x, y, width, height):
        section_id = len(self.sections)
        section = Section(x, y, width, height, section_id)
        self.sections.append(section)
        self.record_history("Add Section")
        return section
        
    def add_path_node(self, x, y):
        # Check for overlap
        for node in self.path_nodes.values():
            if abs(node.x - x) < 5 and abs(node.y - y) < 5:
                return node

        node = PathNode(x, y, self.next_node_id)
        self.path_nodes[self.next_node_id] = node
        self.next_node_id += 1
        self.record_history("Add Path Node")
        return node
        
    def add_tile(self, x, y, tile_id=None):
        if tile_id is None:
            tile_id = self.selected_id
        
        # Check for duplicate
        for t in self.tiles:
            if t.x == x and t.y == y and t.layer == self.selected_layer:
                return t

        tile = Tile(x, y, tile_id, self.selected_layer)
        self.tiles.append(tile)
        self.record_history("Add Tile")
        return tile
        
    def add_block(self, x, y, block_id=None):
        if block_id is None:
            block_id = self.selected_id
            
        # Check for duplicate
        for b in self.blocks:
            if b.x == x and b.y == y and b.layer == self.selected_layer:
                return b
                
        block = Block(x, y, block_id, self.selected_layer)
        self.blocks.append(block)
        self.record_history("Add Block")
        return block
        
    def add_npc(self, x, y, npc_id=None):
        if npc_id is None:
            npc_id = self.selected_id
            
        # Check for duplicate
        for n in self.npcs:
            if n.x == x and n.y == y:
                return n

        npc = NPC(x, y, npc_id)
        self.npcs.append(npc)
        self.record_history("Add NPC")
        return npc
        
    def add_background(self, x, y, bg_id=None):
        if bg_id is None:
            bg_id = self.selected_id

        # Check for duplicate
        for bg in self.backgrounds:
            if bg.x == x and bg.y == y and bg.layer == self.selected_layer:
                return bg

        bg = Background(x, y, bg_id, self.selected_layer)
        self.backgrounds.append(bg)
        self.record_history("Add Background")
        return bg
        
    def delete_selected(self):
        if self.selection:
            if isinstance(self.selection, Tile):
                if self.selection in self.tiles: self.tiles.remove(self.selection)
            elif isinstance(self.selection, Block):
                if self.selection in self.blocks: self.blocks.remove(self.selection)
            elif isinstance(self.selection, NPC):
                if self.selection in self.npcs: self.npcs.remove(self.selection)
            elif isinstance(self.selection, Background):
                if self.selection in self.backgrounds: self.backgrounds.remove(self.selection)
            elif isinstance(self.selection, Section):
                if self.selection in self.sections: self.sections.remove(self.selection)
            elif isinstance(self.selection, PathNode):
                if self.selection.id in self.path_nodes: del self.path_nodes[self.selection.id]
            self.record_history("Delete Object")
            self.selection = None
            
    def record_history(self, action):
        # Save current state
        state = {
            "tiles": [t.to_dict() for t in self.tiles],
            "blocks": [b.to_dict() for b in self.blocks],
            "npcs": [n.to_dict() for n in self.npcs],
            "backgrounds": [bg.to_dict() for bg in self.backgrounds],
            "sections": [s.to_dict() for s in self.sections],
            "path_nodes": {k: v.to_dict() for k, v in self.path_nodes.items()},
            "action": action
        }
        
        # Truncate history if needed
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            
        self.history.append(state)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
            
        self.unsaved_changes = True
        
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_state(self.history[self.history_index])
            
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_state(self.history[self.history_index])
            
    def load_state(self, state):
        # Clear current state
        self.tiles = []
        self.blocks = []
        self.npcs = []
        self.backgrounds = []
        self.sections = []
        self.path_nodes = {}
        
        # Load tiles
        for t in state["tiles"]:
            tile = Tile(t["x"], t["y"], t["id"], Layer(t["layer"]), t.get("foreground", False))
            self.tiles.append(tile)
            
        # Load blocks
        for b in state["blocks"]:
            block = Block(b["x"], b["y"], b["id"], Layer(b["layer"]))
            block.contains = b.get("contents", [])
            block.slippery = b.get("slippery", False)
            block.invisible = b.get("invisible", False)
            self.blocks.append(block)
            
        # Load NPCs
        for n in state["npcs"]:
            npc = NPC(n["x"], n["y"], n["id"], n.get("direction", 1))
            npc.generator = n.get("generator", False)
            self.npcs.append(npc)
            
        # Load backgrounds
        for bg in state["backgrounds"]:
            background = Background(bg["x"], bg["y"], bg["id"], Layer(bg["layer"]))
            background.repeated = bg.get("repeated", True)
            self.backgrounds.append(background)
            
        # Load sections
        for s in state["sections"]:
            section = Section(s["x"], s["y"], s["width"], s["height"], s["id"])
            section.music_id = s.get("music", 0)
            section.background_id = s.get("background", 0)
            section.is_underwater = s.get("underwater", False)
            section.is_warp_zone = s.get("warp_zone", False)
            section.warp_dest = s.get("warp_destination", None)
            self.sections.append(section)
            
        # Load path nodes
        for node_id, node_data in state["path_nodes"].items():
            node = PathNode(node_data["x"], node_data["y"], node_data["id"])
            node.linked_nodes = node_data.get("links", [])
            self.path_nodes[node.id] = node
            self.next_node_id = max(self.next_node_id, node.id + 1)
            
    def save(self, filename=None):
        if filename:
            self.filename = filename
            
        if not self.filename:
            return
            
        data = {
            "metadata": {
                "version": "SMBX2 Editor 1.0",
                "name": self.level_settings["name"],
                "author": "Unknown",
                "created": pygame.time.get_ticks()
            },
            "settings": self.level_settings,
            "sections": [s.to_dict() for s in self.sections],
            "tiles": [t.to_dict() for t in self.tiles],
            "blocks": [b.to_dict() for b in self.blocks],
            "npcs": [n.to_dict() for n in self.npcs],
            "backgrounds": [bg.to_dict() for bg in self.backgrounds],
            "paths": [n.to_dict() for n in self.path_nodes.values()],
            "start_position": self.level_settings["start_pos"]
        }
        
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        self.unsaved_changes = False
        print(f"Level saved to {self.filename}")
        
    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Clear current level
            self.__init__()
            
            # Load settings
            if "settings" in data:
                self.level_settings.update(data["settings"])
                
            # Load sections
            if "sections" in data:
                self.sections = []
                for s in data["sections"]:
                    section = Section(s["x"], s["y"], s["width"], s["height"], s["id"])
                    section.music_id = s.get("music", 0)
                    section.background_id = s.get("background", 0)
                    section.is_underwater = s.get("underwater", False)
                    section.is_warp_zone = s.get("warp_zone", False)
                    section.warp_dest = s.get("warp_destination", None)
                    self.sections.append(section)
                    
            # Load other objects
            if "tiles" in data:
                for t in data["tiles"]:
                    tile = Tile(t["x"], t["y"], t["id"], Layer(t["layer"]), t.get("foreground", False))
                    self.tiles.append(tile)
                    
            if "blocks" in data:
                for b in data["blocks"]:
                    block = Block(b["x"], b["y"], b["id"], Layer(b["layer"]))
                    block.contains = b.get("contents", [])
                    block.slippery = b.get("slippery", False)
                    block.invisible = b.get("invisible", False)
                    self.blocks.append(block)
                    
            if "npcs" in data:
                for n in data["npcs"]:
                    npc = NPC(n["x"], n["y"], n["id"], n.get("direction", 1))
                    npc.generator = n.get("generator", False)
                    self.npcs.append(npc)
                    
            if "backgrounds" in data:
                for bg in data["backgrounds"]:
                    background = Background(bg["x"], bg["y"], bg["id"], Layer(bg["layer"]))
                    background.repeated = bg.get("repeated", True)
                    self.backgrounds.append(background)
                    
            if "paths" in data:
                for node_data in data["paths"]:
                    node = PathNode(node_data["x"], node_data["y"], node_data["id"])
                    node.linked_nodes = node_data.get("links", [])
                    self.path_nodes[node.id] = node
                    self.next_node_id = max(self.next_node_id, node.id + 1)
                    
            self.filename = filename
            self.unsaved_changes = False
            
            # Reset history
            self.history = []
            self.history_index = -1
            self.record_history("Load Level")
            
            print(f"Level loaded from {filename}")
            
        except Exception as e:
            print(f"Error loading level: {e}")
            
    def draw_grid(self, surface):
        if not self.show_grid:
            return
            
        # Calculate visible grid area
        start_x = int(self.camera.x // GRID_SIZE) * GRID_SIZE
        start_y = int(self.camera.y // GRID_SIZE) * GRID_SIZE
        # Safe zooming
        safe_zoom = max(0.1, self.camera.zoom)
        end_x = start_x + int(SCREEN_WIDTH / (safe_zoom * GRID_SIZE) + 2) * GRID_SIZE
        end_y = start_y + int((SCREEN_HEIGHT - TOOLBAR_HEIGHT) / (safe_zoom * GRID_SIZE) + 2) * GRID_SIZE
        
        # Draw grid lines
        grid_color = (80, 80, 80, 100)
        major_grid_color = (100, 100, 100, 150)
        
        for x in range(start_x, end_x, GRID_SIZE):
            screen_x = int((x - self.camera.x) * self.camera.zoom)
            color = major_grid_color if x % (GRID_SIZE * 4) == 0 else grid_color
            pygame.draw.line(surface, color, (screen_x, 0), (screen_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT), 1)
            
        for y in range(start_y, end_y, GRID_SIZE):
            screen_y = int((y - self.camera.y) * self.camera.zoom)
            color = major_grid_color if y % (GRID_SIZE * 4) == 0 else grid_color
            pygame.draw.line(surface, color, (0, screen_y), (SCREEN_WIDTH, screen_y), 1)
            
    def draw_cursor(self, surface, mouse_pos):
        # Convert mouse position to world grid coordinates
        world_x, world_y = self.camera.screen_to_world(mouse_pos)
        grid_x = (world_x // GRID_SIZE) * GRID_SIZE
        grid_y = (world_y // GRID_SIZE) * GRID_SIZE
        
        # Draw brush preview
        screen_x, screen_y = self.camera.world_to_screen((grid_x, grid_y))
        
        # Preview color based on mode
        if self.mode == EditorMode.TILE:
            preview_color = (100, 100, 200, 150)
        elif self.mode == EditorMode.BLOCK:
            preview_color = (200, 150, 100, 150)
        elif self.mode == EditorMode.NPC:
            preview_color = (200, 100, 100, 150)
        elif self.mode == EditorMode.BACKGROUND:
            preview_color = (100, 200, 100, 150)
        elif self.mode == EditorMode.SECTION:
            preview_color = (200, 200, 100, 100)
        elif self.mode == EditorMode.PATH:
            preview_color = (100, 200, 255, 150)
        else:
            preview_color = (200, 200, 200, 150)
            
        # Draw brush preview
        for i in range(self.brush_size):
            for j in range(self.brush_size):
                x = screen_x + i * GRID_SIZE * self.camera.zoom
                y = screen_y + j * GRID_SIZE * self.camera.zoom
                rect = pygame.Rect(x, y, 
                                 GRID_SIZE * self.camera.zoom,
                                 GRID_SIZE * self.camera.zoom)
                s = pygame.Surface((max(1, rect.width), max(1, rect.height)), pygame.SRCALPHA)
                s.fill(preview_color)
                surface.blit(s, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)
                
        # Draw crosshair at cursor
        pygame.draw.line(surface, YELLOW,
                        (mouse_pos[0] - 10, mouse_pos[1]),
                        (mouse_pos[0] + 10, mouse_pos[1]), 1)
        pygame.draw.line(surface, YELLOW,
                        (mouse_pos[0], mouse_pos[1] - 10),
                        (mouse_pos[0], mouse_pos[1] + 10), 1)
                        
    def draw_ui(self, surface):
        # Draw toolbar background
        toolbar_rect = pygame.Rect(0, SCREEN_HEIGHT - TOOLBAR_HEIGHT, SCREEN_WIDTH, TOOLBAR_HEIGHT)
        pygame.draw.rect(surface, DARK_GRAY, toolbar_rect)
        pygame.draw.line(surface, LIGHT_GRAY, (0, SCREEN_HEIGHT - TOOLBAR_HEIGHT), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT), 2)
                        
        # Draw mode selector
        modes = ["Tiles", "Blocks", "NPCs", "Background", "Paths", "Sections", "Settings"]
        for i, mode in enumerate(modes):
            rect = pygame.Rect(10 + i * 110, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 10, 100, 30)
            color = GREEN if i == self.mode.value else GRAY
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=5)
            
            mode_text = font_medium.render(mode, True, WHITE)
            mode_rect = mode_text.get_rect(center=rect.center)
            surface.blit(mode_text, mode_rect)
            
        # Draw layer selector
        layers = ["BGFG", "Destruct", "Main", "FG", "BG"]
        for i, layer in enumerate(layers):
            rect = pygame.Rect(10 + i * 80, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 50, 70, 25)
            color = BLUE if i == self.selected_layer.value else (50, 50, 50)
            pygame.draw.rect(surface, color, rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, rect, 1, border_radius=3)
            
            layer_text = font_small.render(layer, True, WHITE)
            layer_rect = layer_text.get_rect(center=rect.center)
            surface.blit(layer_text, layer_rect)
            
        # Draw object palette
        palette_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT + 85
        palette_height = TOOLBAR_HEIGHT - 95
        
        # Draw palette based on mode
        if self.mode == EditorMode.TILE:
            self.draw_tile_palette(surface, 10, palette_y, SCREEN_WIDTH - 20, palette_height)
        elif self.mode == EditorMode.BLOCK:
            self.draw_block_palette(surface, 10, palette_y, SCREEN_WIDTH - 20, palette_height)
        elif self.mode == EditorMode.NPC:
            self.draw_npc_palette(surface, 10, palette_y, SCREEN_WIDTH - 20, palette_height)
        elif self.mode == EditorMode.BACKGROUND:
            self.draw_bg_palette(surface, 10, palette_y, SCREEN_WIDTH - 20, palette_height)
            
        # Draw info panel
        info_rect = pygame.Rect(SCREEN_WIDTH - 300, 10, 290, 150)
        pygame.draw.rect(surface, (0, 0, 0, 180), info_rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, info_rect, 2, border_radius=5)
        
        # Camera info
        info_lines = [
            f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})",
            f"Zoom: {self.camera.zoom:.2f}x",
            f"Mode: {self.mode.name}",
            f"Layer: {self.selected_layer.name}",
            f"Brush: {self.brush_size}x{self.brush_size}",
            f"Selected ID: {self.selected_id}",
            f"Objects: {len(self.tiles)}T {len(self.blocks)}B {len(self.npcs)}N",
            f"Changes: {'Yes' if self.unsaved_changes else 'No'}"
        ]
        
        for i, line in enumerate(info_lines):
            text = font_small.render(line, True, WHITE)
            surface.blit(text, (info_rect.x + 10, info_rect.y + 10 + i * 18))
            
        # Draw quick controls
        controls = [
            "LMB: Place | RMB: Pan | MMB: Select",
            "Del: Delete | Z/Y: Undo/Redo",
            "G: Toggle Grid | L: Toggle Layers",
            "1-4: Brush Size | +/-: Zoom",
            "Ctrl+S: Save | Ctrl+O: Load"
        ]
        
        for i, control in enumerate(controls):
            text = font_small.render(control, True, LIGHT_GRAY)
            surface.blit(text, (10, 10 + i * 16))
            
    def draw_tile_palette(self, surface, x, y, width, height):
        # Draw tile palette
        palette_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (40, 40, 40), palette_rect)
        pygame.draw.rect(surface, WHITE, palette_rect, 1)
        
        # Draw tile grid
        tile_size = 40
        cols = width // (tile_size + 5)
        rows = height // (tile_size + 5)
        
        for i in range(min(100, rows * cols)):
            row = i // cols
            col = i % cols
            
            tile_x = x + 5 + col * (tile_size + 5)
            tile_y = y + 5 + row * (tile_size + 5)
            tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
            
            # Tile color based on ID
            tile_id = i + 1
            tile_color = self.get_tile_color(tile_id)
            
            pygame.draw.rect(surface, tile_color, tile_rect)
            pygame.draw.rect(surface, WHITE, tile_rect, 1)
            
            # Highlight selected
            if tile_id == self.selected_id:
                pygame.draw.rect(surface, YELLOW, tile_rect, 3)
                
            # Draw ID
            id_text = font_small.render(str(tile_id), True, WHITE)
            surface.blit(id_text, (tile_x + 2, tile_y + 2))
            
    def get_tile_color(self, tile_id):
        # Return color based on tile type
        if tile_id < 10:
            return (100, 100, 200)  # Basic ground
        elif tile_id < 20:
            return (150, 100, 50)   # Stone
        elif tile_id < 30:
            return (50, 150, 50)    # Grass
        elif tile_id < 40:
            return (200, 150, 50)   # Sand
        elif tile_id < 50:
            return (100, 100, 100)  # Metal
        elif tile_id < 60:
            return (150, 50, 150)   # Crystal
        elif tile_id < 70:
            return (50, 150, 150)   # Ice
        elif tile_id < 80:
            return (200, 50, 50)    # Lava
        else:
            return (200, 200, 100)  # Special
            
    def draw_block_palette(self, surface, x, y, width, height):
        # Draw block palette
        palette_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (40, 40, 40), palette_rect)
        pygame.draw.rect(surface, WHITE, palette_rect, 1)
        
        # Block types
        block_types = [
            (1, "Question", (255, 200, 0)),
            (2, "Brick", (180, 100, 50)),
            (3, "Empty", (100, 100, 100)),
            (4, "Invisible", (100, 100, 100, 128)),
            (5, "Note", (255, 100, 100)),
            (6, "PSwitch", (255, 0, 0)),
            (7, "Brick Coin", (255, 200, 100)),
            (8, "Brick Star", (255, 255, 100)),
        ]
        
        for i, (block_id, name, color) in enumerate(block_types):
            block_x = x + 10 + (i % 8) * 90
            block_y = y + 10 + (i // 8) * 60
            
            block_rect = pygame.Rect(block_x, block_y, 80, 50)
            
            # Draw block
            pygame.draw.rect(surface, color, block_rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, block_rect, 2, border_radius=3)
            
            # Highlight selected
            if block_id == self.selected_id:
                pygame.draw.rect(surface, YELLOW, block_rect, 3, border_radius=3)
                
            # Draw name
            name_text = font_small.render(name, True, WHITE)
            name_rect = name_text.get_rect(center=(block_x + 40, block_y + 20))
            surface.blit(name_text, name_rect)
            
            # Draw ID
            id_text = font_small.render(f"ID: {block_id}", True, BLACK)
            surface.blit(id_text, (block_x + 5, block_y + 35))
            
    def draw_npc_palette(self, surface, x, y, width, height):
        # Draw NPC palette
        palette_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (40, 40, 40), palette_rect)
        pygame.draw.rect(surface, WHITE, palette_rect, 1)
        
        # NPC types
        npc_types = [
            (1, "Goomba", (150, 100, 50)),
            (2, "Koopa", (50, 150, 50)),
            (3, "Piranha", (150, 50, 50)),
            (4, "Cheep", (50, 100, 150)),
            (5, "Boo", (200, 200, 200)),
            (6, "Hammer", (200, 100, 50)),
            (7, "Lakitu", (100, 200, 100)),
            (8, "Buzzy", (100, 50, 150)),
        ]
        
        for i, (npc_id, name, color) in enumerate(npc_types):
            npc_x = x + 10 + (i % 8) * 90
            npc_y = y + 10 + (i // 8) * 60
            
            npc_rect = pygame.Rect(npc_x, npc_y, 80, 50)
            
            # Draw NPC
            pygame.draw.rect(surface, color, npc_rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, npc_rect, 2, border_radius=3)
            
            # Highlight selected
            if npc_id == self.selected_id:
                pygame.draw.rect(surface, YELLOW, npc_rect, 3, border_radius=3)
                
            # Draw name
            name_text = font_small.render(name, True, WHITE)
            name_rect = name_text.get_rect(center=(npc_x + 40, npc_y + 20))
            surface.blit(name_text, name_rect)
            
            # Draw ID
            id_text = font_small.render(f"ID: {npc_id}", True, BLACK)
            surface.blit(id_text, (npc_x + 5, npc_y + 35))
            
    def draw_bg_palette(self, surface, x, y, width, height):
        # Draw background object palette
        palette_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (40, 40, 40), palette_rect)
        pygame.draw.rect(surface, WHITE, palette_rect, 1)
        
        # Background types
        bg_types = [
            (1, "Bush", (100, 200, 100)),
            (2, "Cloud", (200, 200, 200)),
            (3, "Hill", (50, 150, 50)),
            (4, "Tree", (100, 150, 50)),
            (5, "Fence", (150, 100, 50)),
            (6, "Column", (100, 100, 100)),
            (7, "Rock", (80, 80, 80)),
            (8, "Pipe", (0, 100, 0)),
        ]
        
        for i, (bg_id, name, color) in enumerate(bg_types):
            bg_x = x + 10 + (i % 8) * 90
            bg_y = y + 10 + (i // 8) * 60
            
            bg_rect = pygame.Rect(bg_x, bg_y, 80, 50)
            
            # Draw background object
            pygame.draw.rect(surface, color, bg_rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, bg_rect, 2, border_radius=3)
            
            # Highlight selected
            if bg_id == self.selected_id:
                pygame.draw.rect(surface, YELLOW, bg_rect, 3, border_radius=3)
                
            # Draw name
            name_text = font_small.render(name, True, WHITE)
            name_rect = name_text.get_rect(center=(bg_x + 40, bg_y + 20))
            surface.blit(name_text, name_rect)
            
            # Draw ID
            id_text = font_small.render(f"ID: {bg_id}", True, BLACK)
            surface.blit(id_text, (bg_x + 5, bg_y + 35))
            
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                # Mode selection
                elif event.key == pygame.K_1:
                    self.mode = EditorMode.TILE
                elif event.key == pygame.K_2:
                    self.mode = EditorMode.BLOCK
                elif event.key == pygame.K_3:
                    self.mode = EditorMode.NPC
                elif event.key == pygame.K_4:
                    self.mode = EditorMode.BACKGROUND
                elif event.key == pygame.K_5:
                    self.mode = EditorMode.PATH
                elif event.key == pygame.K_6:
                    self.mode = EditorMode.SECTION
                    
                # Layer selection
                elif event.key == pygame.K_F1:
                    self.selected_layer = Layer.BACKGROUND
                elif event.key == pygame.K_F2:
                    self.selected_layer = Layer.DESTRUCTIBLE
                elif event.key == pygame.K_F3:
                    self.selected_layer = Layer.MAIN
                elif event.key == pygame.K_F4:
                    self.selected_layer = Layer.FOREGROUND
                elif event.key == pygame.K_F5:
                    self.selected_layer = Layer.FGBACKGROUND
                    
                # Brush size
                elif event.key == pygame.K_q:
                    self.brush_size = max(1, self.brush_size - 1)
                elif event.key == pygame.K_e:
                    self.brush_size = min(10, self.brush_size + 1)
                    
                # Grid toggle
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                    
                # Layer visibility
                elif event.key == pygame.K_l:
                    for i in range(len(self.show_layers)):
                        self.show_layers[i] = not self.show_layers[i]
                        
                # Save/Load
                elif event.key == pygame.K_s and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    if self.filename:
                        self.save()
                    else:
                        # Show save dialog
                        try:
                            import tkinter as tk
                            from tkinter import filedialog
                            root = tk.Tk()
                            root.withdraw()
                            filename = filedialog.asksaveasfilename(
                                defaultextension=".json",
                                filetypes=[("SMBX2 Level", "*.json"), ("All files", "*.*")]
                            )
                            if filename:
                                self.save(filename)
                        except ImportError:
                            print("Tkinter not found. Cannot open file dialog.")
                            
                elif event.key == pygame.K_o and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    # Show load dialog
                    try:
                        import tkinter as tk
                        from tkinter import filedialog
                        root = tk.Tk()
                        root.withdraw()
                        filename = filedialog.askopenfilename(
                            filetypes=[("SMBX2 Level", "*.json"), ("All files", "*.*")]
                        )
                        if filename:
                            self.load(filename)
                    except ImportError:
                        print("Tkinter not found. Cannot open file dialog.")
                        
                # Undo/Redo
                elif event.key == pygame.K_z and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    self.undo()
                elif event.key == pygame.K_y and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    self.redo()
                    
                # Delete
                elif event.key == pygame.K_DELETE:
                    self.delete_selected()
                    
                # Zoom
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.camera.zoom = min(self.camera.zoom * 1.1, 4.0)
                elif event.key == pygame.K_MINUS:
                    self.camera.zoom = max(self.camera.zoom / 1.1, 0.25)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if click is in toolbar
                if mouse_pos[1] > SCREEN_HEIGHT - TOOLBAR_HEIGHT:
                    # Handle toolbar clicks
                    self.handle_toolbar_click(mouse_pos)
                else:
                    # Handle editor clicks
                    if event.button == 1:  # Left click
                        self.handle_editor_click(mouse_pos, keys)
                    elif event.button == 3:  # Right click
                        # Start pan
                        pass
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.selecting = False
                    
        # Update camera
        self.camera.update(keys, mouse_pos, mouse_buttons)
        
        # Place objects while dragging
        if mouse_buttons[0] and mouse_pos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT:
            if not self.selecting:
                self.handle_editor_click(mouse_pos, keys, drag=True)
                
        return True
        
    def handle_toolbar_click(self, mouse_pos):
        # Check mode buttons
        modes = ["Tiles", "Blocks", "NPCs", "Background", "Paths", "Sections", "Settings"]
        for i, mode in enumerate(modes):
            rect = pygame.Rect(10 + i * 110, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 10, 100, 30)
            if rect.collidepoint(mouse_pos):
                if i < len(EditorMode):
                    self.mode = EditorMode(i)
                return
                
        # Check layer buttons
        layers = ["BGFG", "Destruct", "Main", "FG", "BG"]
        for i, layer in enumerate(layers):
            rect = pygame.Rect(10 + i * 80, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 50, 70, 25)
            if rect.collidepoint(mouse_pos):
                if i < len(Layer):
                    self.selected_layer = Layer(i)
                return
                
        # Check palette clicks
        palette_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT + 85
        if mouse_pos[1] > palette_y:
            if self.mode == EditorMode.TILE:
                self.handle_tile_palette_click(mouse_pos)
            elif self.mode == EditorMode.BLOCK:
                self.handle_block_palette_click(mouse_pos)
            elif self.mode == EditorMode.NPC:
                self.handle_npc_palette_click(mouse_pos)
            elif self.mode == EditorMode.BACKGROUND:
                self.handle_bg_palette_click(mouse_pos)
                
    def handle_tile_palette_click(self, mouse_pos):
        # Calculate which tile was clicked
        palette_x, palette_y = 10, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 85
        tile_size = 40
        cols = (SCREEN_WIDTH - 20) // (tile_size + 5)
        
        rel_x = mouse_pos[0] - palette_x
        rel_y = mouse_pos[1] - palette_y
        
        col = rel_x // (tile_size + 5)
        row = rel_y // (tile_size + 5)
        
        tile_id = row * cols + col + 1
        
        if 1 <= tile_id <= 100:
            self.selected_id = tile_id
            
    def handle_block_palette_click(self, mouse_pos):
        # Calculate which block was clicked
        palette_x, palette_y = 10, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 85
        
        rel_x = mouse_pos[0] - palette_x
        rel_y = mouse_pos[1] - palette_y
        
        col = (rel_x - 10) // 90
        row = (rel_y - 10) // 60
        
        block_types = [
            (1, "Question", (255, 200, 0)),
            (2, "Brick", (180, 100, 50)),
            (3, "Empty", (100, 100, 100)),
            (4, "Invisible", (100, 100, 100, 128)),
            (5, "Note", (255, 100, 100)),
            (6, "PSwitch", (255, 0, 0)),
            (7, "Brick Coin", (255, 200, 100)),
            (8, "Brick Star", (255, 255, 100)),
        ]
        
        index = row * 8 + col
        if 0 <= index < len(block_types):
            self.selected_id = block_types[index][0]
            
    def handle_npc_palette_click(self, mouse_pos):
        # Calculate which NPC was clicked
        palette_x, palette_y = 10, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 85
        
        rel_x = mouse_pos[0] - palette_x
        rel_y = mouse_pos[1] - palette_y
        
        col = (rel_x - 10) // 90
        row = (rel_y - 10) // 60
        
        npc_types = [
            (1, "Goomba", (150, 100, 50)),
            (2, "Koopa", (50, 150, 50)),
            (3, "Piranha", (150, 50, 50)),
            (4, "Cheep", (50, 100, 150)),
            (5, "Boo", (200, 200, 200)),
            (6, "Hammer", (200, 100, 50)),
            (7, "Lakitu", (100, 200, 100)),
            (8, "Buzzy", (100, 50, 150)),
        ]
        
        index = row * 8 + col
        if 0 <= index < len(npc_types):
            self.selected_id = npc_types[index][0]
            
    def handle_bg_palette_click(self, mouse_pos):
        # Calculate which background object was clicked
        palette_x, palette_y = 10, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 85
        
        rel_x = mouse_pos[0] - palette_x
        rel_y = mouse_pos[1] - palette_y
        
        col = (rel_x - 10) // 90
        row = (rel_y - 10) // 60
        
        bg_types = [
            (1, "Bush", (100, 200, 100)),
            (2, "Cloud", (200, 200, 200)),
            (3, "Hill", (50, 150, 50)),
            (4, "Tree", (100, 150, 50)),
            (5, "Fence", (150, 100, 50)),
            (6, "Column", (100, 100, 100)),
            (7, "Rock", (80, 80, 80)),
            (8, "Pipe", (0, 100, 0)),
        ]
        
        index = row * 8 + col
        if 0 <= index < len(bg_types):
            self.selected_id = bg_types[index][0]
            
    def handle_editor_click(self, mouse_pos, keys, drag=False):
        world_pos = self.camera.screen_to_world(mouse_pos)
        grid_x = (world_pos[0] // GRID_SIZE) * GRID_SIZE
        grid_y = (world_pos[1] // GRID_SIZE) * GRID_SIZE
        
        # Check for selection
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.selection = None
            self.select_start = (grid_x, grid_y)
            self.selecting = True
            return
            
        # Clear selection if not shift clicking
        if not drag:
            self.selection = None
            
        # Place or select object based on mode
        if self.mode == EditorMode.TILE:
            if not keys[pygame.K_LALT]:  # Not alt - place tile
                for i in range(self.brush_size):
                    for j in range(self.brush_size):
                        x = grid_x + i * GRID_SIZE
                        y = grid_y + j * GRID_SIZE
                        self.add_tile(x, y)
            else:  # Alt - select tile
                for tile in reversed(self.tiles):
                    if (tile.x <= world_pos[0] <= tile.x + tile.width and
                        tile.y <= world_pos[1] <= tile.y + tile.height):
                        self.selection = tile
                        break
                        
        elif self.mode == EditorMode.BLOCK:
            if not keys[pygame.K_LALT]:
                for i in range(self.brush_size):
                    for j in range(self.brush_size):
                        x = grid_x + i * GRID_SIZE
                        y = grid_y + j * GRID_SIZE
                        self.add_block(x, y)
            else:
                for block in reversed(self.blocks):
                    if (block.x <= world_pos[0] <= block.x + block.width and
                        block.y <= world_pos[1] <= block.y + block.height):
                        self.selection = block
                        break
                        
        elif self.mode == EditorMode.NPC:
            if not keys[pygame.K_LALT]:
                self.add_npc(grid_x, grid_y)
            else:
                for npc in reversed(self.npcs):
                    if (npc.x <= world_pos[0] <= npc.x + npc.width and
                        npc.y <= world_pos[1] <= npc.y + npc.height):
                        self.selection = npc
                        break
                        
        elif self.mode == EditorMode.BACKGROUND:
            if not keys[pygame.K_LALT]:
                self.add_background(grid_x, grid_y)
            else:
                for bg in reversed(self.backgrounds):
                    if (bg.x <= world_pos[0] <= bg.x + bg.width and
                        bg.y <= world_pos[1] <= bg.y + bg.height):
                        self.selection = bg
                        break
                        
        elif self.mode == EditorMode.PATH:
            if not keys[pygame.K_LALT]:
                self.add_path_node(grid_x, grid_y)
            else:
                for node in self.path_nodes.values():
                    if (abs(node.x - world_pos[0]) < GRID_SIZE and
                        abs(node.y - world_pos[1]) < GRID_SIZE):
                        self.selection = node
                        break
                        
        elif self.mode == EditorMode.SECTION:
            if not keys[pygame.K_LALT]:
                # Start drawing section
                self.select_start = (grid_x, grid_y)
                self.selecting = True
            else:
                for section in reversed(self.sections):
                    if (section.x <= world_pos[0] <= section.x + section.width and
                        section.y <= world_pos[1] <= section.y + section.height):
                        self.selection = section
                        break
                        
    def draw(self, surface):
        # Clear screen
        surface.fill(BACKGROUND_GRAY)
        
        # Draw grid
        self.draw_grid(surface)
        
        # Draw sections
        if self.show_sections:
            for section in self.sections:
                selected = (self.selection == section)
                section.draw(surface, self.camera, selected)
                
        # Draw path nodes
        if self.show_paths and self.mode == EditorMode.PATH:
            for node in self.path_nodes.values():
                selected = (self.selection == node)
                node.draw(surface, self.camera, self.path_nodes, selected)
                
        # Draw objects by layer
        for layer in Layer:
            if not self.show_layers[layer.value]:
                continue
                
            # Draw tiles in this layer
            for tile in self.tiles:
                if tile.layer == layer:
                    selected = (self.selection == tile)
                    tile.draw(surface, self.camera, selected)
                    
            # Draw blocks in this layer
            for block in self.blocks:
                if block.layer == layer:
                    selected = (self.selection == block)
                    block.draw(surface, self.camera, selected)
                    
            # Draw backgrounds in this layer
            for bg in self.backgrounds:
                if bg.layer == layer:
                    selected = (self.selection == bg)
                    bg.draw(surface, self.camera, selected)
                    
        # Draw NPCs (always on main layer)
        for npc in self.npcs:
            selected = (self.selection == npc)
            npc.draw(surface, self.camera, selected)
            
        # Draw selection rectangle
        if self.selecting and self.select_start:
            start_x, start_y = self.select_start
            world_pos = self.camera.screen_to_world(pygame.mouse.get_pos())
            end_x, end_y = world_pos
            
            rect_x = min(start_x, end_x)
            rect_y = min(start_y, end_y)
            rect_width = abs(end_x - start_x)
            rect_height = abs(end_y - start_y)
            
            screen_x, screen_y = self.camera.world_to_screen((rect_x, rect_y))
            screen_width = int(rect_width * self.camera.zoom)
            screen_height = int(rect_height * self.camera.zoom)
            
            selection_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
            pygame.draw.rect(surface, (255, 255, 0, 100), selection_rect)
            pygame.draw.rect(surface, YELLOW, selection_rect, 2)
            
        # Draw cursor
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT:
            self.draw_cursor(surface, mouse_pos)
            
        # Draw UI
        self.draw_ui(surface)
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()

# Run the editor
if __name__ == "__main__":
    editor = Editor()
    editor.run()

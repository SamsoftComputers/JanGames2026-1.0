import pygame
import sys
import time
import random
import math

# ==========================================
# CAT'S FNF TEMPLATE 0.1 (PYTHON PORT)
# ==========================================
# mimics HaxeFlixel architecture for FNF
# Requires: pip install pygame

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Cat's FNF Template 0.1"

# Colors
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_GRAY = (100, 100, 100)
C_RED = (255, 50, 80)    # Right
C_GREEN = (0, 255, 0)    # Up
C_BLUE = (0, 255, 255)   # Down
C_PURPLE = (180, 0, 255) # Left

# Input Keys (WASD / Arrows)
KEYS_LEFT = [pygame.K_LEFT, pygame.K_a]
KEYS_DOWN = [pygame.K_DOWN, pygame.K_s]
KEYS_UP = [pygame.K_UP, pygame.K_w]
KEYS_RIGHT = [pygame.K_RIGHT, pygame.K_d]

# --- HaxeFlixel Emulation Layer ---
class FlxG:
    """Global helper class mimicking HaxeFlixel's FlxG"""
    width = SCREEN_WIDTH
    height = SCREEN_HEIGHT
    elapsed = 0.0
    keys = []
    keys_just_pressed = []
    keys_just_released = []
    
    @staticmethod
    def log(message):
        print(f"[FlxG] {message}")

class FlxObject:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.active = True
        self.visible = True

    def update(self, elapsed):
        pass

    def draw(self, surface):
        pass

class FlxSprite(FlxObject):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)
        self.alpha = 255
        self.angle = 0
        self.scale = 1.0
        self.color = C_WHITE
        # Simple rect placeholder
        self.width = 50
        self.height = 50

    def draw_rect(self, surface, color, rect):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(color)
        s.set_alpha(self.alpha)
        surface.blit(s, (rect.x, rect.y))

class FlxState:
    def __init__(self):
        self.members = []

    def add(self, obj):
        self.members.append(obj)
        return obj

    def update(self, elapsed):
        for m in self.members:
            if m.active:
                m.update(elapsed)

    def draw(self, surface):
        for m in self.members:
            if m.visible:
                m.draw(surface)

# --- Engine Specific Classes ---

class Conductor:
    """Handles song position and beats"""
    bpm = 100
    crochet = 0 # Step time in ms
    song_position = 0
    safe_zone_offset = 166 # 10 frames at 60fps
    
    @staticmethod
    def change_bpm(new_bpm):
        Conductor.bpm = new_bpm
        Conductor.crochet = (60 / Conductor.bpm) * 1000

class Note(FlxSprite):
    """A scrolling note object"""
    def __init__(self, time, data, parent_strum_line=None):
        super().__init__(0, -200)
        self.strum_time = time
        self.note_data = data # 0:Left, 1:Down, 2:Up, 3:Right
        self.must_press = True # Does player hit this?
        self.was_hit = False
        self.too_late = False
        self.speed = 2.2
        self.width = 100
        self.height = 100
        
        # Determine color
        if self.note_data == 0: self.color = C_PURPLE
        elif self.note_data == 1: self.color = C_BLUE
        elif self.note_data == 2: self.color = C_GREEN
        elif self.note_data == 3: self.color = C_RED

    def update(self, elapsed):
        # Calculate Y based on song position (Scrolls Up)
        # Formula: TargetY - (Distance * Speed)
        # We want the note to be at the strum line (Y=100) when song_pos == strum_time
        
        diff = (self.strum_time - Conductor.song_position)
        
        # Downscroll logic (simplified to Upscroll for template)
        # Strum line is at Y = 100
        # If diff is positive, note is coming (below line)
        # If diff is 0, note is at line
        
        # Upscroll: Line at 100. Notes come from bottom (Height).
        # Actually FNF defaults to Upscroll: Line at Top (100). Notes come from Bottom.
        # Wait, FNF Standard is: Static arrows at top. Notes come from bottom up.
        
        target_y = 100
        self.y = target_y + (diff * (0.45 * self.speed))

        # Check if missed
        if self.strum_time < Conductor.song_position - Conductor.safe_zone_offset and not self.was_hit:
            self.too_late = True

    def draw(self, surface):
        # Draw Arrow
        # Simple Triangle/Arrow shape
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 4)
        
        # Inner fill based on type
        if self.note_data == 0: # Left
            pygame.draw.polygon(surface, self.color, [(self.x+10, center_y), (self.x+90, self.y+10), (self.x+90, self.y+90)])
        elif self.note_data == 1: # Down
            pygame.draw.polygon(surface, self.color, [(self.x+10, self.y+10), (self.x+90, self.y+10), (center_x, self.y+90)])
        elif self.note_data == 2: # Up
            pygame.draw.polygon(surface, self.color, [(center_x, self.y+10), (self.x+10, self.y+90), (self.x+90, self.y+90)])
        elif self.note_data == 3: # Right
            pygame.draw.polygon(surface, self.color, [(self.x+10, self.y+10), (self.x+90, center_y), (self.x+10, self.y+90)])


class StrumLine(FlxObject):
    """The static arrows at the top"""
    def __init__(self, x, id):
        super().__init__(x, 100)
        self.id = id # 0-3
        self.width = 100
        self.height = 100
        self.scale_val = 1.0
        self.reset_anim_timer = 0
        
        if self.id == 0: self.base_color = C_PURPLE
        elif self.id == 1: self.base_color = C_BLUE
        elif self.id == 2: self.base_color = C_GREEN
        elif self.id == 3: self.base_color = C_RED

    def play_anim(self, anim):
        if anim == "confirm":
            self.scale_val = 0.8
            self.reset_anim_timer = 0.1
        elif anim == "press":
            self.scale_val = 0.9
            self.reset_anim_timer = 0.1

    def update(self, elapsed):
        if self.reset_anim_timer > 0:
            self.reset_anim_timer -= elapsed
            if self.reset_anim_timer <= 0:
                self.scale_val = 1.0

    def draw(self, surface):
        # Draw static arrow (Gray outline)
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # If pressing, fill it
        fill = False
        if self.scale_val < 1.0:
            fill = True
            
        final_rect = rect.inflate((1-self.scale_val)*-20, (1-self.scale_val)*-20)
        
        if fill:
            pygame.draw.rect(surface, self.base_color, final_rect)
        else:
            pygame.draw.rect(surface, C_GRAY, final_rect, 4)

class PlayState(FlxState):
    def __init__(self):
        super().__init__()
        
        # Stats
        self.score = 0
        self.misses = 0
        self.accuracy = 0.0
        self.health = 1.0 # 0 to 2 (FNF style)
        self.combo = 0
        
        # Groups
        self.strum_lines = []
        self.notes = []
        
        # Setup UI
        self.score_txt = FlxText(0, 10, SCREEN_WIDTH, "Score: 0", 24)
        
        # Create Strum Lines (4 lanes)
        lane_width = 110
        start_x = (SCREEN_WIDTH / 2) - (lane_width * 2)
        
        for i in range(4):
            strum = StrumLine(start_x + (i * lane_width), i)
            self.strum_lines.append(strum)
            self.add(strum)

        # Generate Chart (Procedural for template)
        Conductor.change_bpm(120)
        # Create 50 notes
        for i in range(100):
            # Random lane
            lane = random.randint(0, 3)
            # Time: Start at 2000ms, add steps
            beat_time = 2000 + (i * Conductor.crochet)
            # Add some syncopation sometimes
            if i % 4 == 2:
                beat_time += Conductor.crochet / 2
                
            n = Note(beat_time, lane)
            n.x = self.strum_lines[lane].x
            self.notes.append(n)
            self.add(n)
            
        # Music (Mock)
        self.music_start_time = time.time() * 1000
        
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.rating_txt = ""
        self.rating_timer = 0

    def update(self, elapsed):
        super().update(elapsed)
        
        # Update Song Pos
        Conductor.song_position = (time.time() * 1000) - self.music_start_time
        
        # Input Handling
        pressed = [False, False, False, False]
        just_pressed = [False, False, False, False]
        
        keys = pygame.key.get_pressed()
        
        # Map inputs
        if keys[KEYS_LEFT[0]] or keys[KEYS_LEFT[1]]: pressed[0] = True
        if keys[KEYS_DOWN[0]] or keys[KEYS_DOWN[1]]: pressed[1] = True
        if keys[KEYS_UP[0]] or keys[KEYS_UP[1]]: pressed[2] = True
        if keys[KEYS_RIGHT[0]] or keys[KEYS_RIGHT[1]]: pressed[3] = True
        
        # Check simple just_pressed logic (naive implementation for template)
        # ideally we use an input manager
        
        # Process Strum Animations
        for i in range(4):
            if pressed[i]:
                self.strum_lines[i].play_anim("press")

        # Hit Detection
        # We need to know which keys were JUST pressed this frame
        # For this template, we iterate events in Main
        
        # Clean up off-screen notes
        for n in self.notes[:]:
            if n.y < -150: # Scrolled past top
                if not n.was_hit:
                    self.note_miss(n)
                self.notes.remove(n)
                self.members.remove(n)
                
            if n.too_late and not n.was_hit:
                 self.note_miss(n)

    def on_key_press(self, lane_id):
        self.strum_lines[lane_id].play_anim("confirm")
        
        # Find hittable note in this lane
        possible_notes = [n for n in self.notes if n.note_data == lane_id and not n.was_hit and not n.too_late]
        
        if not possible_notes:
            # Ghost tapping (no penalty in modern FNF, but we can add small health drain)
            return

        # Sort by closeness to strum time
        possible_notes.sort(key=lambda x: abs(x.strum_time - Conductor.song_position))
        
        target = possible_notes[0]
        diff = abs(target.strum_time - Conductor.song_position)
        
        if diff < Conductor.safe_zone_offset:
            self.note_hit(target, diff)

    def note_hit(self, note, diff):
        note.was_hit = True
        note.visible = False
        self.health += 0.023
        if self.health > 2: self.health = 2
        
        # Ratings
        rating = "SHIT"
        score_add = 50
        if diff < 45: # Sick window
            rating = "SICK!!"
            score_add = 350
        elif diff < 90:
            rating = "GOOD!"
            score_add = 200
        elif diff < 135:
            rating = "BAD"
            score_add = 100
            
        self.score += score_add
        self.combo += 1
        
        self.rating_txt = f"{rating} [{self.combo}]"
        self.rating_timer = 0.5
        
        # Remove from active lists
        if note in self.notes: self.notes.remove(note)
        if note in self.members: self.members.remove(note)

    def note_miss(self, note):
        note.was_hit = True # mark as processed
        self.health -= 0.05
        self.combo = 0
        self.misses += 1
        self.score -= 10
        self.rating_txt = "MISS"
        self.rating_timer = 0.5
        
        # Tint strum line red temporarily?
        # self.strum_lines[note.note_data].color = C_RED

    def draw(self, surface):
        # Draw Background
        surface.fill(C_BLACK)
        
        # Draw Lane Underlay
        lane_width = 110
        start_x = (SCREEN_WIDTH / 2) - (lane_width * 2)
        pygame.draw.rect(surface, (20, 20, 20), (start_x - 10, 0, (lane_width*4) + 20, SCREEN_HEIGHT))

        super().draw(surface)
        
        # UI Overlay
        # Health Bar
        bar_width = 600
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 50
        
        # BG
        pygame.draw.rect(surface, C_GRAY, (bar_x, bar_y, bar_width, bar_height))
        # Fill (Red = Dad/Empty, Green = BF/Full)
        fill_pct = self.health / 2.0
        fill_width = int(bar_width * fill_pct)
        
        # Dad side (Red)
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # BF side (Green) over top
        # In FNF, bar goes right to left or center. 
        # Simplified: Left is empty, Right is full.
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))
        
        # Score Text
        score_surf = self.font.render(f"Score: {self.score} | Misses: {self.misses}", True, C_WHITE)
        surface.blit(score_surf, (20, SCREEN_HEIGHT - 40))
        
        # Rating Popup
        if self.rating_timer > 0:
            self.rating_timer -= 0.016 # approx elapsed
            rat_surf = self.font.render(self.rating_txt, True, C_WHITE)
            # Center it
            rx = (SCREEN_WIDTH - rat_surf.get_width()) // 2
            ry = (SCREEN_HEIGHT // 2) - 50
            surface.blit(rat_surf, (rx, ry))
            
        if self.health <= 0:
            fail_surf = self.font.render("GAME OVER", True, (255, 0, 0))
            surface.blit(fail_surf, ((SCREEN_WIDTH/2)-60, SCREEN_HEIGHT/2))


class FlxText(FlxObject):
    def __init__(self, x, y, w, text, size):
        super().__init__(x, y)
        self.text = text
        self.font = pygame.font.SysFont("Arial", size)
        self.color = C_WHITE
        
    def draw(self, surface):
        img = self.font.render(self.text, True, self.color)
        surface.blit(img, (self.x, self.y))


# --- Main Application ---
def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # State Management
    current_state = PlayState()
    
    running = True
    while running:
        # Time Management
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds
        FlxG.elapsed = dt
        
        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Key Presses for Engine
            if event.type == pygame.KEYDOWN:
                if event.key in KEYS_LEFT: current_state.on_key_press(0)
                if event.key in KEYS_DOWN: current_state.on_key_press(1)
                if event.key in KEYS_UP:   current_state.on_key_press(2)
                if event.key in KEYS_RIGHT: current_state.on_key_press(3)
                
                if event.key == pygame.K_r: # Restart
                    current_state = PlayState()

        # Update
        current_state.update(dt)
        
        # Draw
        current_state.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

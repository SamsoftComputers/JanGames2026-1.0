import pygame
import math
import random
import array

# --- CatSDK [C] 1:1 FAMICOM Space Invaders ---
# Native 600x400 @ 60 FPS - Frame Perfect
SCREEN_W, SCREEN_H = 600, 400
FPS = 60
FRAME_TIME = 1000 / FPS  # 16.67ms per frame

# Colors (Famicom palette style)
BLACK  = (0, 0, 0)
WHITE  = (252, 252, 252)
GREEN  = (0, 184, 0)
RED    = (228, 0, 88)
CYAN   = (0, 232, 216)
YELLOW = (216, 216, 0)
GREY   = (152, 152, 152)
PURPLE = (152, 120, 248)

# --- Sprite Data (scaled 2x for 600x400) ---
PLAYER_DATA = [
    [0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,1,1,1,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1]
]

SQUID_A = [[0,0,0,1,1,0,0,0],[0,0,1,1,1,1,0,0],[0,1,1,1,1,1,1,0],[1,1,0,1,1,0,1,1],[1,1,1,1,1,1,1,1],[0,0,1,0,0,1,0,0],[0,1,0,1,1,0,1,0],[1,0,1,0,0,1,0,1]]
SQUID_B = [[0,0,0,1,1,0,0,0],[0,0,1,1,1,1,0,0],[0,1,1,1,1,1,1,0],[1,1,0,1,1,0,1,1],[1,1,1,1,1,1,1,1],[0,1,0,1,1,0,1,0],[1,0,0,0,0,0,0,1],[0,1,0,0,0,0,1,0]]
CRAB_A = [[0,0,1,0,0,0,1,0,0],[0,0,0,1,0,1,0,0,0],[0,0,1,1,1,1,1,0,0],[0,1,1,0,1,0,1,1,0],[1,1,1,1,1,1,1,1,1],[1,0,1,1,1,1,1,0,1],[1,0,1,0,0,0,1,0,1],[0,0,0,1,1,1,0,0,0]]
CRAB_B = [[0,0,1,0,0,0,1,0,0],[1,0,0,1,0,1,0,0,1],[1,0,1,1,1,1,1,0,1],[1,1,1,0,1,0,1,1,1],[0,1,1,1,1,1,1,1,0],[0,0,1,1,1,1,1,0,0],[0,0,1,0,0,0,1,0,0],[0,1,0,0,0,0,0,1,0]]
OCTO_A = [[0,0,0,1,1,1,1,0,0,0],[0,1,1,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1,1,1],[1,1,1,0,0,0,0,1,1,1],[1,1,1,1,1,1,1,1,1,1],[0,0,1,1,0,0,1,1,0,0],[0,1,1,0,1,1,0,1,1,0],[1,1,0,0,0,0,0,0,1,1]]
OCTO_B = [[0,0,0,1,1,1,1,0,0,0],[0,1,1,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1,1,1],[1,1,1,0,0,0,0,1,1,1],[1,1,1,1,1,1,1,1,1,1],[0,0,0,1,1,1,1,0,0,0],[0,0,1,1,0,0,1,1,0,0],[1,1,0,0,0,0,0,0,1,1]]
UFO_DATA = [[0,0,0,0,1,1,1,1,1,1,0,0,0,0],[0,0,1,1,1,1,1,1,1,1,1,1,0,0],[0,1,1,1,1,1,1,1,1,1,1,1,1,0],[1,1,0,1,1,0,1,1,0,1,1,0,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1],[0,0,1,1,1,0,0,1,1,1,0,0,0,0],[0,0,0,1,0,0,0,0,1,0,0,0,0,0]]
BUNKER_DATA = [[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1],[1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1],[1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1]]

# Sprite scale factor for 600x400
SPRITE_SCALE = 2

# --- Frame-Perfect Movement Speeds (pixels per frame @ 60fps) ---
PLAYER_SPEED = 3.0          # ~180 pixels/sec
PLAYER_SHOT_SPEED = -6.0    # Fast upward
ENEMY_SHOT_SPEED = 3.5      # Slower downward
UFO_SPEED = 1.5             # Steady UFO crawl
INVADER_STEP = 6            # Pixels per step
INVADER_DROP = 12           # Pixels dropped when reversing
PARTICLE_SPEED_MAX = 3.0    
STAR_SPEEDS = [0.3, 0.6, 1.0]
POWERUP_SPEED = 2.0

# --- Sound Synthesis ---
pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)

def make_square_beep(freq, dur_sec, vol=5000):
    sr = 22050
    n = int(sr * dur_sec)
    buf = array.array('h', [0] * n)
    period = sr / freq
    for i in range(n):
        if (i % int(period)) < (period / 2):
            buf[i] = vol
        else:
            buf[i] = -vol
    return pygame.mixer.Sound(buffer=buf)

def make_noise(dur_sec, vol=3000):
    sr = 22050
    n = int(sr * dur_sec)
    buf = array.array('h', [random.randint(-vol, vol) for _ in range(n)])
    return pygame.mixer.Sound(buffer=buf)

# Sounds initialized after pygame.init()
SND_SHOOT = None
SND_HIT = None
SND_UFO = None
SND_DIE = None
SND_STEPS = None
SND_POWER = None
# DOS Boot sounds
SND_DOS_BEEP = None
SND_DOS_BOOP = None
SND_DOS_BOOT = None
SND_DOS_OK = None

def init_sounds():
    global SND_SHOOT, SND_HIT, SND_UFO, SND_DIE, SND_STEPS, SND_POWER
    global SND_DOS_BEEP, SND_DOS_BOOP, SND_DOS_BOOT, SND_DOS_OK
    SND_SHOOT = make_square_beep(880, 0.05)
    SND_HIT   = make_noise(0.12)
    SND_UFO   = make_square_beep(440, 0.08)
    SND_DIE   = make_noise(0.25)
    SND_STEPS = [make_square_beep(f, 0.08) for f in [92, 82, 73, 62]]
    SND_POWER = make_square_beep(660, 0.08)
    # DOS-style boot sounds
    SND_DOS_BEEP = make_square_beep(1000, 0.015, vol=3000)  # Short high beep for typing
    SND_DOS_BOOP = make_square_beep(600, 0.04, vol=4000)    # Lower boop for line complete
    SND_DOS_BOOT = make_square_beep(800, 0.08, vol=4500)    # Boot start beep
    SND_DOS_OK   = make_square_beep(1200, 0.06, vol=4000)   # Success beep

def pixarray_to_surf(data, color, scale=SPRITE_SCALE):
    h = len(data)
    w = len(data[0]) if h > 0 else 0
    s = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            if data[y][x]:
                pygame.draw.rect(s, color, (x*scale, y*scale, scale, scale))
    return s

# --- Game Objects ---
class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'color', 'life']
    
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-PARTICLE_SPEED_MAX, PARTICLE_SPEED_MAX)
        self.vy = random.uniform(-PARTICLE_SPEED_MAX * 1.5, PARTICLE_SPEED_MAX * 0.5)
        self.color = color
        self.life = random.randint(15, 35)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # Gravity
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (int(self.x), int(self.y), 2, 2))

class Star:
    __slots__ = ['x', 'y', 'speed', 'color']
    
    def __init__(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(0, SCREEN_H)
        self.speed = random.choice(STAR_SPEEDS)
        brightness = int(40 + self.speed * 60)
        self.color = (brightness, brightness, brightness)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_H:
            self.y = 0
            self.x = random.randint(0, SCREEN_W)

class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 7, y, 14, 14)
        self.type = random.choice([0, 1])  # 0=Laser, 1=1UP
        self.color = RED if self.type == 0 else PURPLE
        self.flash_timer = 0
    
    def update(self):
        self.rect.y += POWERUP_SPEED
        self.flash_timer = (self.flash_timer + 1) % 12
        return self.rect.top < SCREEN_H

    def draw(self, surf):
        c = WHITE if self.flash_timer < 6 else self.color
        pygame.draw.rect(surf, c, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect.inflate(-6, -6))

class Message:
    def __init__(self, text, x, y, color, font):
        self.img = font.render(text, True, color)
        self.rect = self.img.get_rect(center=(x, y))
        self.life = 60
        self.vy = -0.8
    
    def update(self):
        self.rect.y += self.vy
        self.life -= 1
        return self.life > 0
        
    def draw(self, surf):
        surf.blit(self.img, self.rect)

class Shot:
    __slots__ = ['rect', 'dy', 'color']
    
    def __init__(self, x, y, dy, color):
        self.rect = pygame.Rect(x - 2, y, 4, 10)
        self.dy = dy
        self.color = color

    def update(self):
        self.rect.y += self.dy

class Invader:
    __slots__ = ['frames', 'rect', 'anim_frame', 'points', 'col', 'color']
    
    def __init__(self, x, y, frame_datas, color, points, col):
        self.frames = [pixarray_to_surf(f, color) for f in frame_datas]
        self.rect = self.frames[0].get_rect(topleft=(x, y))
        self.anim_frame = 0
        self.points = points
        self.col = col
        self.color = color

    def draw(self, surf):
        surf.blit(self.frames[self.anim_frame], self.rect.topleft)

class ArcadeInvaders:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF)
        pygame.display.set_caption("Cat's Space Invaders - 60 FPS Famicom Edition")
        self.clock = pygame.time.Clock()
        
        init_sounds()
        
        # Fonts scaled for 600x400
        self.font = pygame.font.SysFont("monospace", 24, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 14, bold=True)
        self.tiny_font = pygame.font.SysFont("monospace", 12)

        self.player_surf = pixarray_to_surf(PLAYER_DATA, GREEN)
        
        # Menu
        self.menu_options = ["START GAME", "HOW TO PLAY", "CREDITS", "EXIT"]
        self.selected = 0
        
        # Boot Sequence
        self.state = "BOOT"
        self.boot_lines = [
            "CAT-SDK BIOS v2.0", 
            "CATSDK LOADED................[Y]",
            "CATSDK AUGMENTER FAMICOM BREWING..[Y]",
            "INITIALIZING FAMICOM MODE....[Y]", 
            "LOADING 60 FPS ENGINE........[Y]", 
            "RESOLUTION: 600x400..........[Y]",
            "SPRITES LOADED...............[Y]",
            "SOUND SYSTEM ACTIVE..........[Y]",
            "INVADERS DETECTED............[Y]",
            "SYSTEM READY. PRESS ANY KEY."
        ]
        self.current_line = 0
        self.char_idx = 0
        self.boot_timer = 0
        self.boot_started = False  # Track if initial beep played
        self.boot_complete_timer = 0  # Timer after boot completes
        
        # FX
        self.particles = []
        self.stars = [Star() for _ in range(60)]
        self.powerups = []
        self.messages = []
        
        # Game State
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.shot_speed = PLAYER_SHOT_SPEED
        self.paused = False
        
        # Frame counter for accurate timing
        self.frame_count = 0
        
        self.reset()

    def reset(self):
        pw, ph = self.player_surf.get_size()
        self.player_x = float(SCREEN_W // 2 - pw // 2)
        self.player_rect = pygame.Rect(int(self.player_x), SCREEN_H - 30, pw, ph)
        
        self.invaders = []
        self.enemy_shots = []
        self.powerups = []
        self.messages = []
        self.particles = []
        self.player_shot = None
        self.ufo = None
        self.ufo_timer = 0
        self.lives = 3
        self.game_over = False
        self.inv_dir = 1
        self.inv_move_timer = 0
        self.inv_step_idx = 0
        self.shot_speed = PLAYER_SHOT_SPEED
        self.shot_cooldown = 0
        
        self.reset_invaders()
        self.setup_bunkers()

    def setup_bunkers(self):
        self.bunkers = []
        bunker_y = SCREEN_H - 80
        spacing = SCREEN_W // 5
        for i in range(4):
            bx = spacing * (i + 1) - 16
            surf = pixarray_to_surf(BUNKER_DATA, GREEN)
            self.bunkers.append([surf, pygame.Rect(bx, bunker_y, surf.get_width(), surf.get_height())])

    def reset_invaders(self):
        self.invaders = []
        start_y = 60 + (self.level - 1) * 10
        col_spacing = 44
        row_spacing = 32
        start_x = (SCREEN_W - (11 * col_spacing)) // 2
        
        for row in range(5):
            for col in range(11):
                x = start_x + col * col_spacing
                y = start_y + row * row_spacing
                if row == 0:
                    data, color, pts = [SQUID_A, SQUID_B], CYAN, 30
                elif row < 3:
                    data, color, pts = [CRAB_A, CRAB_B], YELLOW, 20
                else:
                    data, color, pts = [OCTO_A, OCTO_B], WHITE, 10
                self.invaders.append(Invader(x, y, data, color, pts, col))

    def create_explosion(self, x, y, color, count=12):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def spawn_powerup(self, x, y):
        if random.random() < 0.12:
            self.powerups.append(PowerUp(x, y))

    def damage_bunker(self, surf, rect, shot_rect, radius=5):
        rel_x = shot_rect.centerx - rect.left
        rel_y = shot_rect.centery - rect.top
        pygame.draw.circle(surf, (0, 0, 0, 0), (rel_x, rel_y), radius)

    def text_center(self, txt, y, color, font):
        img = font.render(txt, True, color)
        rect = img.get_rect(center=(SCREEN_W // 2, y))
        self.screen.blit(img, rect)

    def draw_stars(self):
        for star in self.stars:
            star.update()
            self.screen.set_at((int(star.x), int(star.y)), star.color)

    # --- BOOT SCREEN ---
    def boot_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                SND_DOS_OK.play()
                self.state = "MENU"
                return True

        self.screen.fill(BLACK)
        
        # Play initial boot beep on first frame
        if not self.boot_started:
            self.boot_started = True
            SND_DOS_BOOT.play()
        
        self.boot_timer += 1
        if self.boot_timer > 2:
            self.boot_timer = 0
            if self.current_line < len(self.boot_lines):
                txt = self.boot_lines[self.current_line]
                if self.char_idx < len(txt):
                    self.char_idx += 1
                    # DOS beep on each character (skip spaces for cleaner sound)
                    if txt[self.char_idx - 1] != ' ':
                        SND_DOS_BEEP.play()
                else:
                    # DOS boop when line completes
                    SND_DOS_BOOP.play()
                    self.current_line += 1
                    self.char_idx = 0
                    # Final line - play success sound
                    if self.current_line >= len(self.boot_lines):
                        SND_DOS_OK.play()

        # Auto-transition to menu after boot completes
        if self.current_line >= len(self.boot_lines):
            self.boot_complete_timer += 1
            if self.boot_complete_timer > 90:  # ~1.5 seconds at 60fps
                self.state = "MENU"
                return True

        # Render boot text
        for i in range(self.current_line + 1):
            if i < len(self.boot_lines):
                txt = self.boot_lines[i]
                if i == self.current_line:
                    txt = txt[:self.char_idx] + "_"
                img = self.small_font.render(txt, True, GREEN)
                self.screen.blit(img, (20, 30 + i * 24))
        
        # Show all lines when boot complete (no cursor)
        if self.current_line >= len(self.boot_lines):
            for i, txt in enumerate(self.boot_lines):
                img = self.small_font.render(txt, True, GREEN)
                self.screen.blit(img, (20, 30 + i * 24))
            # Blinking cursor effect
            if (self.boot_complete_timer // 15) % 2 == 0:
                cursor_img = self.small_font.render("_", True, GREEN)
                self.screen.blit(cursor_img, (20, 30 + len(self.boot_lines) * 24))

        pygame.display.flip()
        return True

    # --- MENU ---
    def menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.menu_options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    opt = self.menu_options[self.selected]
                    if opt == "START GAME":
                        self.score = 0
                        self.level = 1
                        self.reset()
                        self.state = "PLAY"
                    elif opt == "HOW TO PLAY":
                        self.state = "HOW"
                    elif opt == "CREDITS":
                        self.state = "CREDITS"
                    elif opt == "EXIT":
                        return False

        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        self.text_center("CAT'S SPACE INVADERS", 60, GREEN, self.font)
        self.text_center("60 FPS FAMICOM EDITION", 90, YELLOW, self.small_font)
        
        # Menu options
        for i, opt in enumerate(self.menu_options):
            color = YELLOW if i == self.selected else WHITE
            prefix = "> " if i == self.selected else "  "
            self.text_center(prefix + opt, 180 + i * 36, color, self.small_font)
        
        # High score
        self.text_center(f"HIGH SCORE: {self.high_score:05}", 350, CYAN, self.tiny_font)
        
        pygame.display.flip()
        return True

    # --- HOW TO PLAY ---
    def how_to_play(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.state = "MENU"

        self.screen.fill(BLACK)
        self.draw_stars()
        
        self.text_center("HOW TO PLAY", 40, CYAN, self.font)
        
        instructions = [
            ("LEFT / RIGHT  or  A / D", "MOVE SHIP"),
            ("SPACE  or  Z", "FIRE"),
            ("P", "PAUSE"),
            ("ESC", "RETURN TO MENU"),
            ("", ""),
            ("RED POWERUP", "RAPID LASER"),
            ("PURPLE POWERUP", "EXTRA LIFE"),
        ]
        
        y = 100
        for key, desc in instructions:
            if key:
                self.text_center(f"{key}  -  {desc}", y, WHITE, self.small_font)
            y += 28
        
        self.text_center("PRESS ANY KEY", 340, YELLOW, self.small_font)
        pygame.display.flip()
        return True

    # --- CREDITS ---
    def credits(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.state = "MENU"

        self.screen.fill(BLACK)
        self.draw_stars()
        
        self.text_center("CREDITS", 60, CYAN, self.font)
        self.text_center("TEAM CAT 'N CO", 120, GREEN, self.font)
        self.text_center("CatSDK [C] 2.X", 160, WHITE, self.small_font)
        self.text_center("60 FPS Famicom Engine", 200, YELLOW, self.small_font)
        self.text_center("Native 600x400 Resolution", 240, GREY, self.tiny_font)
        self.text_center("PRESS ANY KEY", 340, YELLOW, self.small_font)
        
        pygame.display.flip()
        return True

    # --- MAIN GAME ---
    def play(self):
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    return True
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_r and self.game_over:
                    if self.score > self.high_score:
                        self.high_score = self.score
                    self.score = 0
                    self.level = 1
                    self.reset()

        self.screen.fill(BLACK)
        self.draw_stars()

        if self.paused:
            self.draw_game()
            self.text_center("PAUSED", SCREEN_H // 2, WHITE, self.font)
            pygame.display.flip()
            return True

        if not self.game_over:
            self.frame_count += 1
            
            # Check wave clear
            if len(self.invaders) == 0:
                self.level += 1
                self.reset_invaders()
                self.player_shot = None
                self.enemy_shots = []

            # --- Player Movement (Frame-perfect) ---
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_x += PLAYER_SPEED
            
            # Clamp player position
            self.player_x = max(10, min(self.player_x, SCREEN_W - self.player_rect.width - 10))
            self.player_rect.x = int(self.player_x)

            # --- Player Shooting ---
            if self.shot_cooldown > 0:
                self.shot_cooldown -= 1
            
            if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.player_shot is None and self.shot_cooldown == 0:
                self.player_shot = Shot(self.player_rect.centerx, self.player_rect.top, self.shot_speed, GREEN)
                self.shot_cooldown = 10 if self.shot_speed == PLAYER_SHOT_SPEED else 5
                SND_SHOOT.play()

            # --- Invader Movement (Frame-based timing) ---
            move_interval = max(3, int(len(self.invaders) * 0.6))
            self.inv_move_timer += 1
            
            if self.inv_move_timer >= move_interval:
                self.inv_move_timer = 0
                hit_edge = False
                
                for inv in self.invaders:
                    inv.rect.x += INVADER_STEP * self.inv_dir
                    inv.anim_frame = 1 - inv.anim_frame
                    if inv.rect.right > SCREEN_W - 20 or inv.rect.left < 20:
                        hit_edge = True
                
                SND_STEPS[self.inv_step_idx].play()
                self.inv_step_idx = (self.inv_step_idx + 1) % 4
                
                if hit_edge:
                    self.inv_dir *= -1
                    for inv in self.invaders:
                        inv.rect.y += INVADER_DROP
                        if inv.rect.bottom >= self.player_rect.top:
                            self.game_over = True

            # --- UFO Logic ---
            self.ufo_timer += 1
            if not self.ufo and self.ufo_timer > 800:
                self.ufo = Invader(-40, 30, [UFO_DATA], RED, 100, -1)
                SND_UFO.play(-1)
            
            if self.ufo:
                self.ufo.rect.x += UFO_SPEED
                if self.ufo.rect.left > SCREEN_W:
                    self.ufo = None
                    self.ufo_timer = 0
                    SND_UFO.stop()

            # --- Powerups ---
            self.powerups = [p for p in self.powerups if p.update()]
            for p in self.powerups[:]:
                if p.rect.colliderect(self.player_rect):
                    if p.type == 0:  # Laser
                        self.shot_speed = PLAYER_SHOT_SPEED * 1.5
                        self.messages.append(Message("LASER!", self.player_rect.centerx, self.player_rect.top - 20, RED, self.small_font))
                    else:  # 1UP
                        self.lives += 1
                        self.messages.append(Message("1UP!", self.player_rect.centerx, self.player_rect.top - 20, PURPLE, self.small_font))
                    SND_POWER.play()
                    self.powerups.remove(p)

            # --- Messages ---
            self.messages = [m for m in self.messages if m.update()]

            # --- Player Shot Collision ---
            if self.player_shot:
                self.player_shot.update()
                
                # Bunker collision
                for b_surf, b_rect in self.bunkers:
                    if self.player_shot.rect.colliderect(b_rect):
                        self.damage_bunker(b_surf, b_rect, self.player_shot.rect)
                        self.create_explosion(self.player_shot.rect.centerx, self.player_shot.rect.centery, GREEN, 5)
                        self.player_shot = None
                        break
                
                if self.player_shot:
                    if self.player_shot.rect.bottom < 0:
                        self.player_shot = None
                    else:
                        # Enemy collision
                        for inv in self.invaders[:]:
                            if self.player_shot.rect.colliderect(inv.rect):
                                self.create_explosion(inv.rect.centerx, inv.rect.centery, inv.color, 15)
                                self.spawn_powerup(inv.rect.centerx, inv.rect.centery)
                                self.invaders.remove(inv)
                                self.score += inv.points
                                self.player_shot = None
                                SND_HIT.play()
                                break
                        
                        # UFO collision
                        if self.player_shot and self.ufo and self.player_shot.rect.colliderect(self.ufo.rect):
                            self.create_explosion(self.ufo.rect.centerx, self.ufo.rect.centery, RED, 25)
                            bonus = random.choice([50, 100, 150, 300])
                            self.score += bonus
                            self.messages.append(Message(str(bonus), self.ufo.rect.centerx, self.ufo.rect.centery, YELLOW, self.small_font))
                            self.ufo = None
                            self.ufo_timer = 0
                            self.player_shot = None
                            SND_UFO.stop()
                            SND_HIT.play()

            # --- Enemy Shooting ---
            shoot_chance = 0.012 + (self.level * 0.003)
            if self.invaders and random.random() < shoot_chance and len(self.enemy_shots) < 4:
                shooter = random.choice(self.invaders)
                self.enemy_shots.append(Shot(shooter.rect.centerx, shooter.rect.bottom, ENEMY_SHOT_SPEED, WHITE))

            # --- Enemy Shot Collision ---
            for s in self.enemy_shots[:]:
                s.update()
                
                # Bunker collision
                hit_bunker = False
                for b_surf, b_rect in self.bunkers:
                    if s.rect.colliderect(b_rect):
                        self.damage_bunker(b_surf, b_rect, s.rect)
                        self.create_explosion(s.rect.centerx, s.rect.centery, WHITE, 4)
                        self.enemy_shots.remove(s)
                        hit_bunker = True
                        break
                
                if hit_bunker:
                    continue
                
                if s.rect.top > SCREEN_H:
                    self.enemy_shots.remove(s)
                elif s.rect.colliderect(self.player_rect):
                    self.enemy_shots.remove(s)
                    self.create_explosion(self.player_rect.centerx, self.player_rect.centery, GREEN, 30)
                    self.lives -= 1
                    SND_DIE.play()
                    if self.lives <= 0:
                        self.game_over = True
                        if self.score > self.high_score:
                            self.high_score = self.score

            # --- Particles ---
            self.particles = [p for p in self.particles if p.update()]

        # --- Render ---
        self.draw_game()
        
        # HUD
        score_text = f"SCORE {self.score:05}"
        self.screen.blit(self.small_font.render(score_text, True, WHITE), (10, 8))
        
        level_text = f"WAVE {self.level}"
        self.screen.blit(self.small_font.render(level_text, True, CYAN), (SCREEN_W // 2 - 30, 8))
        
        lives_text = f"LIVES {self.lives}"
        self.screen.blit(self.small_font.render(lives_text, True, GREEN), (SCREEN_W - 90, 8))
        
        # FPS display (debug)
        fps_text = f"{int(self.clock.get_fps())} FPS"
        self.screen.blit(self.tiny_font.render(fps_text, True, GREY), (SCREEN_W - 60, SCREEN_H - 18))

        if self.game_over:
            self.text_center("GAME OVER", SCREEN_H // 2 - 20, RED, self.font)
            self.text_center(f"FINAL SCORE: {self.score}", SCREEN_H // 2 + 20, WHITE, self.small_font)
            self.text_center("PRESS R TO RESTART", SCREEN_H // 2 + 50, YELLOW, self.small_font)

        pygame.display.flip()
        return True

    def draw_game(self):
        # Player
        self.screen.blit(self.player_surf, self.player_rect)
        
        # Invaders
        for inv in self.invaders:
            inv.draw(self.screen)
        
        # UFO
        if self.ufo:
            self.ufo.draw(self.screen)
        
        # Bunkers
        for b_surf, b_rect in self.bunkers:
            self.screen.blit(b_surf, b_rect)
        
        # Player shot
        if self.player_shot:
            pygame.draw.rect(self.screen, GREEN, self.player_shot.rect)
        
        # Enemy shots
        for s in self.enemy_shots:
            pygame.draw.rect(self.screen, WHITE, s.rect)
        
        # Particles
        for p in self.particles:
            p.draw(self.screen)
        
        # Powerups
        for p in self.powerups:
            p.draw(self.screen)
        
        # Messages
        for m in self.messages:
            m.draw(self.screen)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            if self.state == "BOOT":
                running = self.boot_screen()
            elif self.state == "MENU":
                running = self.menu()
            elif self.state == "HOW":
                running = self.how_to_play()
            elif self.state == "CREDITS":
                running = self.credits()
            elif self.state == "PLAY":
                running = self.play()
        
        pygame.quit()

if __name__ == "__main__":
    game = ArcadeInvaders()
    game.run()

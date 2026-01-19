import pygame
import sys
import math
import random
import array
import struct

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# --- Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Ultra Mario 2D Bros. (1-1 to 8-4)"

# Colors
SKY_BLUE = (92, 148, 252)
UNDERGROUND_BLACK = (0, 0, 0)
CASTLE_BLACK = (32, 0, 0)
WATER_BLUE = (32, 56, 236)  # New Underwater Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 0, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
BRICK_COLOR = (179, 58, 58)
PIPE_GREEN = (34, 177, 76)
LAVA_RED = (207, 16, 32)
FLAG_POLE_GREY = (169, 169, 169)
FLAG_GREEN = (50, 205, 50)

# Physics
GRAVITY = 0.8
WATER_GRAVITY = 0.3  # Lower gravity for water levels
FRICTION = 0.85
ACCELERATION = 0.6
JUMP_FORCE = -17
WATER_JUMP_FORCE = -12
MAX_SPEED = 6

# Tile/Grid Size
TILE_SIZE = 40
MAP_HEIGHT = 15  # 600px / 40px

# --- Audio Synthesis (Files = Off) ---
class Synthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.sounds = {}
        self.music_tracks = {}
        self.current_music = None

    def make_wave_buffer(self, freq, duration, wave_type='square', volume=0.5):
        """Generates a raw audio buffer for a specific frequency and duration."""
        n_samples = int(self.sample_rate * duration)
        buf = array.array('h')  # signed short (16-bit)
        
        period = self.sample_rate / freq if freq > 0 else 0
        
        for i in range(n_samples):
            # Envelope (Fade out at end)
            env = 1.0
            if i > n_samples - 1000:
                env = (n_samples - i) / 1000.0
            
            val = 0
            if freq == 0:
                val = 0
            elif wave_type == 'square':
                val = 32767 if (i % period) < (period / 2) else -32768
            elif wave_type == 'triangle':
                phase = (i % period) / period
                if phase < 0.5:
                    val = -32768 + (phase * 4 * 32767)
                else:
                    val = 32767 - ((phase - 0.5) * 4 * 32767)
            elif wave_type == 'noise':
                val = random.randint(-32768, 32767)

            buf.append(int(val * volume * env))
            buf.append(int(val * volume * env)) # Stereo duplication

        return buf

    def generate_sound(self, name, freq, duration, type='square', vol=0.3):
        buf = self.make_wave_buffer(freq, duration, type, vol)
        self.sounds[name] = pygame.mixer.Sound(buffer=buf)

    def generate_jump_sound(self):
        # Slide pitch up for jump
        n_samples = int(self.sample_rate * 0.3)
        buf = array.array('h')
        for i in range(n_samples):
            progress = i / n_samples
            freq = 150 + (progress * 300) # 150Hz to 450Hz
            period = self.sample_rate / freq
            val = 32767 if (i % period) < (period / 2) else -32768
            buf.append(int(val * 0.2))
            buf.append(int(val * 0.2))
        self.sounds['jump'] = pygame.mixer.Sound(buffer=buf)

    def generate_music(self, name, sequence_data, tempo=0.15, loop=True):
        """
        sequence_data: List of (note_freq, duration_in_beats)
        """
        full_buffer = array.array('h')
        
        for freq, beats in sequence_data:
            duration = beats * tempo
            if freq == 0:
                # Silence
                n_samples = int(self.sample_rate * duration)
                full_buffer.extend(array.array('h', [0] * (n_samples * 2)))
            else:
                # Note
                # Shorten slightly for staccato effect unless it's a long note
                staccato = 0.9 if beats < 2 else 0.98
                note_dur = duration * staccato
                gap_dur = duration * (1 - staccato)
                
                wave_type = 'square'
                # Use triangle for lower freqs (bass)
                if freq < 200: 
                    wave_type = 'triangle'

                wave_chunk = self.make_wave_buffer(freq, note_dur, wave_type, 0.15)
                full_buffer.extend(wave_chunk)
                
                gap_samples = int(self.sample_rate * gap_dur)
                full_buffer.extend(array.array('h', [0] * (gap_samples * 2)))
        
        self.music_tracks[name] = pygame.mixer.Sound(buffer=full_buffer)

    def init_audio(self):
        # SFX
        self.generate_jump_sound()
        self.generate_sound('stomp', 100, 0.1, 'noise', 0.3)
        self.generate_sound('coin', 900, 0.1, 'square', 0.2)
        
        # --- MUSIC COMPOSITION ---
        # Frequencies (Approximate)
        G2, A2, B2 = 98, 110, 123
        C3, D3, E3, F3, G3, A3, B3 = 130, 146, 164, 174, 196, 220, 246
        C4, D4, E4, F4, G4, A4, B4 = 261, 293, 329, 349, 392, 440, 493
        C5, E5, G5 = 523, 659, 783
        
        # 1. Overworld Theme
        overworld_notes = [
            (E4, 1), (E4, 1), (0, 1), (E4, 1), (0, 1), (C4, 1), (E4, 2),
            (G4, 2), (0, 2), (G3, 2), (0, 2),
            (C4, 2), (0, 1), (G3, 2), (0, 1), (E3, 2),
            (0, 1), (A3, 1), (B3, 1), (233, 1), (A3, 1), (G3, 2) # 233=Bb3
        ]
        self.generate_music('overworld', overworld_notes, tempo=0.13)

        # 2. Underground "Duh Duh Duh" (Bass heavy)
        underground_notes = [
            (C3, 1), (C3, 1), (A2, 1), (A2, 1), (233, 1), (233, 1) # Bass line
        ]
        self.generate_music('underground', underground_notes * 4, tempo=0.18)

        # 3. Castle (Fast, ominous)
        castle_notes = [
            (110, 0.5), (123, 0.5), (110, 0.5), (0, 0.5),
            (110, 0.5), (123, 0.5), (110, 0.5), (0, 0.5),
            (165, 2)
        ]
        self.generate_music('castle', castle_notes * 4, tempo=0.10)

        # 4. Underwater (Waltz-ish 3/4 feel simulated in 4/4)
        underwater_notes = [
            (D4, 2), (E4, 2), (F3+20, 2), # F# approx
            (G4, 2), (A4, 2), (B4, 2), 
            (B4, 1), (A4, 1), (G4, 1), (F3+20, 1), (E4, 1), (D4, 1)
        ]
        self.generate_music('underwater', underwater_notes * 2, tempo=0.20)

        # 5. Level Clear (Jingle)
        level_clear_notes = [
            (G3, 0.5), (C4, 0.5), (E4, 0.5), (G4, 0.5), (C5, 0.5), (E5, 0.5),
            (G5, 2)
        ]
        self.generate_music('level_clear', level_clear_notes, tempo=0.10)

        # 6. Game Over
        game_over_notes = [
            (C5, 1), (G4, 1), (E4, 2),
            (A4, 1), (F4, 1), (D4, 2),
            (C4, 3)
        ]
        self.generate_music('game_over', game_over_notes, tempo=0.25)
        
        # 7. Victory (Ending)
        victory_notes = [
            (C4, 1), (D4, 1), (E4, 1), (F4, 1), (G4, 2), (G4, 2),
            (A4, 1), (B4, 1), (C5, 4)
        ]
        self.generate_music('victory', victory_notes, tempo=0.20)

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, track_name, loops=-1):
        if self.current_music:
            self.current_music.stop()
        
        if track_name in self.music_tracks:
            self.current_music = self.music_tracks[track_name]
            self.current_music.play(loops=loops)

    def stop_music(self):
        if self.current_music:
            self.current_music.stop()

# Initialize Audio
AUDIO = Synthesizer()
AUDIO.init_audio()


# --- Asset Generation ---
def create_textures():
    textures = {}

    # Mario (Red square with details)
    mario = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    mario.fill(RED)
    pygame.draw.rect(mario, (0, 0, 255), (10, 20, 20, 20))  # Overalls
    pygame.draw.circle(mario, (255, 200, 150), (20, 10), 8)  # Face
    textures['mario'] = mario

    # Ground
    ground = pygame.Surface((TILE_SIZE, TILE_SIZE))
    ground.fill(BROWN)
    pygame.draw.rect(ground, GREEN, (0, 0, TILE_SIZE, 8))
    textures['ground'] = ground

    # Castle Ground (Grey/Stone)
    castle_ground = pygame.Surface((TILE_SIZE, TILE_SIZE))
    castle_ground.fill((100, 100, 100))
    pygame.draw.rect(castle_ground, (120, 120, 120), (0, 0, TILE_SIZE, TILE_SIZE), 2)
    textures['castle_ground'] = castle_ground
    
    # Underwater Ground (Sand color)
    water_ground = pygame.Surface((TILE_SIZE, TILE_SIZE))
    water_ground.fill((200, 200, 100)) # Sand
    pygame.draw.rect(water_ground, (0, 100, 200), (0, 0, TILE_SIZE, 4)) # Water line
    textures['water_ground'] = water_ground

    # Brick
    brick = pygame.Surface((TILE_SIZE, TILE_SIZE))
    brick.fill(BRICK_COLOR)
    pygame.draw.rect(brick, BLACK, (0, 0, TILE_SIZE, TILE_SIZE), 2)
    pygame.draw.line(brick, BLACK, (0, TILE_SIZE // 2), (TILE_SIZE, TILE_SIZE // 2), 2)
    pygame.draw.line(brick, BLACK, (TILE_SIZE // 2, 0), (TILE_SIZE // 2, TILE_SIZE // 2), 2)
    textures['brick'] = brick
    
    # Blue Brick (Underground)
    blue_brick = brick.copy()
    blue_brick.fill((0, 50, 150), special_flags=pygame.BLEND_MULT)
    textures['blue_brick'] = blue_brick

    # Block (Question Box)
    qblock = pygame.Surface((TILE_SIZE, TILE_SIZE))
    qblock.fill(GOLD)
    pygame.draw.rect(qblock, BROWN, (0, 0, TILE_SIZE, TILE_SIZE), 4)
    font = pygame.font.SysFont('arial', 24, bold=True)
    text = font.render("?", True, BROWN)
    qblock.blit(text, (12, 5))
    textures['qblock'] = qblock
    textures['empty_block'] = brick

    # Pipe
    pipe = pygame.Surface((TILE_SIZE, TILE_SIZE))
    pipe.fill(PIPE_GREEN)
    pygame.draw.rect(pipe, (0, 100, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
    textures['pipe'] = pipe

    # Goomba
    goomba = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(goomba, BROWN, (TILE_SIZE // 2, TILE_SIZE // 2 + 5), TILE_SIZE // 2 - 2)
    pygame.draw.rect(goomba, BLACK, (10, 30, 8, 8))  # Foot 1
    pygame.draw.rect(goomba, BLACK, (22, 30, 8, 8))  # Foot 2
    textures['goomba'] = goomba

    # Lava (fixed wave effect)
    lava = pygame.Surface((TILE_SIZE, TILE_SIZE))
    lava.fill(LAVA_RED)
    for i in range(0, TILE_SIZE, 4):
        y_off = int(math.sin(i * 0.5) * 3) + 8
        pygame.draw.circle(lava, (255, 100, 0), (i, y_off), 3)
    textures['lava'] = lava

    # Flag Pole
    flag_pole = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(flag_pole, FLAG_POLE_GREY, (TILE_SIZE // 2 - 2, 0, 4, TILE_SIZE))
    textures['flag_pole'] = flag_pole

    # Flag Top
    flag_top = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(flag_top, FLAG_POLE_GREY, (TILE_SIZE // 2 - 2, 0, 4, TILE_SIZE))
    pygame.draw.polygon(flag_top, FLAG_GREEN, [(TILE_SIZE // 2 + 2, 2), (TILE_SIZE, 10), (TILE_SIZE // 2 + 2, 18)])
    textures['flag_top'] = flag_top

    return textures


TEXTURES = create_textures()
FONT = pygame.font.SysFont('arial', 20)
BIG_FONT = pygame.font.SysFont('arial', 48, bold=True)


# --- Procedural Level Generator ---

def generate_level_data(world, stage):
    # Determine Level Type
    is_castle = (stage == 4)
    is_underground = (world == 1 and stage == 2) or (world == 4 and stage == 2)
    is_water = (world == 2 and stage == 2) or (world == 7 and stage == 2)

    # 15 rows tall
    rows = ["" for _ in range(MAP_HEIGHT)]

    # Base Length grows with world
    length = 100 + (world * 10)

    # Tile Types
    if is_castle:
        FLOOR = 'C'
        ROOF = 'B'
        AIR = ' '
    elif is_water:
        FLOOR = 'W' # Water ground
        ROOF = ' '
        AIR = ' '
    elif is_underground:
        FLOOR = 'U' # Underground brick
        ROOF = 'U'
        AIR = ' '
    else:
        FLOOR = 'G'
        ROOF = ' '
        AIR = ' '

    # --- Generation Helper ---
    def add_slice(slice_str_list):
        for i in range(MAP_HEIGHT):
            rows[i] += slice_str_list[i]

    # 1. Start Zone (Safe)
    for col_idx in range(5):
        col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
        col[MAP_HEIGHT - 1] = FLOOR
        col[MAP_HEIGHT - 2] = FLOOR
        if col_idx == 2:
            col[MAP_HEIGHT - 4] = '@'  # Player Start
        add_slice(col)

    # 2. Main Level Body
    current_x = 5
    while current_x < length:
        # Determine segment type
        segment_type = random.choice(['flat', 'flat', 'pits', 'pipe', 'stairs', 'enemies'])

        # Adjust difficulty
        if is_castle:
            segment_type = random.choice(['flat', 'lava_pit', 'flat', 'enemies'])
        elif is_water:
             segment_type = random.choice(['flat', 'flat', 'enemies']) # No pits in water usually, or physics handles them

        segment_len = random.randint(3, 8)

        if segment_type == 'flat':
            for _ in range(segment_len):
                col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR

                # Random scenery
                if random.random() < 0.3:
                    col[MAP_HEIGHT - 5] = '?' if random.random() < 0.5 else 'B'
                add_slice(col)

        elif segment_type == 'enemies':
            for _ in range(segment_len):
                col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR
                if random.random() < (0.1 + (world * 0.05)):  # More enemies in later worlds
                    col[MAP_HEIGHT - 3] = 'E'
                add_slice(col)

        elif segment_type == 'pits':
            if is_water:
                # In water, pits are just deeper areas
                for _ in range(segment_len):
                    col = [AIR for r in range(MAP_HEIGHT)] # Open water
                    add_slice(col)
            else:
                # Gap
                gap_size = random.randint(2, 3 + (world // 4))  # Wider gaps later
                for _ in range(gap_size):
                    col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                    # No floor
                    add_slice(col)
                # Landing
                for _ in range(2):
                    col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                    col[MAP_HEIGHT - 1] = FLOOR
                    col[MAP_HEIGHT - 2] = FLOOR
                    add_slice(col)

        elif segment_type == 'lava_pit':
            gap_size = random.randint(3, 5)
            for _ in range(gap_size):
                col = [ROOF if r == 0 and is_castle else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = 'L'  # Lava
                add_slice(col)
            # Landing
            for _ in range(3):
                col = [ROOF if r == 0 and is_castle else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR
                add_slice(col)

        elif segment_type == 'pipe':
            # Pipe needs 2 width
            height = random.randint(2, 4)
            for w in range(2):
                col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR
                for h in range(height):
                    col[MAP_HEIGHT - 3 - h] = 'P'
                add_slice(col)
            # Buffer
            for _ in range(2):
                col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR
                add_slice(col)

        elif segment_type == 'stairs':
            stair_height = random.randint(3, 6)
            # Up
            for h in range(stair_height):
                col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR
                for brick_h in range(h + 1):
                    col[MAP_HEIGHT - 3 - brick_h] = 'B'  # Stair blocks
                add_slice(col)
            # Down
            for h in range(stair_height - 1, -1, -1):
                col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
                col[MAP_HEIGHT - 1] = FLOOR
                col[MAP_HEIGHT - 2] = FLOOR
                for brick_h in range(h + 1):
                    col[MAP_HEIGHT - 3 - brick_h] = 'B'
                add_slice(col)

        current_x += segment_len

    # 3. End Zone
    for _ in range(5):
        col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
        col[MAP_HEIGHT - 1] = FLOOR
        col[MAP_HEIGHT - 2] = FLOOR
        add_slice(col)

    # Flagpole / Axe
    flag_col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
    flag_col[MAP_HEIGHT - 1] = FLOOR
    flag_col[MAP_HEIGHT - 2] = FLOOR

    if is_castle:
        # Axe placeholder (flag for now)
        flag_col[MAP_HEIGHT - 4] = 'F'
    else:
        # Pole
        for i in range(3, 13):
            flag_col[MAP_HEIGHT - i] = 'f'  # pole part
        flag_col[MAP_HEIGHT - 12] = 'F'  # top

    add_slice(flag_col)

    # Castle at end visual
    for _ in range(8):
        col = [ROOF if r == 0 and (is_castle or is_underground) else AIR for r in range(MAP_HEIGHT)]
        col[MAP_HEIGHT - 1] = FLOOR
        col[MAP_HEIGHT - 2] = FLOOR
        # Draw a little castle wall
        if not is_castle and not is_underground:
            for h in range(4):
                col[MAP_HEIGHT - 3 - h] = 'B'
        add_slice(col)

    return rows


# --- Classes ---

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        x = min(0, x)
        x = max(-(self.width - SCREEN_WIDTH), x)
        self.camera = pygame.Rect(x, 0, self.width, self.height)


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_name):
        super().__init__()
        self.image = TEXTURES[texture_name]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block(Entity):
    def __init__(self, x, y, tile_type):
        texture = 'brick'
        if tile_type == 'G':
            texture = 'ground'
        elif tile_type == 'C':
            texture = 'castle_ground'
        elif tile_type == 'W':
            texture = 'water_ground'
        elif tile_type == 'U':
            texture = 'blue_brick'
        elif tile_type == 'B':
            texture = 'brick'
        elif tile_type == '?':
            texture = 'qblock'
        elif tile_type == 'P':
            texture = 'pipe'
        elif tile_type == 'L':
            texture = 'lava'
        elif tile_type == 'f':
            texture = 'flag_pole'
        elif tile_type == 'F':
            texture = 'flag_top'

        super().__init__(x, y, texture)
        self.type = tile_type


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'goomba')
        self.vel_x = -2
        self.vel_y = 0
        self.on_ground = False
        self.dead = False
        self.dead_timer = 0

    def update(self, blocks):
        if self.dead:
            self.dead_timer += 1
            if self.dead_timer > 30:
                self.kill()
            return

        self.vel_y += GRAVITY

        self.rect.x += self.vel_x
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if block.type in ('L', 'F', 'f'):
                continue  # Ignore non-solids for walking
            if self.vel_x > 0:
                self.rect.right = block.rect.left
                self.vel_x = -2
            elif self.vel_x < 0:
                self.rect.left = block.rect.right
                self.vel_x = 2

        self.rect.y += self.vel_y
        hits = pygame.sprite.spritecollide(self, blocks, False)
        self.on_ground = False
        for block in hits:
            if block.type in ('L', 'F', 'f'):
                continue
            if self.vel_y > 0:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = block.rect.bottom
                self.vel_y = 0

        if self.rect.y > SCREEN_HEIGHT + 100:
            self.kill()

    def squash(self):
        AUDIO.play_sfx('stomp')
        self.dead = True
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE // 2))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom += TILE_SIZE // 2


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = TEXTURES['mario']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3
        self.is_dead = False
        self.level_complete = False
        self.in_water = False

    def update(self, keys, blocks, enemies):
        if self.is_dead or self.level_complete:
            if self.is_dead:
                self.rect.y += 5
            return

        # Input
        if keys[pygame.K_LEFT]:
            self.vel_x -= ACCELERATION
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vel_x += ACCELERATION
            self.facing_right = True
        else:
            self.vel_x *= FRICTION

        if abs(self.vel_x) > MAX_SPEED:
            self.vel_x = MAX_SPEED if self.vel_x > 0 else -MAX_SPEED
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0

        # Jump
        jump_force = WATER_JUMP_FORCE if self.in_water else JUMP_FORCE
        gravity = WATER_GRAVITY if self.in_water else GRAVITY

        if keys[pygame.K_SPACE]:
            if self.in_water:
                self.vel_y = jump_force # Swim capability
            elif self.on_ground:
                self.vel_y = jump_force
                self.on_ground = False
                AUDIO.play_sfx('jump')

        self.vel_y += gravity

        # X Collision
        self.rect.x += int(self.vel_x)
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if block.type == 'F':  # Flag Top
                self.level_complete = True
                return
            if block.type == 'f':  # Flag Pole
                self.level_complete = True
                return
            if block.type == 'L':  # Lava
                self.die()
                return

            if self.vel_x > 0:
                self.rect.right = block.rect.left
                self.vel_x = 0
            elif self.vel_x < 0:
                self.rect.left = block.rect.right
                self.vel_x = 0

        # Y Collision
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if block.type == 'F' or block.type == 'f':
                self.level_complete = True
                return
            if block.type == 'L':
                self.die()
                return

            if self.vel_y > 0:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = block.rect.bottom
                self.vel_y = 0

        # Enemy Collision
        enemy_hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hits:
            if enemy.dead:
                continue

            if self.vel_y > 0 and self.rect.bottom < enemy.rect.centery + 10:
                enemy.squash()
                self.vel_y = -8
                self.score += 100
            else:
                self.die()

        if self.rect.y > SCREEN_HEIGHT:
            self.die()

    def die(self):
        if not self.is_dead:
            AUDIO.stop_music()
            # We don't have a dead music track so just silence
            self.is_dead = True
            self.lives -= 1
            self.vel_y = -10


class Level:
    def __init__(self, world, stage):
        layout_data = generate_level_data(world, stage)

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.width = len(layout_data[0]) * TILE_SIZE
        self.height = len(layout_data) * TILE_SIZE
        self.player_spawn = (100, 100)
        self.background_color = SKY_BLUE
        self.is_water = False
        
        # Determine Music and Background
        self.music_track = 'overworld'
        
        if stage == 4:
            self.background_color = CASTLE_BLACK
            self.music_track = 'castle'
        elif (world == 1 and stage == 2) or (world == 4 and stage == 2):
            self.background_color = UNDERGROUND_BLACK
            self.music_track = 'underground'
        elif (world == 2 and stage == 2) or (world == 7 and stage == 2):
            self.background_color = WATER_BLUE
            self.music_track = 'underwater'
            self.is_water = True

        row_count = 0
        for row in layout_data:
            col_count = 0
            for tile in row:
                x = col_count * TILE_SIZE
                y = row_count * TILE_SIZE

                if tile in ['G', 'C', 'B', '?', 'P', 'L', 'F', 'f', 'W', 'U']:
                    b = Block(x, y, tile)
                    self.blocks.add(b)
                elif tile == 'E':
                    e = Enemy(x, y)
                    self.enemies.add(e)
                elif tile == '@':
                    self.player_spawn = (x, y)

                col_count += 1
            row_count += 1


# --- Game Flow ---

def draw_text(screen, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))


def show_how_to_play(screen):
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        draw_text(screen, "HOW TO PLAY", BIG_FONT, GOLD, SCREEN_WIDTH // 2, 80, center=True)
        
        instructions = [
            "",
            "LEFT / RIGHT - Move Mario",
            "SPACE - Jump (Swim in Water)",
            "ESC - Return to Menu",
            "",
            "Jump on enemies to defeat them!",
            "Avoid pits and lava!",
            "Reach the flag to clear each level!",
            "",
            "Complete all 32 levels (1-1 to 8-4)",
            "to save the kingdom!",
            "",
            "",
            "Press any key to return..."
        ]
        
        for i, line in enumerate(instructions):
            draw_text(screen, line, FONT, WHITE, SCREEN_WIDTH // 2, 150 + i * 28, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Quit"
            if event.type == pygame.KEYDOWN:
                return "Menu"
        
        pygame.display.flip()
        clock.tick(FPS)


def show_credits(screen):
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        draw_text(screen, "CREDITS", BIG_FONT, GOLD, SCREEN_WIDTH // 2, 80, center=True)
        
        credits = [
            "",
            "ULTRA MARIO 2D BROS",
            "",
            "Original Game:",
            "Nintendo (C) 1985",
            "",
            "This Fan Recreation:",
            "Samsoft (C) 1999-2026",
            "",
            "Programming & Design:",
            "Team Flames",
            "",
            "Engine: Pygame-CE",
            "",
            "",
            "Press any key to return..."
        ]
        
        for i, line in enumerate(credits):
            color = GOLD if "Samsoft" in line or "Nintendo" in line or "Team Flames" in line else WHITE
            draw_text(screen, line, FONT, color, SCREEN_WIDTH // 2, 140 + i * 26, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Quit"
            if event.type == pygame.KEYDOWN:
                return "Menu"
        
        pygame.display.flip()
        clock.tick(FPS)


def main_menu(screen):
    running = True
    clock = pygame.time.Clock()
    selected = 0
    options = ["Play Game", "How to Play", "Credits", "Exit Program"]
    
    AUDIO.play_music('overworld')

    while running:
        screen.fill(SKY_BLUE)

        # Title
        draw_text(screen, "ULTRA MARIO 2D BROS", BIG_FONT, WHITE, SCREEN_WIDTH // 2, 120, center=True)
        draw_text(screen, "Adventure 1-1 to 8-4", FONT, WHITE, SCREEN_WIDTH // 2, 170, center=True)
        
        # Copyright notices
        draw_text(screen, "(C) 1985 Nintendo", FONT, WHITE, SCREEN_WIDTH // 2, 220, center=True)
        draw_text(screen, "(C) Samsoft 1999-2026", FONT, GOLD, SCREEN_WIDTH // 2, 250, center=True)

        # Menu options
        for i, option in enumerate(options):
            color = GOLD if i == selected else WHITE
            draw_text(screen, option, FONT, color, SCREEN_WIDTH // 2, 340 + i * 40, center=True)
        
        # Selection indicator
        draw_text(screen, ">", FONT, GOLD, SCREEN_WIDTH // 2 - 100, 340 + selected * 40, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    AUDIO.play_sfx('stomp') # Menu blip
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    AUDIO.play_sfx('stomp') # Menu blip
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    AUDIO.play_sfx('coin') # Confirm sound
                    if selected == 0:
                        AUDIO.stop_music()
                        return "Start"
                    elif selected == 1:
                        result = show_how_to_play(screen)
                        if result == "Quit":
                            return "Quit"
                    elif selected == 2:
                        result = show_credits(screen)
                        if result == "Quit":
                            return "Quit"
                    elif selected == 3:
                        return "Quit"

        pygame.display.flip()
        clock.tick(FPS)


def run_level(screen, world, stage, lives_carryover):
    level = Level(world, stage)
    player = Player(*level.player_spawn)
    player.lives = lives_carryover
    player.in_water = level.is_water # Set water state

    camera = Camera(level.width, level.height)
    clock = pygame.time.Clock()

    # Interstitial Screen
    AUDIO.stop_music()
    screen.fill(BLACK)
    draw_text(screen, f"WORLD {world}-{stage}", BIG_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
    draw_text(screen, f"Lives: {player.lives}", FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)
    pygame.display.flip()
    pygame.time.delay(2000)
    
    # Start Music
    AUDIO.play_music(level.music_track)

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Quit", player.lives
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    AUDIO.stop_music()
                    return "Menu", player.lives

        player.update(keys, level.blocks, level.enemies)
        level.enemies.update(level.blocks)
        camera.update(player)

        # Win Condition
        if player.level_complete:
            AUDIO.play_music('level_clear', loops=0) # Play once
            # Play a short animation or delay
            for _ in range(180):  # 3 seconds wait to hear music
                screen.fill(level.background_color)
                for s in level.blocks:
                    screen.blit(s.image, camera.apply(s))
                screen.blit(player.image, camera.apply(player))
                draw_text(screen, "LEVEL CLEARED!", BIG_FONT, GOLD, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
                pygame.display.flip()
                clock.tick(FPS)
            return "Next", player.lives

        # Death Condition
        if player.rect.y > SCREEN_HEIGHT + 200:
            if player.lives > 0:
                # Reset position
                AUDIO.play_music(level.music_track) # Restart music
                player.rect.topleft = level.player_spawn
                player.vel_x, player.vel_y = 0, 0
                player.is_dead = False
                player.image = TEXTURES['mario']
                camera.camera.x = 0
            else:
                AUDIO.stop_music()
                return "GameOver", 0

        # Draw
        screen.fill(level.background_color)

        for sprite in level.blocks:
            screen.blit(sprite.image, camera.apply(sprite))

        for sprite in level.enemies:
            screen.blit(sprite.image, camera.apply(sprite))

        screen.blit(player.image, camera.apply(player))

        # HUD
        draw_text(screen, f"MARIO", FONT, WHITE, 50, 20)
        draw_text(screen, f"{player.score:06}", FONT, WHITE, 50, 45)

        draw_text(screen, f"WORLD", FONT, WHITE, 400, 20)
        draw_text(screen, f"{world}-{stage}", FONT, WHITE, 400, 45)

        draw_text(screen, f"LIVES", FONT, WHITE, 700, 20)
        draw_text(screen, f"{player.lives}", FONT, WHITE, 700, 45)

        pygame.display.flip()
        clock.tick(FPS)

    return "Menu", player.lives


def game_over_screen(screen):
    AUDIO.play_music('game_over', loops=0)
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", BIG_FONT, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
    pygame.display.flip()
    pygame.time.delay(4000)


def victory_screen(screen):
    AUDIO.play_music('victory', loops=0)
    screen.fill(SKY_BLUE)
    draw_text(screen, "CONGRATULATIONS!", BIG_FONT, GOLD, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
    draw_text(screen, "You saved the kingdom!", FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)
    pygame.display.flip()
    pygame.time.delay(6000)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    while True:
        choice = main_menu(screen)

        if choice == "Quit":
            break
        elif choice == "Start":
            # Game Loop 1-1 to 8-4
            world = 1
            stage = 1
            lives = 3
            game_running = True

            while game_running:
                result, lives = run_level(screen, world, stage, lives)

                if result == "Next":
                    stage += 1
                    if stage > 4:
                        stage = 1
                        world += 1

                    if world > 8:
                        victory_screen(screen)
                        game_running = False  # Back to menu

                elif result == "GameOver":
                    game_over_screen(screen)
                    game_running = False
                elif result == "Menu" or result == "Quit":
                    game_running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

import pygame
import random
import sys
import math

# ────────────────────────────────────────────────
# CONFIGURATION & INITIALIZATION
# ────────────────────────────────────────────────
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# Classic Arcade Resolution Scaled
BASE_WIDTH, BASE_HEIGHT = 224, 256
SCALE = 3
SCREEN_WIDTH, SCREEN_HEIGHT = BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ULTRA! SPACE INVADERS")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

COLORS = {
    'BLACK':  (0, 0, 0),
    'WHITE':  (255, 255, 255),
    'GREEN':  (50, 255, 50),
    'RED':    (255, 50, 50),
    'CYAN':   (50, 255, 255),
    'YELLOW': (255, 255, 50),
    'GRAY':   (100, 100, 100)
}

# ────────────────────────────────────────────────
# PROCEDURAL SFX ENGINE
# ────────────────────────────────────────────────
def make_sfx(wf, f, d, decay=True):
    sr = 44100
    n = int(sr * d)
    buf = bytearray()
    for i in range(n):
        vol = 0.5 * (1.0 - (i/n)) if decay else 0.4
        t = i / (sr/f)
        if wf == 'square': v = 1.0 if (t % 1.0) < 0.5 else -1.0
        elif wf == 'noise': v = random.uniform(-1, 1)
        elif wf == 'saw': v = 2.0 * (t % 1.0) - 1.0
        else: v = math.sin(2 * math.pi * t)
        s = int(v * vol * 32767)
        buf += s.to_bytes(2, 'little', signed=True)
    return pygame.mixer.Sound(buf)

sfx_shoot = make_sfx('square', 800, 0.1)
sfx_kill  = make_sfx('noise', 100, 0.15)
sfx_die   = make_sfx('noise', 50, 0.8)
sfx_beat  = [make_sfx('square', f, 0.05) for f in [160, 150, 140, 130]]
sfx_confirm = make_sfx('saw', 600, 0.1)
sfx_select  = make_sfx('square', 440, 0.05)

# ────────────────────────────────────────────────
# PIXEL ENGINE & FONT
# ────────────────────────────────────────────────
def get_pixel_sprite(pattern_lines, color):
    rows = len(pattern_lines)
    cols = len(pattern_lines[0])
    surf = pygame.Surface((cols * SCALE, rows * SCALE))
    surf.set_colorkey((0,0,0))
    for r, line in enumerate(pattern_lines):
        for c, char in enumerate(line):
            if char == '1':
                pygame.draw.rect(surf, color, (c * SCALE, r * SCALE, SCALE, SCALE))
    return surf

def render_text(text, x, y, color, size=1, center=False):
    font_map = {
        'A':["01110","10001","11111","10001","10001"], 'B':["11110","10001","11110","10001","11110"],
        'C':["01110","10001","10000","10001","01110"], 'D':["11110","10001","10001","10001","11110"],
        'E':["11111","10000","11110","10000","11111"], 'F':["11111","10000","11110","10000","10000"],
        'G':["01110","10000","10111","10001","01110"], 'H':["10001","10001","11111","10001","10001"],
        'I':["010","010","010","010","010"],           'J':["00001","00001","00001","10001","01110"],
        'K':["10001","10010","11100","10010","10001"], 'L':["10000","10000","10000","10000","11111"],
        'M':["10001","11011","10101","10001","10001"], 'N':["10001","11001","10101","10011","10001"],
        'O':["01110","10001","10001","10001","01110"], 'P':["11110","10001","11110","10000","10000"],
        'Q':["01110","10001","10101","10010","00101"], 'R':["11110","10001","11110","10001","10001"],
        'S':["01111","10000","01110","00001","11110"], 'T':["11111","00100","00100","00100","00100"],
        'U':["10001","10001","10001","10001","01110"], 'V':["10001","10001","10001","01010","00100"],
        'W':["10001","10001","10101","11011","10001"], 'X':["10001","01010","00100","01010","10001"],
        'Y':["10001","01010","00100","00100","00100"], 'Z':["11111","00010","00100","01000","11111"],
        '0':["01110","10011","10101","11001","01110"], '1':["00100","01100","00100","00100","01110"],
        '2':["01110","10001","00010","01000","11111"], '3':["01110","10001","00110","10001","01110"],
        '4':["00110","01010","10010","11111","00010"], '5':["11111","10000","11110","00001","11110"],
        '6':["01110","10000","11110","10001","01110"], '7':["11111","00001","00010","00100","00100"],
        '8':["01110","10001","01110","10001","01110"], '9':["01110","10001","01111","00001","01110"],
        '!':["010","010","010","000","010"],           '.':["000","000","000","000","010"],
        '[':["011","010","010","010","011"],           ']':["110","010","010","010","110"],
        ' ':[ "000" ]
    }
    
    total_w = 0
    for char in text.upper():
        if char in font_map: total_w += (len(font_map[char][0]) + 1) * SCALE * size
        else: total_w += 4 * SCALE * size
    
    if center: x = (SCREEN_WIDTH - total_w) // 2
    
    curr_x = x
    for char in text.upper():
        if char in font_map:
            p = font_map[char]
            for r, line in enumerate(p):
                for c, pix in enumerate(line):
                    if pix == '1':
                        pygame.draw.rect(screen, color, (curr_x + c*SCALE*size, y + r*SCALE*size, SCALE*size, SCALE*size))
            curr_x += (len(p[0]) + 1) * SCALE * size
        else: curr_x += 4 * SCALE * size
    return pygame.Rect(x, y, total_w, 5 * SCALE * size)

def get_row_color(y):
    y_base = y / SCALE
    if y_base < 60: return COLORS['WHITE']
    if y_base < 100: return COLORS['RED']
    if y_base < 160: return COLORS['CYAN']
    return COLORS['GREEN']

# ────────────────────────────────────────────────
# CLASSES
# ────────────────────────────────────────────────

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((1*SCALE, 4*SCALE))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
    def update(self):
        self.rect.y += self.speed
        if not screen.get_rect().contains(self.rect): self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, color):
        super().__init__()
        p = ["00100100","01011010","10100101","00000000","10100101","01011010","00100100"]
        self.image = get_pixel_sprite(p, color)
        self.rect = self.image.get_rect(center=center)
        self.timer = 12
    def update(self):
        self.timer -= 1
        if self.timer <= 0: self.kill()

class Invader(pygame.sprite.Sprite):
    def __init__(self, r, c, level):
        super().__init__()
        self.type = 'C' if r == 0 else 'B' if r < 3 else 'A'
        self.score = 30 if r == 0 else 20 if r < 3 else 10
        self.images = self.gen_frames()
        self.frame = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(25*SCALE + c*16*SCALE, 50*SCALE + r*12*SCALE + level*8*SCALE))

    def gen_frames(self):
        color = COLORS['WHITE']
        if self.type == 'A':
            p1, p2 = ["00011000","00111100","01111110","11011011","11111111","00100100","01011010","10100101"], ["00011000","00111100","01111110","11011011","11111111","00100100","01000010","00100100"]
        elif self.type == 'B':
            p1, p2 = ["00100000100","00011111000","00111111100","01101110110","11111111111","10111111101","10100000101","00011011000"], ["00100000100","10011111001","10111111101","11101110111","11111111111","00111111100","00100000100","00010001000"]
        else:
            p1, p2 = ["000011110000","011111111110","111111111111","111001100111","111111111111","000110011000","001101101100","110000000011"], ["000011110000","011111111110","111111111111","111001100111","111111111111","001110011100","011001100110","000000000000"]
        return [get_pixel_sprite(p1, color), get_pixel_sprite(p2, color)]

    def update_frame(self, dx):
        self.rect.x += dx
        self.frame = 1 - self.frame
        self.image = self.images[self.frame]

class Bunker(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((22*SCALE, 16*SCALE))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, COLORS['GREEN'], (0, 0, 22*SCALE, 16*SCALE))
        pygame.draw.rect(self.image, (0,0,0), (6*SCALE, 10*SCALE, 10*SCALE, 6*SCALE))
        self.rect = self.image.get_rect(topleft=(x, SCREEN_HEIGHT - 65*SCALE))
    
    def hit(self, pos):
        lx, ly = pos[0] - self.rect.x, pos[1] - self.rect.y
        pygame.draw.circle(self.image, (0,0,0), (lx, ly), 4*SCALE)

# ────────────────────────────────────────────────
# ENGINE CORE
# ────────────────────────────────────────────────

player_img = get_pixel_sprite(["00000100000","00001110000","01111111110","11111111111","11111111111"], COLORS['GREEN'])
player_rect = player_img.get_rect(midbottom=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 15*SCALE))

invaders, p_lasers, e_lasers, bunkers, explosions = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

def start_level(lv):
    invaders.empty(); p_lasers.empty(); e_lasers.empty()
    for r in range(5):
        for c in range(11):
            invaders.add(Invader(r, c, lv))
    if lv == 0:
        bunkers.empty()
        for i in range(4): bunkers.add(Bunker(25*SCALE + i*50*SCALE))

score, hi_score, level, state = 0, 0, 0, 'MENU'
lives, respawn_timer = 3, 0
move_dir, move_timer, beat_idx = 1, 0, 0
menu_idx = 0
MENU_OPTIONS = ["PLAY", "HOW TO PLAY", "CREDITS", "EXIT"]

# ────────────────────────────────────────────────
# MAIN LOOP
# ────────────────────────────────────────────────

while True:
    screen.fill((0,0,0))
    mx, my = pygame.mouse.get_pos()
    m_clicked = False
    action_trigger = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: m_clicked = True
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_z, pygame.K_SPACE, pygame.K_RETURN]: action_trigger = True
            if state == 'MENU':
                if event.key == pygame.K_UP: menu_idx = (menu_idx - 1) % len(MENU_OPTIONS); sfx_select.play()
                if event.key == pygame.K_DOWN: menu_idx = (menu_idx + 1) % len(MENU_OPTIONS); sfx_select.play()

    # --- STATE: MENU ---
    if state == 'MENU':
        render_text("ULTRA!", 0, 30*SCALE, COLORS['RED'], 1, center=True)
        render_text("SPACE INVADERS", 0, 45*SCALE, COLORS['WHITE'], 2, center=True)
        
        for i, opt in enumerate(MENU_OPTIONS):
            col = COLORS['YELLOW'] if i == menu_idx else COLORS['GRAY']
            rect = render_text(opt, 0, 100*SCALE + (i*20*SCALE), col, 1, center=True)
            if rect.collidepoint(mx, my):
                if menu_idx != i: sfx_select.play(); menu_idx = i
                if m_clicked: action_trigger = True
        
        if action_trigger:
            sfx_confirm.play()
            if MENU_OPTIONS[menu_idx] == "PLAY": state, score, level, lives = 'PLAY', 0, 0, 3; start_level(level)
            elif MENU_OPTIONS[menu_idx] == "HOW TO PLAY": state = 'HELP'
            elif MENU_OPTIONS[menu_idx] == "CREDITS": state = 'CREDITS'
            else: pygame.quit(); sys.exit()

    # --- STATE: HELP ---
    elif state == 'HELP':
        render_text("HOW TO PLAY", 0, 30*SCALE, COLORS['CYAN'], 2, center=True)
        h_lines = ["MOUSE OR ARROWS TO MOVE", "CLICK OR Z TO FIRE", "", "DESTROY THE ALIEN SWARM", "DON'T LET THEM LAND", "YOU HAVE 3 LIVES"]
        for i, line in enumerate(h_lines): render_text(line, 0, 80*SCALE + (i*15*SCALE), COLORS['WHITE'], 1, center=True)
        render_text("CLICK OR Z TO RETURN", 0, 200*SCALE, COLORS['RED'], 1, center=True)
        if action_trigger or m_clicked: sfx_confirm.play(); state = 'MENU'

    # --- STATE: CREDITS ---
    elif state == 'CREDITS':
        render_text("CREDITS", 0, 30*SCALE, COLORS['GREEN'], 2, center=True)
        c_lines = ["[C] SAMSOFT 1999-2026", "[C] ATARI 1978", "", "CODE AND SOUNDS", "BY AI ENGINE", "RENDERED IN PYGAME"]
        for i, line in enumerate(c_lines): render_text(line, 0, 80*SCALE + (i*15*SCALE), COLORS['WHITE'], 1, center=True)
        render_text("CLICK OR Z TO RETURN", 0, 200*SCALE, COLORS['RED'], 1, center=True)
        if action_trigger or m_clicked: sfx_confirm.play(); state = 'MENU'

    # --- STATE: PLAY ---
    elif state == 'PLAY':
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player_rect.x -= 4*SCALE
        elif keys[pygame.K_RIGHT]: player_rect.x += 4*SCALE
        if abs(pygame.mouse.get_rel()[0]) > 0: player_rect.centerx = max(15*SCALE, min(SCREEN_WIDTH-15*SCALE, mx))
        player_rect.clamp_ip(screen.get_rect())

        # Shooting
        if (action_trigger or m_clicked) and len(p_lasers) == 0 and respawn_timer == 0:
            sfx_shoot.play(); p_lasers.add(Laser(player_rect.centerx, player_rect.top, -6*SCALE, COLORS['WHITE']))

        # Respawn
        if respawn_timer > 0: respawn_timer -= 1

        # Invaders Logic
        count = len(invaders)
        if count == 0: level += 1; start_level(level)
        
        move_timer += 1
        if move_timer >= max(2, count - (level*3)):
            move_timer, turn = 0, False
            for inv in invaders:
                if (move_dir > 0 and inv.rect.right > SCREEN_WIDTH-10) or (move_dir < 0 and inv.rect.left < 10): turn = True; break
            if turn:
                move_dir *= -1
                for inv in invaders: 
                    inv.rect.y += 8*SCALE
                    if inv.rect.bottom >= player_rect.top: lives = 0; sfx_die.play(); state = 'GAMEOVER'
            else:
                for inv in invaders: inv.update_frame(4*SCALE*move_dir)
            sfx_beat[beat_idx].play(); beat_idx = (beat_idx + 1) % 4

        # Enemy Fire
        if random.random() < 0.015 + (level*0.01) and count > 0:
            luck = random.choice(invaders.sprites())
            e_lasers.add(Laser(luck.rect.centerx, luck.rect.bottom, 4*SCALE, COLORS['RED']))

        # Collisions
        for l in p_lasers:
            hit = pygame.sprite.spritecollideany(l, invaders)
            if hit: score += hit.score; sfx_kill.play(); explosions.add(Explosion(hit.rect.center, COLORS['WHITE'])); hit.kill(); l.kill()
            b_hit = pygame.sprite.spritecollideany(l, bunkers)
            if b_hit: b_hit.hit(l.rect.center); l.kill()
            
        for l in e_lasers:
            if respawn_timer == 0 and player_rect.colliderect(l.rect):
                sfx_die.play(); explosions.add(Explosion(player_rect.center, COLORS['GREEN'])); l.kill()
                lives -= 1
                if lives > 0: respawn_timer = 90
                else: state = 'GAMEOVER'; hi_score = max(score, hi_score)
            b_hit = pygame.sprite.spritecollideany(l, bunkers)
            if b_hit: b_hit.hit(l.rect.center); l.kill()

        # Update & Draw
        p_lasers.update(); e_lasers.update(); explosions.update()
        if respawn_timer == 0 or (respawn_timer % 10 < 5): screen.blit(player_img, player_rect)
        for inv in invaders:
            tmp = inv.image.copy()
            tmp.fill(get_row_color(inv.rect.y), special_flags=pygame.BLEND_MULT)
            screen.blit(tmp, inv.rect)
        bunkers.draw(screen); p_lasers.draw(screen); e_lasers.draw(screen); explosions.draw(screen)
        
        render_text(f"SCORE {score:04}  HI-SCORE {hi_score:04}", 10*SCALE, 10*SCALE, COLORS['WHITE'])
        pygame.draw.line(screen, COLORS['GREEN'], (0, SCREEN_HEIGHT-2), (SCREEN_WIDTH, SCREEN_HEIGHT-2), 2)
        render_text(f"{lives}", 10*SCALE, SCREEN_HEIGHT-12*SCALE, COLORS['WHITE'])
        for i in range(max(0, lives-1)): screen.blit(player_img, (22*SCALE + i*14*SCALE, SCREEN_HEIGHT-12*SCALE))

    # --- STATE: GAMEOVER ---
    elif state == 'GAMEOVER':
        render_text("GAME OVER", 0, 100*SCALE, COLORS['RED'], 2, center=True)
        render_text("CLICK OR Z TO MENU", 0, 130*SCALE, COLORS['WHITE'], 1, center=True)
        explosions.update(); explosions.draw(screen)
        if action_trigger or m_clicked: state = 'MENU'

    # CRT Overlay
    for y in range(0, SCREEN_HEIGHT, 3): pygame.draw.line(screen, (0,0,0,60), (0,y), (SCREEN_WIDTH,y))
    pygame.display.flip()
    clock.tick(60)

#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║               ULTRA MARIO 2D BROS                             ║
║         A Complete SMB-Style Platformer                       ║
║              Worlds 1-1 through 8-4                           ║
║          (C) 2025 Samsoft / Team Flames                       ║
╚═══════════════════════════════════════════════════════════════╝

Add your own music files to 'music/' folder:
- overworld.mp3, underground.mp3, castle.mp3, underwater.mp3
"""

import pygame
import math
import random
import os

pygame.init()
pygame.mixer.init()

# NES Style Constants
SCALE = 3
NES_W, NES_H = 256, 240
SW, SH = NES_W * SCALE, NES_H * SCALE
FPS = 60

# NES Color Palette
class C:
    BLACK = (0, 0, 0)
    WHITE = (252, 252, 252)
    SKY = (92, 148, 252)
    BRICK = (200, 76, 12)
    BRICK_DARK = (136, 20, 0)
    GROUND = (228, 92, 16)
    QBLOCK = (252, 152, 56)
    PIPE = (0, 168, 0)
    PIPE_HI = (128, 208, 16)
    MARIO_RED = (200, 76, 12)
    SKIN = (252, 152, 56)
    GOOMBA = (136, 20, 0)
    KOOPA = (0, 168, 0)
    COIN = (252, 188, 60)

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("ULTRA MARIO 2D BROS")
clock = pygame.time.Clock()
nes = pygame.Surface((NES_W, NES_H))

font = pygame.font.Font(None, 8 * SCALE)
font_lg = pygame.font.Font(None, 12 * SCALE)

# Sound system
def play_music(name):
    for ext in ['.mp3', '.ogg', '.wav']:
        path = f"music/{name}{ext}"
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
                return
            except: pass

# Drawing functions
def draw_brick(s, x, y):
    pygame.draw.rect(s, C.BRICK, (x, y, 16, 16))
    pygame.draw.rect(s, C.BRICK_DARK, (x, y, 16, 16), 1)
    pygame.draw.line(s, C.BRICK_DARK, (x, y+8), (x+16, y+8))
    pygame.draw.line(s, C.BRICK_DARK, (x+8, y), (x+8, y+8))
    pygame.draw.line(s, C.BRICK_DARK, (x+4, y+8), (x+4, y+16))
    pygame.draw.line(s, C.BRICK_DARK, (x+12, y+8), (x+12, y+16))

def draw_qblock(s, x, y):
    pygame.draw.rect(s, C.QBLOCK, (x, y, 16, 16))
    pygame.draw.rect(s, C.BRICK_DARK, (x, y, 16, 16), 1)
    pygame.draw.rect(s, C.BRICK_DARK, (x+6, y+3, 4, 7))
    pygame.draw.rect(s, C.BRICK_DARK, (x+6, y+12, 4, 2))

def draw_ground(s, x, y):
    pygame.draw.rect(s, C.GROUND, (x, y, 16, 16))
    pygame.draw.rect(s, C.BRICK_DARK, (x, y, 16, 16), 1)

def draw_pipe(s, x, y, h=2):
    pygame.draw.rect(s, C.PIPE, (x-2, y, 36, 16))
    pygame.draw.rect(s, C.PIPE_HI, (x, y+2, 4, 12))
    for i in range(1, h):
        pygame.draw.rect(s, C.PIPE, (x, y+i*16, 32, 16))
        pygame.draw.rect(s, C.PIPE_HI, (x+2, y+i*16, 4, 16))

def draw_cloud(s, x, y, w=1):
    for i in range(w):
        pygame.draw.ellipse(s, C.WHITE, (x+i*16, y, 20, 16))
    pygame.draw.ellipse(s, C.WHITE, (x+4, y-8, 16*w-8, 16))

def draw_bush(s, x, y, w=1):
    for i in range(w):
        pygame.draw.ellipse(s, C.PIPE, (x+i*16, y, 20, 16))

def draw_hill(s, x, y):
    pygame.draw.polygon(s, C.PIPE, [(x, y+48), (x+40, y), (x+80, y+48)])

def draw_coin(s, x, y, f=0):
    ws = [8, 6, 2, 6]
    w = ws[f % 4]
    pygame.draw.ellipse(s, C.COIN, (x+4-w//2, y, w, 14))

def draw_flag(s, x, y):
    pygame.draw.rect(s, C.PIPE, (x+6, y, 4, 160))
    pygame.draw.circle(s, C.PIPE, (x+8, y), 4)
    pygame.draw.polygon(s, C.MARIO_RED, [(x+10, y+8), (x+26, y+16), (x+10, y+24)])

# Player class
class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 12, 16
        self.big = False
        self.grounded = False
        self.facing = 1
        self.dead = False
        self.invuln = 0
        self.coins = 0
        self.score = 0
        self.lives = 3
        self.anim = 0
    
    def update(self, keys, blocks):
        if self.dead:
            self.vy += 0.3
            self.y += self.vy
            return
        
        acc = 0.15 if self.grounded else 0.1
        mx = 2.5 if keys[pygame.K_x] else 1.5
        
        if keys[pygame.K_LEFT]:
            self.vx = max(-mx, self.vx - acc)
            self.facing = -1
        elif keys[pygame.K_RIGHT]:
            self.vx = min(mx, self.vx + acc)
            self.facing = 1
        else:
            if abs(self.vx) < 0.1: self.vx = 0
            elif self.vx > 0: self.vx -= 0.1
            else: self.vx += 0.1
        
        if keys[pygame.K_z] and self.grounded:
            self.vy = -4.5 if not self.big else -5.0
            self.grounded = False
        
        gv = 0.2 if keys[pygame.K_z] and self.vy < 0 else 0.35
        self.vy = min(self.vy + gv, 6.0)
        
        self.x += self.vx
        self.y += self.vy
        
        self.h = 24 if self.big else 16
        self.grounded = False
        
        for bx, by, bt in blocks:
            br = pygame.Rect(bx, by, 16, 16)
            pr = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
            if not pr.colliderect(br): continue
            
            if self.vy > 0 and pr.bottom > br.top and pr.bottom - self.vy <= br.top + 4:
                self.y = br.top - self.h
                self.vy = 0
                self.grounded = True
            elif self.vy < 0 and pr.top < br.bottom:
                self.y = br.bottom
                self.vy = 0
            
            pr = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
            if pr.colliderect(br):
                if self.vx > 0: self.x = br.left - self.w
                elif self.vx < 0: self.x = br.right
                self.vx = 0
        
        if self.x < 0: self.x = 0
        if self.y > NES_H + 32: self.die()
        if self.invuln > 0: self.invuln -= 1
        self.anim = (self.anim + 1) % 16 if abs(self.vx) > 0.5 else 0
    
    def die(self):
        if not self.dead:
            self.dead = True
            self.vy = -5
            self.lives -= 1
    
    def draw(self, s, cx):
        if self.invuln > 0 and self.invuln % 4 < 2: return
        x, y = int(self.x - cx), int(self.y)
        
        if self.big:
            pygame.draw.rect(s, C.MARIO_RED, (x+2, y, 8, 8))
            pygame.draw.rect(s, C.SKIN, (x+2, y+4, 8, 6))
            pygame.draw.rect(s, C.MARIO_RED, (x, y+10, 12, 8))
            pygame.draw.rect(s, (0, 0, 200), (x+1, y+18, 4, 6))
            pygame.draw.rect(s, (0, 0, 200), (x+7, y+18, 4, 6))
        else:
            pygame.draw.rect(s, C.MARIO_RED, (x+2, y, 8, 6))
            pygame.draw.rect(s, C.SKIN, (x+3, y+3, 6, 4))
            pygame.draw.rect(s, C.MARIO_RED, (x+1, y+7, 10, 5))
            pygame.draw.rect(s, (0, 0, 200), (x+1, y+12, 4, 4))
            pygame.draw.rect(s, (0, 0, 200), (x+7, y+12, 4, 4))

# Enemy classes
class Goomba:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = -0.5, 0
        self.alive = True
        self.squished = 0
        self.anim = 0
    
    def update(self, blocks):
        if self.squished > 0:
            self.squished -= 1
            if self.squished <= 0: self.alive = False
            return
        if not self.alive: return
        
        self.vy = min(self.vy + 0.3, 4)
        self.x += self.vx
        self.y += self.vy
        self.anim = (self.anim + 1) % 16
        
        for bx, by, bt in blocks:
            br = pygame.Rect(bx, by, 16, 16)
            gr = pygame.Rect(int(self.x), int(self.y), 16, 16)
            if not gr.colliderect(br): continue
            if self.vy > 0: self.y = br.top - 16; self.vy = 0
            if self.vx > 0 and gr.right > br.left and gr.left < br.left: self.vx = -0.5
            elif self.vx < 0 and gr.left < br.right and gr.right > br.right: self.vx = 0.5
        
        if self.y > NES_H + 32: self.alive = False
    
    def draw(self, s, cx):
        if not self.alive: return
        x, y = int(self.x - cx), int(self.y)
        if self.squished > 0:
            pygame.draw.rect(s, C.GOOMBA, (x, y+12, 16, 4))
            return
        pygame.draw.ellipse(s, C.GOOMBA, (x, y, 16, 12))
        off = 2 if self.anim < 8 else 0
        pygame.draw.rect(s, C.GOOMBA, (x+1+off, y+10, 5, 6))
        pygame.draw.rect(s, C.GOOMBA, (x+10-off, y+10, 5, 6))
        pygame.draw.rect(s, C.WHITE, (x+3, y+4, 3, 3))
        pygame.draw.rect(s, C.WHITE, (x+10, y+4, 3, 3))

class Koopa:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = -0.5, 0
        self.alive = True
        self.shell = False
    
    def update(self, blocks):
        if not self.alive or (self.shell and self.vx == 0): return
        self.vy = min(self.vy + 0.3, 4)
        self.x += self.vx
        self.y += self.vy
        
        h = 16 if self.shell else 24
        for bx, by, bt in blocks:
            br = pygame.Rect(bx, by, 16, 16)
            kr = pygame.Rect(int(self.x), int(self.y), 16, h)
            if not kr.colliderect(br): continue
            if self.vy > 0: self.y = br.top - h; self.vy = 0
            if self.vx > 0: self.vx = -abs(self.vx)
            elif self.vx < 0: self.vx = abs(self.vx)
    
    def draw(self, s, cx):
        if not self.alive: return
        x, y = int(self.x - cx), int(self.y)
        if self.shell:
            pygame.draw.ellipse(s, C.KOOPA, (x, y, 16, 14))
            return
        pygame.draw.ellipse(s, C.KOOPA, (x, y+8, 16, 14))
        pygame.draw.ellipse(s, C.PIPE_HI, (x+2, y, 12, 12))
        pygame.draw.rect(s, C.QBLOCK, (x+2, y+20, 5, 4))
        pygame.draw.rect(s, C.QBLOCK, (x+9, y+20, 5, 4))

# Level generation
def gen_level(world, level):
    blocks, enemies, pipes, coins = [], [], [], []
    width = 3200 + world * 200
    goal_x = width - 200
    
    # Ground with gaps
    x = 0
    while x < width:
        if x > 400 and x < width - 300 and random.random() < 0.05 + world * 0.01:
            x += random.choice([32, 48, 64])
            continue
        for yo in range(2):
            blocks.append((x, NES_H - 32 - yo * 16, 'ground'))
        x += 16
    
    # Platforms
    for i in range(width // 200):
        bx = 200 + i * 200 + random.randint(-50, 50)
        by = random.choice([NES_H - 80, NES_H - 96, NES_H - 112])
        for j in range(random.randint(2, 5)):
            bt = random.choice(['brick', 'brick', 'brick', 'qblock'])
            blocks.append((bx + j * 16, by, bt))
    
    # Pipes
    px = 300
    while px < width - 400:
        h = random.randint(2, 4)
        pipes.append((px, NES_H - 32 - h * 16, h))
        px += random.randint(200, 400)
    
    # Enemies
    for i in range(5 + world * 3 + level * 2):
        ex = 300 + random.randint(0, width - 600)
        ey = NES_H - 48
        if random.random() < 0.6:
            enemies.append(Goomba(ex, ey))
        else:
            enemies.append(Koopa(ex, ey - 8))
    
    # Coins
    for i in range(10 + world * 2):
        cx = random.randint(200, width - 200)
        cy = random.choice([NES_H - 64, NES_H - 96, NES_H - 128])
        coins.append([cx, cy, True])
    
    return {'blocks': blocks, 'enemies': enemies, 'pipes': pipes, 'coins': coins, 
            'width': width, 'goal_x': goal_x, 'underground': level == 2, 'castle': level == 4}

# Main menu
def draw_menu(sel, top, ca):
    nes.fill(C.SKY)
    
    # Ground
    for x in range(0, NES_W, 16):
        draw_ground(nes, x, NES_H - 32)
        draw_ground(nes, x, NES_H - 16)
    
    # Background
    draw_cloud(nes, 30, 40, 2)
    draw_cloud(nes, 150, 60, 1)
    draw_bush(nes, 20, NES_H - 48, 2)
    draw_bush(nes, 180, NES_H - 48, 1)
    draw_hill(nes, 80, NES_H - 80)
    
    # Title
    ty = 45
    for i, c in enumerate("ULTRA"):
        x = 68 + i * 16
        pygame.draw.rect(nes, C.MARIO_RED, (x, ty, 14, 14))
        t = font.render(c, True, C.WHITE)
        nes.blit(t, (x + 3, ty + 2))
    
    for i, c in enumerate("MARIO"):
        x = 58 + i * 18
        pygame.draw.rect(nes, C.QBLOCK, (x, ty + 20, 16, 16))
        t = font.render(c, True, C.MARIO_RED)
        nes.blit(t, (x + 3, ty + 24))
    
    t = font.render("2D BROS.", True, C.WHITE)
    nes.blit(t, (82, ty + 42))
    
    t = font.render("@2025 SAMSOFT", True, C.WHITE)
    nes.blit(t, (68, ty + 58))
    
    # Menu
    my = 148
    draw_coin(nes, 88, my - 5, ca)
    
    # Cursor (mushroom)
    cy = my + sel * 16
    pygame.draw.ellipse(nes, C.MARIO_RED, (73, cy + 2, 10, 8))
    pygame.draw.rect(nes, C.SKIN, (75, cy + 8, 6, 6))
    
    t = font.render("1 PLAYER GAME", True, C.WHITE)
    nes.blit(t, (103, my))
    t = font.render("2 PLAYER GAME", True, C.WHITE)
    nes.blit(t, (103, my + 16))
    
    t = font.render(f"TOP- {top:06d}", True, C.WHITE)
    nes.blit(t, (78, my + 38))
    
    draw_pipe(nes, 200, NES_H - 80, 3)
    
    scaled = pygame.transform.scale(nes, (SW, SH))
    screen.blit(scaled, (0, 0))

def draw_hud(s, p, w, l, t, ca):
    pygame.draw.rect(s, C.BLACK, (0, 0, NES_W, 24))
    txt = font.render("MARIO", True, C.WHITE)
    s.blit(txt, (20, 2))
    txt = font.render(f"{p.score:06d}", True, C.WHITE)
    s.blit(txt, (20, 12))
    draw_coin(s, 90, 10, ca)
    txt = font.render(f"x{p.coins:02d}", True, C.WHITE)
    s.blit(txt, (100, 12))
    txt = font.render("WORLD", True, C.WHITE)
    s.blit(txt, (140, 2))
    txt = font.render(f" {w}-{l}", True, C.WHITE)
    s.blit(txt, (145, 12))
    txt = font.render("TIME", True, C.WHITE)
    s.blit(txt, (200, 2))
    txt = font.render(f" {int(t):03d}", True, C.WHITE)
    s.blit(txt, (200, 12))

def draw_trans(w, l, lives):
    nes.fill(C.BLACK)
    t = font_lg.render(f"WORLD {w}-{l}", True, C.WHITE)
    nes.blit(t, (NES_W//2 - t.get_width()//2, NES_H//2 - 30))
    pygame.draw.rect(nes, C.MARIO_RED, (100, NES_H//2+10, 8, 12))
    pygame.draw.rect(nes, C.SKIN, (101, NES_H//2+13, 6, 4))
    t = font.render(f"x  {lives}", True, C.WHITE)
    nes.blit(t, (115, NES_H//2 + 15))
    scaled = pygame.transform.scale(nes, (SW, SH))
    screen.blit(scaled, (0, 0))

# Main loop
def main():
    state = 0  # 0=menu, 1=trans, 2=play, 3=pause, 4=over, 5=clear
    sel, top = 0, 0
    player, world, level, data, cam_x, time_left, trans = None, 1, 1, None, 0, 400, 0
    ca, at = 0, 0
    
    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False
            elif e.type == pygame.KEYDOWN:
                if state == 0:
                    if e.key == pygame.K_UP: sel = (sel - 1) % 2
                    elif e.key == pygame.K_DOWN: sel = (sel + 1) % 2
                    elif e.key in [pygame.K_RETURN, pygame.K_z]:
                        state = 1
                        world, level = 1, 1
                        player = Player(40, NES_H - 64)
                        trans = 180
                        play_music("overworld")
                elif state == 2:
                    if e.key in [pygame.K_p, pygame.K_ESCAPE]: state = 3
                elif state == 3:
                    if e.key in [pygame.K_p, pygame.K_ESCAPE]: state = 2
                elif state in [4, 5]:
                    if e.key in [pygame.K_RETURN, pygame.K_z]:
                        state = 0
                        pygame.mixer.music.stop()
        
        keys = pygame.key.get_pressed()
        at += 1
        if at >= 8: ca = (ca + 1) % 4; at = 0
        
        if state == 0:
            draw_menu(sel, top, ca)
        
        elif state == 1:
            draw_trans(world, level, player.lives)
            trans -= 1
            if trans <= 0:
                state = 2
                data = gen_level(world, level)
                cam_x = 0
                player.x, player.y = 40, NES_H - 64
                player.dead, player.vx, player.vy = False, 0, 0
                time_left = 400
        
        elif state == 2:
            time_left -= 1/60
            if time_left <= 0: player.die()
            
            solid = [(b[0], b[1], b[2]) for b in data['blocks']]
            for px, py, ph in data['pipes']:
                for i in range(ph):
                    solid.append((px, py + i*16, 'pipe'))
                    solid.append((px+16, py + i*16, 'pipe'))
            
            player.update(keys, solid)
            
            for en in data['enemies']:
                en.update(solid)
                if not en.alive: continue
                pr = pygame.Rect(int(player.x), int(player.y), player.w, player.h)
                er = pygame.Rect(int(en.x), int(en.y), 16, 16)
                if pr.colliderect(er) and not player.dead:
                    if player.vy > 0 and player.y + player.h < en.y + 10:
                        if isinstance(en, Goomba): en.squished = 30
                        elif isinstance(en, Koopa):
                            if en.shell: en.vx = 4 if player.x < en.x else -4
                            else: en.shell = True; en.vx = 0
                        player.vy = -3
                        player.score += 100
                    elif player.invuln <= 0:
                        if player.big: player.big = False; player.invuln = 120
                        else: player.die()
            
            for c in data['coins']:
                if not c[2]: continue
                cr = pygame.Rect(c[0], c[1], 12, 14)
                pr = pygame.Rect(int(player.x), int(player.y), player.w, player.h)
                if pr.colliderect(cr):
                    c[2] = False
                    player.coins += 1
                    player.score += 200
                    if player.coins >= 100: player.coins -= 100; player.lives += 1
            
            if player.x >= data['goal_x']:
                player.score += int(time_left) * 50
                if player.score > top: top = player.score
                level += 1
                if level > 4: level = 1; world += 1
                if world > 8: state = 5
                else: state = 1; trans = 180
            
            if player.dead and player.y > NES_H + 50:
                if player.lives <= 0: state = 4
                else: state = 1; trans = 180; player.dead = False
            
            cam_x = max(cam_x, player.x - NES_W // 3)
            cam_x = min(cam_x, data['width'] - NES_W)
            cam_x = max(0, cam_x)
            
            bg = C.BLACK if data['underground'] or data['castle'] else C.SKY
            nes.fill(bg)
            
            if not data['underground'] and not data['castle']:
                for i in range(0, data['width'], 300):
                    bx = (i - int(cam_x * 0.5)) % (NES_W + 100) - 50
                    draw_cloud(nes, bx, 40, 2)
                for i in range(0, data['width'], 250):
                    bx = i - int(cam_x * 0.8)
                    if 0 < bx < NES_W: draw_bush(nes, bx, NES_H - 48, 2)
            
            for px, py, ph in data['pipes']:
                if -40 < px - cam_x < NES_W + 40:
                    draw_pipe(nes, int(px - cam_x), py, ph)
            
            for bx, by, bt in data['blocks']:
                if bx - cam_x < -16 or bx - cam_x > NES_W: continue
                x = int(bx - cam_x)
                if bt == 'ground': draw_ground(nes, x, by)
                elif bt == 'brick': draw_brick(nes, x, by)
                elif bt == 'qblock': draw_qblock(nes, x, by)
            
            for c in data['coins']:
                if c[2] and -16 < c[0] - cam_x < NES_W:
                    draw_coin(nes, int(c[0] - cam_x), c[1], ca)
            
            for en in data['enemies']: en.draw(nes, cam_x)
            player.draw(nes, cam_x)
            
            if data['goal_x'] - cam_x < NES_W:
                draw_flag(nes, int(data['goal_x'] - cam_x), NES_H - 192)
            
            draw_hud(nes, player, world, level, time_left, ca)
            scaled = pygame.transform.scale(nes, (SW, SH))
            screen.blit(scaled, (0, 0))
        
        elif state == 3:
            scaled = pygame.transform.scale(nes, (SW, SH))
            screen.blit(scaled, (0, 0))
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 128))
            screen.blit(ov, (0, 0))
            t = font_lg.render("PAUSED", True, C.WHITE)
            screen.blit(t, (SW//2 - t.get_width()//2, SH//2 - 20))
        
        elif state == 4:
            nes.fill(C.BLACK)
            t = font_lg.render("GAME OVER", True, C.WHITE)
            nes.blit(t, (NES_W//2 - t.get_width()//2, NES_H//2 - 10))
            scaled = pygame.transform.scale(nes, (SW, SH))
            screen.blit(scaled, (0, 0))
        
        elif state == 5:
            nes.fill(C.BLACK)
            t = font_lg.render("CONGRATULATIONS!", True, C.WHITE)
            nes.blit(t, (NES_W//2 - t.get_width()//2, NES_H//2 - 30))
            t = font.render("ALL WORLDS COMPLETE!", True, C.WHITE)
            nes.blit(t, (NES_W//2 - t.get_width()//2, NES_H//2 + 10))
            t = font.render(f"SCORE: {player.score}", True, C.QBLOCK)
            nes.blit(t, (NES_W//2 - t.get_width()//2, NES_H//2 + 30))
            scaled = pygame.transform.scale(nes, (SW, SH))
            screen.blit(scaled, (0, 0))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════╗")
    print("║          ULTRA MARIO 2D BROS                      ║")
    print("║        Worlds 1-1 through 8-4                     ║")
    print("║      (C) 2025 Samsoft / Team Flames               ║")
    print("╠═══════════════════════════════════════════════════╣")
    print("║  Controls:                                        ║")
    print("║    Arrow Keys - Move                              ║")
    print("║    Z - Jump    X - Run    P - Pause               ║")
    print("╠═══════════════════════════════════════════════════╣")
    print("║  Add music to 'music/' folder:                    ║")
    print("║    overworld.mp3, underground.mp3, castle.mp3     ║")
    print("╚═══════════════════════════════════════════════════╝")
    main()

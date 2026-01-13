#!/usr/bin/env python3
"""
Cat's PVZ By ChatGPT 1.0
FULL GAME — SINGLE FILE — EDUCATIONAL BUILD
Inspired by PvZ1 structure and mechanics
NO ASSETS • NO FILE I/O • PURE PYGAME SHAPES

FEATURES:
- Main Menu
- Level Intro
- Wave-based gameplay
- Sunflower / Peashooter / Wall-Nut / Cherry Bomb
- Zombie eating plants
- Conehead zombies
- Lawnmowers
- Win & Game Over screens
"""

import pygame, sys, random
from enum import Enum

pygame.init()

# ================= CONFIG =================
SCREEN_W, SCREEN_H = 900, 520
ROWS, COLS = 5, 9
CELL_W, CELL_H = 80, 90
GRID_X, GRID_Y = 140, 80
FPS = 60

# ================= COLORS =================
BG = (60, 160, 60)
GRID = (40, 120, 40)
SUN = (255, 220, 0)
PEA = (0, 200, 0)
ZOMBIE = (120, 120, 120)
CONE = (200, 120, 0)
TEXT = (255, 255, 255)
BTN = (50, 50, 50)
BTN_HOVER = (90, 90, 90)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Cat's PVZ By ChatGPT 1.0")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 18, bold=True)
big = pygame.font.SysFont("arial", 44, bold=True)

# ================= GAME STATE =================
class GameState(Enum):
    MENU = 0
    LEVEL = 1
    PLAY = 2
    WIN = 3
    GAME_OVER = 4

state = GameState.MENU
level = 1

# ================= GAME DATA =================
sun = 150
plants = {}
zombies = []
peas = []
suns = []
lawnmowers = [True]*ROWS
wave_left = 0
spawn_timer = 0
selected = None

# ================= CLASSES =================
class SunDrop:
    def __init__(self,x,y): self.x=x; self.y=y; self.life=600
    def update(self): self.life-=1
    def draw(self): pygame.draw.circle(screen,SUN,(int(self.x),int(self.y)),12)

class Plant:
    cost=0
    def __init__(self,r,c,hp):
        self.r=r; self.c=c; self.hp=hp
        self.x=GRID_X+c*CELL_W; self.y=GRID_Y+r*CELL_H
    def update(self): pass
    def draw(self): pass

class Sunflower(Plant):
    cost=50
    def __init__(self,r,c): super().__init__(r,c,100); self.t=0
    def update(self):
        self.t+=1
        if self.t>300:
            suns.append(SunDrop(self.x+40,self.y+40)); self.t=0
    def draw(self): pygame.draw.circle(screen,(255,200,0),(self.x+40,self.y+40),22)

class Peashooter(Plant):
    cost=100
    def __init__(self,r,c): super().__init__(r,c,100); self.cd=0
    def update(self):
        self.cd+=1
        if self.cd>60:
            peas.append([self.x+60,self.y+40,self.r]); self.cd=0
    def draw(self): pygame.draw.circle(screen,PEA,(self.x+40,self.y+40),20)

class WallNut(Plant):
    cost=50
    def __init__(self,r,c): super().__init__(r,c,300)
    def draw(self): pygame.draw.circle(screen,(160,100,60),(self.x+40,self.y+40),28)

class CherryBomb(Plant):
    cost=150
    def __init__(self,r,c): super().__init__(r,c,999); self.t=30
    def update(self):
        self.t-=1
        if self.t<=0:
            for z in zombies[:]:
                if abs(z.row-self.r)<=1 and abs(z.x-(self.x+40))<100:
                    zombies.remove(z)
            plants.pop((self.r,self.c))
    def draw(self): pygame.draw.circle(screen,(220,0,0),(self.x+40,self.y+40),18)

class Zombie:
    def __init__(self,row,hp=100,speed=0.3,cone=False):
        self.row=row; self.x=SCREEN_W; self.y=GRID_Y+row*CELL_H+20
        self.hp=hp; self.speed=speed; self.cone=cone; self.eat=0
    def update(self):
        gp=((self.y-GRID_Y)//CELL_H, int((self.x-GRID_X)//CELL_W))
        if gp in plants:
            self.eat+=1
            if self.eat>30:
                plants[gp].hp-=20; self.eat=0
                if plants[gp].hp<=0: plants.pop(gp)
        else: self.x-=self.speed
    def draw(self):
        pygame.draw.rect(screen,ZOMBIE,(self.x,self.y,40,60))
        if self.cone:
            pygame.draw.polygon(screen,CONE,[(self.x+20,self.y-20),(self.x,self.y),(self.x+40,self.y)])

# ================= HELPERS =================
def grid_pos(mx,my):
    if mx<GRID_X or my<GRID_Y: return None
    c=(mx-GRID_X)//CELL_W; r=(my-GRID_Y)//CELL_H
    if 0<=r<ROWS and 0<=c<COLS: return int(r),int(c)

def button(r,t):
    mx,my=pygame.mouse.get_pos(); h=r.collidepoint(mx,my)
    pygame.draw.rect(screen,BTN_HOVER if h else BTN,r)
    screen.blit(font.render(t,True,TEXT),(r.x+10,r.y+10))
    return h and pygame.mouse.get_pressed()[0]

def reset_level():
    global plants,zombies,peas,suns,lawnmowers,wave_left,spawn_timer,sun
    plants={}; zombies=[]; peas=[]; suns=[]; lawnmowers=[True]*ROWS
    wave_left=10+level*5; spawn_timer=0; sun=150

# ================= MAIN LOOP =================
running=True
menu_tick=0
zombie_peek_x=-80

while running:
    clock.tick(FPS)
    menu_tick+=1
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if state==GameState.PLAY:
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_1: selected='sun'
                if e.key==pygame.K_2: selected='pea'
                if e.key==pygame.K_3: selected='nut'
                if e.key==pygame.K_4: selected='bomb'
            if e.type==pygame.MOUSEBUTTONDOWN:
                mx,my=e.pos
                for s in suns[:]:
                    if abs(mx-s.x)<15 and abs(my-s.y)<15:
                        sun+=25; suns.remove(s)
                gp=grid_pos(mx,my)
                if gp and gp not in plants:
                    r,c=gp
                    if selected=='sun' and sun>=50: plants[gp]=Sunflower(r,c); sun-=50
                    if selected=='pea' and sun>=100: plants[gp]=Peashooter(r,c); sun-=100
                    if selected=='nut' and sun>=50: plants[gp]=WallNut(r,c); sun-=50
                    if selected=='bomb' and sun>=150: plants[gp]=CherryBomb(r,c); sun-=150

    screen.fill(BG)

    # ================= PVZ-STYLE MAIN MENU =================
    if state==GameState.MENU:
        # sky
        pygame.draw.rect(screen,(90,180,255),(0,0,SCREEN_W,140))
        # grass layers
        pygame.draw.rect(screen,(50,150,50),(0,140,SCREEN_W,200))
        pygame.draw.rect(screen,(40,120,40),(0,340,SCREEN_W,180))

        # wobble title
        wob=int(6*pygame.math.sin(menu_tick*0.05))
        screen.blit(big.render("CAT'SZ'Z PVZ 1 1.0",True,TEXT),(300,60+wob))
        screen.blit(font.render("Classic Dev Edition",True,TEXT),(360,110))

        # zombie peek animation
        zombie_peek_x=min(40,zombie_peek_x+0.6)
        pygame.draw.rect(screen,ZOMBIE,(zombie_peek_x,300,50,90))
        pygame.draw.circle(screen,(200,200,200),(zombie_peek_x+15,330),6)
        pygame.draw.circle(screen,(200,200,200),(zombie_peek_x+35,330),6)

        # menu buttons (PvZ vertical slab style)
        if button(pygame.Rect(360,200,200,44),"ADVENTURE"):
            reset_level(); state=GameState.LEVEL
        if button(pygame.Rect(360,250,200,44),"OPTIONS"):
            pass
        if button(pygame.Rect(360,300,200,44),"QUIT"):
            running=False

    # ================= LEVEL INTRO =================
    elif state==GameState.LEVEL:
        screen.fill((30,90,30))
        screen.blit(big.render(f"LEVEL {level}",True,TEXT),(350,220))
        pygame.display.flip(); pygame.time.delay(1200)
        state=GameState.PLAY

    # ================= GAMEPLAY =================
    elif state==GameState.PLAY:
        spawn_timer+=1
        if spawn_timer>120 and wave_left>0:
            zombies.append(Zombie(random.randint(0,ROWS-1),100+level*20,0.3+level*0.05,random.random()<0.3))
            wave_left-=1; spawn_timer=0

        for p in list(plants.values()): p.update()
        for z in zombies: z.update()

        for pea in peas[:]:
            pea[0]+=6
            for z in zombies:
                if z.row==pea[2] and abs(pea[0]-z.x)<20:
                    z.hp-=20; peas.remove(pea); break
        zombies=[z for z in zombies if z.hp>0]

        for z in zombies:
            if z.x<60:
                if lawnmowers[z.row]: lawnmowers[z.row]=False; zombies=[x for x in zombies if x.row!=z.row]
                else: state=GameState.GAME_OVER

        if wave_left==0 and not zombies: state=GameState.WIN

        for s in suns[:]: s.update();
        suns=[s for s in suns if s.life>0]

        for r in range(ROWS):
            for c in range(COLS): pygame.draw.rect(screen,GRID,(GRID_X+c*CELL_W,GRID_Y+r*CELL_H,CELL_W,CELL_H),1)
        for p in plants.values(): p.draw()
        for z in zombies: z.draw()
        for pea in peas: pygame.draw.circle(screen,(0,255,0),(int(pea[0]),int(pea[1])),5)
        for s in suns: s.draw()

        screen.blit(font.render(f"SUN: {sun}",True,TEXT),(10,10))
        screen.blit(font.render("1 Sun  2 Pea  3 Nut  4 Bomb",True,TEXT),(10,34))

    # ================= WIN =================
    elif state==GameState.WIN:
        screen.fill((40,120,40))
        screen.blit(big.render("LEVEL CLEAR!",True,TEXT),(300,220))
        if button(pygame.Rect(360,280,200,44),"NEXT LEVEL"):
            level+=1; reset_level(); state=GameState.LEVEL

    # ================= GAME OVER =================
    elif state==GameState.GAME_OVER:
        screen.fill((90,40,40))
        screen.blit(big.render("ZOMBIES ATE YOUR BRAINS",True,TEXT),(180,220))
        if button(pygame.Rect(360,280,200,44),"MAIN MENU"):
            level=1; zombie_peek_x=-80; state=GameState.MENU

    pygame.display.flip()

pygame.quit(); sys.exit()

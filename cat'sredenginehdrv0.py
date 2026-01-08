#!/usr/bin/env python3
"""
██████╗  ██████╗ ██╗  ██╗███████╗███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗ ████║██╔═══██╗████╗  ██║
██████╔╝██║   ██║█████╔╝ █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
██║     ╚██████╔╝██║  ██╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                        RED VERSION
            Authentic Recreation - Team Flames 2026
"""
import pygame
import random

pygame.init()

# ═══════════════════════════════════════════════════════════════════════════════
# GAME BOY DISPLAY (160x144 native, scaled 3x)
# ═══════════════════════════════════════════════════════════════════════════════
SCALE = 3
GBW, GBH = 160, 144
WIN_W, WIN_H = GBW * SCALE, GBH * SCALE
TILE = 16

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("POKEMON RED")
clock = pygame.time.Clock()
gb = pygame.Surface((GBW, GBH))

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTIC POKEMON RED PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
C = {
    'blk': (8, 24, 32),
    'drk': (48, 104, 80),
    'lit': (136, 192, 112),
    'wht': (224, 248, 208),
    'red': (208, 48, 48),
    'blu': (64, 96, 176),
    'water': (64, 144, 248),
    'path': (200, 168, 96),
    'roof': (176, 40, 40),
    'wall': (248, 248, 248),
    'wood': (112, 72, 48),
    'tree_t': (32, 128, 56),
    'tree_b': (80, 56, 32),
    'grass': (96, 184, 80),
    'dgrass': (40, 128, 48),
}

# Type colors
TCOL = {
    'NORMAL':(168,168,120),'FIRE':(240,128,48),'WATER':(104,144,240),
    'ELECTRIC':(248,208,48),'GRASS':(120,200,80),'ICE':(152,216,216),
    'FIGHTING':(192,48,40),'POISON':(160,64,160),'GROUND':(224,192,104),
    'FLYING':(168,144,240),'PSYCHIC':(248,88,136),'BUG':(168,184,32),
    'ROCK':(184,160,56),'GHOST':(112,88,152),'DRAGON':(112,56,248),
}

# ═══════════════════════════════════════════════════════════════════════════════
# TILES - Exact Pokemon Red style
# ═══════════════════════════════════════════════════════════════════════════════
# g=grass, G=tall grass, p=path, T=tree, W=water, .=floor
# H=house wall, R=red roof, B=blue roof, D=door, w=window, S=sign
# L=lab roof, M=mailbox, f=fence, F=flowers, X=blocked, E=exit

def tile(t, x, y, f):
    """Draw one 16x16 tile."""
    
    if t == 'g':  # Grass
        pygame.draw.rect(gb, C['grass'], (x, y, 16, 16))
        pygame.draw.rect(gb, C['dgrass'], (x+3, y+10, 2, 5))
        pygame.draw.rect(gb, C['dgrass'], (x+9, y+8, 2, 6))
        pygame.draw.rect(gb, C['dgrass'], (x+13, y+12, 2, 4))
        
    elif t == 'G':  # Tall grass (encounters)
        pygame.draw.rect(gb, C['dgrass'], (x, y, 16, 16))
        o = (f//10) % 2
        for i in range(4):
            gx = x + 1 + i*4
            gy = y + 3 + (o if i%2==0 else 1-o)
            pygame.draw.line(gb, C['grass'], (gx, gy+10), (gx, gy), 2)
            pygame.draw.line(gb, C['grass'], (gx+1, gy+10), (gx+3, gy+3))
            
    elif t == 'p':  # Path
        pygame.draw.rect(gb, C['path'], (x, y, 16, 16))
        pygame.draw.rect(gb, (180,150,80), (x+4, y+4, 2, 2))
        pygame.draw.rect(gb, (180,150,80), (x+11, y+9, 2, 2))
        
    elif t == 'T':  # Tree
        pygame.draw.rect(gb, C['grass'], (x, y, 16, 16))
        pygame.draw.rect(gb, C['tree_b'], (x+5, y+10, 6, 6))
        pygame.draw.ellipse(gb, C['tree_t'], (x+1, y, 14, 12))
        pygame.draw.ellipse(gb, C['dgrass'], (x+3, y+2, 10, 8))
        
    elif t == 'W':  # Water
        pygame.draw.rect(gb, C['water'], (x, y, 16, 16))
        o = (f//12) % 4
        pygame.draw.line(gb, C['wht'], (x+2+o, y+5), (x+6+o, y+5))
        pygame.draw.line(gb, C['wht'], (x+1+o, y+11), (x+5+o, y+11))
        
    elif t == 'H':  # House wall
        pygame.draw.rect(gb, C['wall'], (x, y, 16, 16))
        pygame.draw.rect(gb, C['blk'], (x, y, 16, 16), 1)
        
    elif t == 'R':  # Red roof
        pygame.draw.rect(gb, C['roof'], (x, y, 16, 16))
        pygame.draw.line(gb, (144,32,32), (x, y+7), (x+16, y+7))
        
    elif t == 'B':  # Blue roof
        pygame.draw.rect(gb, C['blu'], (x, y, 16, 16))
        pygame.draw.line(gb, (48,72,128), (x, y+7), (x+16, y+7))
        
    elif t == 'L':  # Lab roof (special)
        pygame.draw.rect(gb, C['roof'], (x, y, 16, 16))
        pygame.draw.line(gb, (144,32,32), (x, y+4), (x+16, y+4))
        pygame.draw.line(gb, (144,32,32), (x, y+11), (x+16, y+11))
        
    elif t == 'D':  # Door
        pygame.draw.rect(gb, C['wall'], (x, y, 16, 16))
        pygame.draw.rect(gb, C['wood'], (x+3, y+2, 10, 14))
        pygame.draw.rect(gb, C['blk'], (x+3, y+2, 10, 14), 1)
        pygame.draw.rect(gb, (200,160,80), (x+10, y+8, 2, 2))
        
    elif t == 'w':  # Window
        pygame.draw.rect(gb, C['wall'], (x, y, 16, 16))
        pygame.draw.rect(gb, C['blu'], (x+3, y+4, 10, 8))
        pygame.draw.rect(gb, C['blk'], (x+3, y+4, 10, 8), 1)
        pygame.draw.line(gb, C['blk'], (x+8, y+4), (x+8, y+12))
        
    elif t == 'S':  # Sign
        pygame.draw.rect(gb, C['grass'], (x, y, 16, 16))
        pygame.draw.rect(gb, (168,136,80), (x+3, y+4, 10, 7))
        pygame.draw.rect(gb, C['wood'], (x+6, y+11, 4, 5))
        pygame.draw.rect(gb, C['blk'], (x+3, y+4, 10, 7), 1)
        
    elif t == 'M':  # Mailbox/Mat
        pygame.draw.rect(gb, C['path'], (x, y, 16, 16))
        pygame.draw.rect(gb, C['wood'], (x+4, y+4, 8, 8))
        
    elif t == 'f':  # Fence
        pygame.draw.rect(gb, C['grass'], (x, y, 16, 16))
        pygame.draw.rect(gb, (176,144,88), (x, y+6, 16, 5))
        pygame.draw.rect(gb, C['wood'], (x+2, y+3, 3, 10))
        pygame.draw.rect(gb, C['wood'], (x+11, y+3, 3, 10))
        
    elif t == 'F':  # Flowers
        pygame.draw.rect(gb, C['grass'], (x, y, 16, 16))
        pygame.draw.circle(gb, C['red'], (x+4, y+6), 3)
        pygame.draw.circle(gb, (248,208,48), (x+11, y+8), 3)
        pygame.draw.circle(gb, C['red'], (x+7, y+12), 3)
        
    elif t == 'X':  # Solid black
        pygame.draw.rect(gb, C['blk'], (x, y, 16, 16))
        
    elif t in 'nsew':  # Exit tiles (look like path)
        pygame.draw.rect(gb, C['path'], (x, y, 16, 16))
        
    else:  # Default grass
        pygame.draw.rect(gb, C['grass'], (x, y, 16, 16))

# ═══════════════════════════════════════════════════════════════════════════════
# PALLET TOWN - EXACT AUTHENTIC LAYOUT (20x18)
# ═══════════════════════════════════════════════════════════════════════════════
PALLET = [
    "TTTTTTTTnnnnTTTTTTTT",  # 0  - north exit to Route 1
    "TgggggggppppggggggT",  # 1
    "TgRRRRggppppggRRRRgT",  # 2  - house roofs
    "TgRRRRggppppggRRRRgT",  # 3
    "TgHwHHggppppggHwHHgT",  # 4  - house walls with windows
    "TgHDHHggppppggHDHHgT",  # 5  - doors
    "TgSMggggppppggSMgggT",  # 6  - signs and mats
    "TgggggggppppgggggggT",  # 7
    "TgggffffppppffffgggT",  # 8  - fences
    "TgggggggppppgggggggT",  # 9
    "TgggggLLLLLLLLggggT",   # 10 - Oak's lab roof
    "TgggggLLLLLLLLggggT",   # 11
    "TgggggHwHHHHwHggggT",   # 12 - lab walls
    "TgggggHHHDDHHHggggT",   # 13 - lab door (double)
    "TgggggggMMMMgggggggT",  # 14 - welcome mat
    "TgFFggggppppggggFFgT",  # 15 - flowers
    "TgggggggppppgggggggT",  # 16
    "TTTTTTTTssssTTTTTTTT",  # 17 - south exit to Route 21
]

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTE 1 - Pallet to Viridian (16x72)
# ═══════════════════════════════════════════════════════════════════════════════
def make_route1():
    r = []
    for y in range(72):
        row = ""
        for x in range(16):
            # Borders
            if x == 0 or x == 15:
                row += "T"
            # North exit
            elif y == 0 and 6 <= x <= 9:
                row += "n"
            elif y == 0:
                row += "T"
            # South exit  
            elif y == 71 and 6 <= x <= 9:
                row += "s"
            elif y == 71:
                row += "T"
            # Path through middle
            elif 6 <= x <= 9:
                row += "p"
            # Tall grass patches
            elif (8 <= y <= 18 or 28 <= y <= 38 or 48 <= y <= 58) and (2 <= x <= 5 or 10 <= x <= 13):
                row += "G"
            # Ledges
            elif y in [20, 40, 60] and (2 <= x <= 5 or 10 <= x <= 13):
                row += "g"  # ledge visual later
            else:
                row += "g"
        r.append(row)
    return r

ROUTE1 = make_route1()

# ═══════════════════════════════════════════════════════════════════════════════
# VIRIDIAN CITY (24x24)
# ═══════════════════════════════════════════════════════════════════════════════
def make_viridian():
    v = []
    for y in range(24):
        row = ""
        for x in range(24):
            # Borders
            if y == 0:
                if 10 <= x <= 13:
                    row += "n"  # North to Route 2
                else:
                    row += "T"
            elif y == 23:
                if 10 <= x <= 13:
                    row += "s"  # South to Route 1
                else:
                    row += "T"
            elif x == 0:
                if 10 <= y <= 13:
                    row += "w"  # West to Route 22
                else:
                    row += "T"
            elif x == 23:
                row += "T"
            # Main path
            elif 10 <= x <= 13:
                row += "p"
            elif y == 12 and x > 0:
                row += "p"
            # Pokemon Center (left)
            elif 3 <= y <= 5 and 2 <= x <= 6:
                if y == 3:
                    row += "R"
                elif y == 4:
                    row += "H" if x != 4 else "w"
                else:
                    row += "H" if x != 4 else "D"
            # Mart (right)
            elif 3 <= y <= 5 and 17 <= x <= 21:
                if y == 3:
                    row += "B"
                elif y == 4:
                    row += "H" if x != 19 else "w"
                else:
                    row += "H" if x != 19 else "D"
            # Gym (blocked)
            elif 15 <= y <= 17 and 17 <= x <= 21:
                if y == 15:
                    row += "R"
                elif y == 16:
                    row += "H" if x != 19 else "w"
                else:
                    row += "H"  # Locked
            # Signs
            elif (x, y) == (5, 6):
                row += "S"
            elif (x, y) == (20, 6):
                row += "S"
            else:
                row += "g"
        v.append(row)
    return v

VIRIDIAN = make_viridian()

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTE 22 - West of Viridian (30x16)
# ═══════════════════════════════════════════════════════════════════════════════
def make_route22():
    r = []
    for y in range(16):
        row = ""
        for x in range(30):
            if y == 0 or y == 15:
                row += "T"
            elif x == 0:
                row += "T"
            elif x == 29:
                if 6 <= y <= 9:
                    row += "e"  # East to Viridian
                else:
                    row += "T"
            # Path
            elif 6 <= y <= 9:
                row += "p"
            # Tall grass
            elif (2 <= y <= 5 or 10 <= y <= 13) and 5 <= x <= 15:
                row += "G"
            # Water
            elif 2 <= y <= 5 and 20 <= x <= 27:
                row += "W"
            else:
                row += "g"
        r.append(row)
    return r

ROUTE22 = make_route22()

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTE 2 SOUTH (16x30)
# ═══════════════════════════════════════════════════════════════════════════════
def make_route2s():
    r = []
    for y in range(30):
        row = ""
        for x in range(16):
            if x == 0 or x == 15:
                row += "T"
            elif y == 0:
                if 6 <= x <= 9:
                    row += "n"  # North to Forest
                else:
                    row += "T"
            elif y == 29:
                if 6 <= x <= 9:
                    row += "s"  # South to Viridian
                else:
                    row += "T"
            elif 6 <= x <= 9:
                row += "p"
            elif (5 <= y <= 15) and (2 <= x <= 5 or 10 <= x <= 13):
                row += "G"
            else:
                row += "g"
        r.append(row)
    return r

ROUTE2S = make_route2s()

# ═══════════════════════════════════════════════════════════════════════════════
# MAP DATA
# ═══════════════════════════════════════════════════════════════════════════════
MAPS = {
    'pallet_town': {
        'name': 'PALLET TOWN',
        'data': PALLET,
        'wild': [],
        'lv': (2, 5),
    },
    'route_1': {
        'name': 'ROUTE 1',
        'data': ROUTE1,
        'wild': ['PIDGEY', 'RATTATA'],
        'lv': (2, 5),
    },
    'viridian_city': {
        'name': 'VIRIDIAN CITY',
        'data': VIRIDIAN,
        'wild': [],
        'lv': (3, 6),
    },
    'route_22': {
        'name': 'ROUTE 22',
        'data': ROUTE22,
        'wild': ['RATTATA', 'SPEAROW', 'NIDORAN_M', 'NIDORAN_F'],
        'lv': (2, 5),
    },
    'route_2': {
        'name': 'ROUTE 2',
        'data': ROUTE2S,
        'wild': ['PIDGEY', 'RATTATA', 'CATERPIE', 'WEEDLE'],
        'lv': (3, 5),
    },
}

# Warps: exit_char -> (map, x, y)
WARPS = {
    'pallet_town': {
        'n': ('route_1', 7, 70),
        's': ('route_21', 7, 1),  # Not implemented
    },
    'route_1': {
        's': ('pallet_town', 9, 1),
        'n': ('viridian_city', 11, 22),
    },
    'viridian_city': {
        's': ('route_1', 7, 1),
        'n': ('route_2', 7, 28),
        'w': ('route_22', 28, 7),
    },
    'route_22': {
        'e': ('viridian_city', 1, 11),
    },
    'route_2': {
        's': ('viridian_city', 11, 1),
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# POKEMON DATA (Gen 1 authentic)
# ═══════════════════════════════════════════════════════════════════════════════
POKEMON = {
    'BULBASAUR': {'id':1,'t':['GRASS','POISON'],'hp':45,'atk':49,'def':49,'spd':45,'spc':65,'moves':['TACKLE','GROWL'],'evo':('IVYSAUR',16)},
    'CHARMANDER': {'id':4,'t':['FIRE'],'hp':39,'atk':52,'def':43,'spd':65,'spc':50,'moves':['SCRATCH','GROWL'],'evo':('CHARMELEON',16)},
    'SQUIRTLE': {'id':7,'t':['WATER'],'hp':44,'atk':48,'def':65,'spd':43,'spc':50,'moves':['TACKLE','TAIL_WHIP'],'evo':('WARTORTLE',16)},
    'CATERPIE': {'id':10,'t':['BUG'],'hp':45,'atk':30,'def':35,'spd':45,'spc':20,'moves':['TACKLE','STRING_SHOT'],'evo':('METAPOD',7)},
    'WEEDLE': {'id':13,'t':['BUG','POISON'],'hp':40,'atk':35,'def':30,'spd':50,'spc':20,'moves':['POISON_STING','STRING_SHOT'],'evo':('KAKUNA',7)},
    'PIDGEY': {'id':16,'t':['NORMAL','FLYING'],'hp':40,'atk':45,'def':40,'spd':56,'spc':35,'moves':['TACKLE','GUST'],'evo':('PIDGEOTTO',18)},
    'RATTATA': {'id':19,'t':['NORMAL'],'hp':30,'atk':56,'def':35,'spd':72,'spc':25,'moves':['TACKLE','QUICK_ATTACK'],'evo':('RATICATE',20)},
    'SPEAROW': {'id':21,'t':['NORMAL','FLYING'],'hp':40,'atk':60,'def':30,'spd':70,'spc':31,'moves':['PECK','GROWL'],'evo':('FEAROW',20)},
    'PIKACHU': {'id':25,'t':['ELECTRIC'],'hp':35,'atk':55,'def':30,'spd':90,'spc':50,'moves':['THUNDER_SHOCK','QUICK_ATTACK']},
    'NIDORAN_M': {'id':32,'t':['POISON'],'hp':46,'atk':57,'def':40,'spd':50,'spc':40,'moves':['TACKLE','HORN_ATTACK'],'evo':('NIDORINO',16)},
    'NIDORAN_F': {'id':29,'t':['POISON'],'hp':55,'atk':47,'def':52,'spd':41,'spc':40,'moves':['TACKLE','SCRATCH'],'evo':('NIDORINA',16)},
}

MOVES = {
    'TACKLE': {'t':'NORMAL','p':35,'a':95,'pp':35},
    'SCRATCH': {'t':'NORMAL','p':40,'a':100,'pp':35},
    'GROWL': {'t':'NORMAL','p':0,'a':100,'pp':40,'ef':'atk-'},
    'TAIL_WHIP': {'t':'NORMAL','p':0,'a':100,'pp':30,'ef':'def-'},
    'GUST': {'t':'FLYING','p':40,'a':100,'pp':35},
    'PECK': {'t':'FLYING','p':35,'a':100,'pp':35},
    'QUICK_ATTACK': {'t':'NORMAL','p':40,'a':100,'pp':30,'pri':1},
    'THUNDER_SHOCK': {'t':'ELECTRIC','p':40,'a':100,'pp':30},
    'POISON_STING': {'t':'POISON','p':15,'a':100,'pp':35},
    'STRING_SHOT': {'t':'BUG','p':0,'a':95,'pp':40,'ef':'spd-'},
    'HORN_ATTACK': {'t':'NORMAL','p':65,'a':100,'pp':25},
}

TYPE_CHART = {
    'NORMAL': {'ROCK':0.5,'GHOST':0},
    'FIRE': {'FIRE':0.5,'WATER':0.5,'GRASS':2,'ICE':2,'BUG':2,'ROCK':0.5,'DRAGON':0.5},
    'WATER': {'FIRE':2,'WATER':0.5,'GRASS':0.5,'GROUND':2,'ROCK':2,'DRAGON':0.5},
    'ELECTRIC': {'WATER':2,'ELECTRIC':0.5,'GRASS':0.5,'GROUND':0,'FLYING':2,'DRAGON':0.5},
    'GRASS': {'FIRE':0.5,'WATER':2,'GRASS':0.5,'POISON':0.5,'GROUND':2,'FLYING':0.5,'BUG':0.5,'ROCK':2,'DRAGON':0.5},
    'FLYING': {'ELECTRIC':0.5,'GRASS':2,'FIGHTING':2,'BUG':2,'ROCK':0.5},
    'POISON': {'GRASS':2,'POISON':0.5,'GROUND':0.5,'BUG':2,'ROCK':0.5,'GHOST':0.5},
    'BUG': {'FIRE':0.5,'GRASS':2,'FIGHTING':0.5,'POISON':2,'FLYING':0.5,'PSYCHIC':2,'GHOST':0.5},
}

# ═══════════════════════════════════════════════════════════════════════════════
# GAME STATE
# ═══════════════════════════════════════════════════════════════════════════════
G = {
    'scr': 'title',
    'map': 'pallet_town',
    'px': 9, 'py': 8,
    'dir': 'down',
    'walk': 0,
    'frame': 0,
    'party': [],
    'bag': {'POTION': 5, 'POKE_BALL': 5},
    'money': 3000,
    'badges': [],
    'seen': set(),
    'caught': set(),
    'dlg': None,
    'battle': None,
    'menu': 0,
    'starter': 0,
}

# ═══════════════════════════════════════════════════════════════════════════════
# POKEMON CREATION
# ═══════════════════════════════════════════════════════════════════════════════
def make_mon(species, lv):
    if species not in POKEMON:
        return None
    b = POKEMON[species]
    
    # IVs (0-15 Gen1)
    iv = {k: random.randint(0,15) for k in ['atk','def','spd','spc']}
    iv['hp'] = ((iv['atk']&1)<<3)|((iv['def']&1)<<2)|((iv['spd']&1)<<1)|(iv['spc']&1)
    
    def stat(base, iv_val, is_hp=False):
        s = ((base + iv_val) * 2 * lv) // 100
        return s + lv + 10 if is_hp else s + 5
    
    hp = stat(b['hp'], iv['hp'], True)
    
    moves = []
    for m in b['moves'][:4]:
        if m in MOVES:
            moves.append({'id': m, 'pp': MOVES[m]['pp'], 'max': MOVES[m]['pp']})
    
    return {
        'species': species,
        'nick': species,
        'lv': lv,
        'exp': lv**3,
        'hp': hp,
        'maxhp': hp,
        'atk': stat(b['atk'], iv['atk']),
        'def': stat(b['def'], iv['def']),
        'spd': stat(b['spd'], iv['spd']),
        'spc': stat(b['spc'], iv['spc']),
        'moves': moves,
        'status': None,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING
# ═══════════════════════════════════════════════════════════════════════════════
font = pygame.font.Font(None, 16)
font_big = pygame.font.Font(None, 24)

def txt(s, x, y, c=C['blk']):
    t = font.render(str(s), False, c)
    gb.blit(t, (x, y))

def txt_big(s, x, y, c=C['blk']):
    t = font_big.render(str(s), False, c)
    gb.blit(t, (x, y))

def box(x, y, w, h):
    pygame.draw.rect(gb, C['wht'], (x, y, w, h))
    pygame.draw.rect(gb, C['blk'], (x, y, w, h), 2)
    pygame.draw.rect(gb, C['blk'], (x+2, y+2, w-4, h-4), 1)

def draw_player(x, y, d, walking, f):
    bob = 0
    if walking:
        bob = 1 if (f//8)%2==0 else -1
    
    # Colors
    body = C['red']
    skin = (248, 208, 176)
    hair = C['blk']
    
    if d == 'down':
        pygame.draw.rect(gb, body, (x+4, y+bob, 8, 4))       # Hat
        pygame.draw.rect(gb, hair, (x+4, y+4+bob, 8, 3))     # Hair
        pygame.draw.rect(gb, skin, (x+4, y+7+bob, 8, 5))     # Face
        pygame.draw.rect(gb, C['blk'], (x+5, y+8+bob, 2, 2)) # Eyes
        pygame.draw.rect(gb, C['blk'], (x+9, y+8+bob, 2, 2))
        pygame.draw.rect(gb, body, (x+3, y+12+bob, 10, 4))   # Body
    elif d == 'up':
        pygame.draw.rect(gb, body, (x+4, y+bob, 8, 4))
        pygame.draw.rect(gb, hair, (x+4, y+4+bob, 8, 8))
        pygame.draw.rect(gb, body, (x+3, y+12+bob, 10, 4))
    elif d == 'left':
        pygame.draw.rect(gb, body, (x+3, y+bob, 8, 4))
        pygame.draw.rect(gb, hair, (x+3, y+4+bob, 6, 3))
        pygame.draw.rect(gb, skin, (x+3, y+7+bob, 6, 5))
        pygame.draw.rect(gb, C['blk'], (x+4, y+8+bob, 2, 2))
        pygame.draw.rect(gb, body, (x+4, y+12+bob, 8, 4))
    elif d == 'right':
        pygame.draw.rect(gb, body, (x+5, y+bob, 8, 4))
        pygame.draw.rect(gb, hair, (x+7, y+4+bob, 6, 3))
        pygame.draw.rect(gb, skin, (x+7, y+7+bob, 6, 5))
        pygame.draw.rect(gb, C['blk'], (x+10, y+8+bob, 2, 2))
        pygame.draw.rect(gb, body, (x+4, y+12+bob, 8, 4))

def draw_mon(species, x, y, sz=48, flip=False):
    if species not in POKEMON:
        return
    p = POKEMON[species]
    c1 = TCOL.get(p['t'][0], (128,128,128))
    c2 = TCOL.get(p['t'][1], c1) if len(p['t']) > 1 else c1
    
    # Body
    bw, bh = int(sz*0.6), int(sz*0.5)
    bx, by = x + (sz-bw)//2, y + int(sz*0.35)
    
    for py in range(bh):
        t = py / max(1, bh)
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        pygame.draw.line(gb, (r,g,b), (bx, by+py), (bx+bw, by+py))
    
    # Head
    hs = int(sz*0.35)
    hx, hy = x + (sz-hs)//2, y + int(sz*0.1)
    pygame.draw.ellipse(gb, c1, (hx, hy, hs, hs))
    
    # Eyes
    es = max(2, sz//16)
    ey = hy + hs//3
    pygame.draw.circle(gb, C['blk'], (hx+hs//3, ey), es)
    pygame.draw.circle(gb, C['blk'], (hx+2*hs//3, ey), es)
    pygame.draw.circle(gb, C['wht'], (hx+hs//3-1, ey-1), max(1, es//2))
    pygame.draw.circle(gb, C['wht'], (hx+2*hs//3-1, ey-1), max(1, es//2))

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_title():
    gb.fill(C['wht'])
    txt_big("POKEMON", 48, 15, C['red'])
    txt_big("RED", 68, 40, C['red'])
    draw_mon('CHARMANDER', 56, 55, 48)
    if (G['frame']//30) % 2 == 0:
        txt("PRESS START", 45, 115, C['blk'])
    txt("Team Flames 2026", 35, 130, C['drk'])

def draw_starter():
    gb.fill(C['wht'])
    txt("Prof.OAK: Pick one!", 15, 5, C['blk'])
    
    starters = ['BULBASAUR', 'CHARMANDER', 'SQUIRTLE']
    for i, s in enumerate(starters):
        sx = 8 + i*50
        sy = 22
        
        if i == G['starter']:
            pygame.draw.rect(gb, C['red'], (sx-2, sy-2, 46, 75), 2)
        
        draw_mon(s, sx, sy, 38)
        txt(s[:7], sx, sy+42, C['blk'])
        
        tc = TCOL.get(POKEMON[s]['t'][0], (128,128,128))
        pygame.draw.rect(gb, tc, (sx, sy+54, 40, 10))
        txt(POKEMON[s]['t'][0][:5], sx+4, sy+55, C['wht'])
    
    txt("<- Z select ->", 35, 125, C['drk'])

def draw_world():
    m = MAPS[G['map']]
    data = m['data']
    mh = len(data)
    mw = len(data[0])
    
    # Camera
    cx = G['px']*16 - GBW//2 + 8
    cy = G['py']*16 - GBH//2 + 8
    
    gb.fill(C['blk'])
    
    # Draw tiles
    for ty in range(max(0, cy//16), min(mh, (cy+GBH)//16 + 2)):
        for tx in range(max(0, cx//16), min(mw, (cx+GBW)//16 + 2)):
            if 0 <= ty < mh and 0 <= tx < len(data[ty]):
                t = data[ty][tx]
                sx = tx*16 - cx
                sy = ty*16 - cy
                tile(t, sx, sy, G['frame'])
    
    # Player
    px = G['px']*16 - cx
    py = G['py']*16 - cy
    walking = G['walk'] > 0
    draw_player(px, py, G['dir'], walking, G['frame'])
    
    # HUD
    box(0, 0, GBW, 14)
    txt(m['name'], 5, 2, C['blk'])
    
    # Dialog
    if G['dlg']:
        box(0, GBH-38, GBW, 38)
        words = G['dlg'].split()
        l1, l2 = "", ""
        for w in words:
            if len(l1) + len(w) < 22:
                l1 += w + " "
            else:
                l2 += w + " "
        txt(l1, 8, GBH-33, C['blk'])
        txt(l2, 8, GBH-20, C['blk'])
        if (G['frame']//20)%2 == 0:
            txt("v", GBW-12, GBH-12, C['blk'])

def draw_battle():
    if not G['battle']:
        return
    b = G['battle']
    
    gb.fill(C['wht'])
    
    # Enemy
    draw_mon(b['enemy']['species'], 98, 8, 44)
    box(5, 5, 88, 32)
    txt(b['enemy']['species'][:10], 10, 8, C['blk'])
    txt(f"Lv{b['enemy']['lv']}", 62, 8, C['blk'])
    hp_pct = b['enemy']['hp'] / b['enemy']['maxhp']
    pygame.draw.rect(gb, C['blk'], (10, 20, 72, 8))
    col = (0,200,0) if hp_pct > 0.5 else (255,200,0) if hp_pct > 0.2 else (200,0,0)
    pygame.draw.rect(gb, col, (11, 21, int(70*hp_pct), 6))
    
    # Player
    draw_mon(b['player']['species'], 15, 52, 44, True)
    box(68, 48, 88, 42)
    txt(b['player']['species'][:10], 73, 51, C['blk'])
    txt(f"Lv{b['player']['lv']}", 127, 51, C['blk'])
    hp_pct = b['player']['hp'] / b['player']['maxhp']
    pygame.draw.rect(gb, C['blk'], (73, 63, 72, 8))
    col = (0,200,0) if hp_pct > 0.5 else (255,200,0) if hp_pct > 0.2 else (200,0,0)
    pygame.draw.rect(gb, col, (74, 64, int(70*hp_pct), 6))
    txt(f"{b['player']['hp']}/{b['player']['maxhp']}", 83, 76, C['blk'])
    
    # Menu
    box(0, 98, GBW, 46)
    
    if b['state'] == 'intro':
        txt(f"Wild {b['enemy']['species']}", 8, 105, C['blk'])
        txt("appeared!", 8, 118, C['blk'])
    elif b['state'] == 'menu':
        txt(b.get('msg', 'What will you do?'), 8, 102, C['blk'])
        opts = ['FIGHT', 'BAG', 'PKMN', 'RUN']
        for i, o in enumerate(opts):
            ox = 88 + (i%2)*36
            oy = 115 + (i//2)*12
            if i == b['menu']:
                txt(">", ox-8, oy, C['blk'])
            txt(o, ox, oy, C['blk'])
    elif b['state'] == 'moves':
        txt("Pick a move:", 8, 102, C['blk'])
        for i, mv in enumerate(b['player']['moves']):
            ox = 8 + (i%2)*70
            oy = 115 + (i//2)*12
            if i == b['msel']:
                txt(">", ox-6, oy, C['blk'])
            txt(mv['id'][:9], ox, oy, C['blk'])
    else:
        txt(b.get('msg', ''), 8, 108, C['blk'])

# ═══════════════════════════════════════════════════════════════════════════════
# GAME LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def get_tile(tx, ty):
    m = MAPS[G['map']]
    data = m['data']
    if 0 <= ty < len(data) and 0 <= tx < len(data[ty]):
        return data[ty][tx]
    return 'X'

def solid(t):
    return t in 'TWHRBLDSX'

def try_warp(tx, ty):
    t = get_tile(tx, ty)
    warps = WARPS.get(G['map'], {})
    
    if t == 'n' and 'n' in warps:
        return warps['n']
    elif t == 's' and 's' in warps:
        return warps['s']
    elif t == 'e' and 'e' in warps:
        return warps['e']
    elif t == 'w' and 'w' in warps:
        return warps['w']
    return None

def move(dx, dy):
    if G['dlg']:
        return
    
    # Direction
    if dx > 0: G['dir'] = 'right'
    elif dx < 0: G['dir'] = 'left'
    elif dy > 0: G['dir'] = 'down'
    elif dy < 0: G['dir'] = 'up'
    
    nx, ny = G['px'] + dx, G['py'] + dy
    t = get_tile(nx, ny)
    
    if solid(t):
        return
    
    # Warp?
    warp = try_warp(nx, ny)
    if warp:
        nm, wx, wy = warp
        G['map'] = nm
        G['px'] = wx
        G['py'] = wy
        G['dlg'] = f"Entered {MAPS[nm]['name']}!"
        return
    
    G['px'] = nx
    G['py'] = ny
    G['walk'] = 8
    
    # Encounter?
    if t == 'G':
        check_enc()

def check_enc():
    m = MAPS[G['map']]
    if not m['wild']:
        return
    
    if random.random() < 0.15:
        sp = random.choice(m['wild'])
        lv = random.randint(m['lv'][0], m['lv'][1])
        start_battle(sp, lv)

def start_battle(sp, lv):
    if not G['party']:
        return
    
    wild = make_mon(sp, lv)
    G['seen'].add(sp)
    
    G['battle'] = {
        'type': 'wild',
        'enemy': wild,
        'player': G['party'][0],
        'state': 'intro',
        'msg': f"Wild {sp} appeared!",
        'menu': 0,
        'msel': 0,
        'timer': 60,
    }
    G['scr'] = 'battle'

def calc_dmg(atk, dfn, mv):
    md = MOVES[mv['id']]
    if md['p'] == 0:
        return 0
    
    lv = atk['lv']
    a = atk['atk']
    d = dfn['def']
    
    dmg = ((2*lv//5 + 2) * md['p'] * a // d) // 50 + 2
    
    # Type eff
    mt = md['t']
    eff = 1.0
    if dfn['species'] in POKEMON:
        for dt in POKEMON[dfn['species']]['t']:
            if mt in TYPE_CHART and dt in TYPE_CHART[mt]:
                eff *= TYPE_CHART[mt][dt]
    
    # STAB
    if atk['species'] in POKEMON:
        if mt in POKEMON[atk['species']]['t']:
            eff *= 1.5
    
    dmg = int(dmg * eff * random.uniform(0.85, 1.0))
    return max(1, dmg) if eff > 0 else 0

def battle_tick():
    if not G['battle']:
        return
    b = G['battle']
    
    if b['timer'] > 0:
        b['timer'] -= 1
        return
    
    if b['state'] == 'intro':
        b['state'] = 'menu'
        b['msg'] = "What will you do?"
    
    elif b['state'] == 'player_turn':
        if b['enemy']['hp'] <= 0:
            exp = (POKEMON[b['enemy']['species']]['hp'] * b['enemy']['lv']) // 7
            b['player']['exp'] += exp
            b['state'] = 'won'
            b['msg'] = f"Gained {exp} EXP!"
            b['timer'] = 90
        else:
            # Enemy attacks
            if b['enemy']['moves']:
                em = random.choice(b['enemy']['moves'])
                dmg = calc_dmg(b['enemy'], b['player'], em)
                b['player']['hp'] = max(0, b['player']['hp'] - dmg)
                b['state'] = 'enemy_turn'
                b['msg'] = f"Foe used {em['id']}!"
                b['timer'] = 60
            else:
                b['state'] = 'menu'
    
    elif b['state'] == 'enemy_turn':
        if b['player']['hp'] <= 0:
            b['state'] = 'lost'
            b['msg'] = f"{b['player']['species']} fainted!"
            b['timer'] = 90
        else:
            b['state'] = 'menu'
            b['msg'] = "What will you do?"
    
    elif b['state'] in ('won', 'lost', 'run'):
        G['scr'] = 'world'
        G['battle'] = None

def interact():
    dx, dy = 0, 0
    if G['dir'] == 'up': dy = -1
    elif G['dir'] == 'down': dy = 1
    elif G['dir'] == 'left': dx = -1
    elif G['dir'] == 'right': dx = 1
    
    t = get_tile(G['px']+dx, G['py']+dy)
    
    if t == 'S':
        if G['map'] == 'pallet_town':
            G['dlg'] = "PALLET TOWN - Shades of your journey await!"
        else:
            G['dlg'] = "A sign is posted here."
    elif t == 'D':
        G['dlg'] = "The door is closed."

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    running = True
    
    while running:
        G['frame'] += 1
        if G['walk'] > 0:
            G['walk'] -= 1
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            
            elif ev.type == pygame.KEYDOWN:
                k = ev.key
                
                if G['scr'] == 'title':
                    if k in (pygame.K_RETURN, pygame.K_z):
                        G['scr'] = 'starter'
                
                elif G['scr'] == 'starter':
                    if k == pygame.K_LEFT:
                        G['starter'] = (G['starter'] - 1) % 3
                    elif k == pygame.K_RIGHT:
                        G['starter'] = (G['starter'] + 1) % 3
                    elif k in (pygame.K_RETURN, pygame.K_z):
                        starters = ['BULBASAUR', 'CHARMANDER', 'SQUIRTLE']
                        s = starters[G['starter']]
                        mon = make_mon(s, 5)
                        G['party'].append(mon)
                        G['seen'].add(s)
                        G['caught'].add(s)
                        G['dlg'] = f"You got {s}!"
                        G['scr'] = 'world'
                
                elif G['scr'] == 'world':
                    if G['dlg']:
                        if k in (pygame.K_RETURN, pygame.K_z, pygame.K_x):
                            G['dlg'] = None
                    else:
                        if k == pygame.K_UP: move(0, -1)
                        elif k == pygame.K_DOWN: move(0, 1)
                        elif k == pygame.K_LEFT: move(-1, 0)
                        elif k == pygame.K_RIGHT: move(1, 0)
                        elif k in (pygame.K_RETURN, pygame.K_z): interact()
                
                elif G['scr'] == 'battle':
                    b = G['battle']
                    if not b:
                        continue
                    
                    if b['state'] == 'menu':
                        if k == pygame.K_UP: b['menu'] = (b['menu']-2) % 4
                        elif k == pygame.K_DOWN: b['menu'] = (b['menu']+2) % 4
                        elif k == pygame.K_LEFT: b['menu'] = (b['menu']-1) % 4
                        elif k == pygame.K_RIGHT: b['menu'] = (b['menu']+1) % 4
                        elif k in (pygame.K_RETURN, pygame.K_z):
                            if b['menu'] == 0:  # FIGHT
                                b['state'] = 'moves'
                                b['msel'] = 0
                            elif b['menu'] == 3:  # RUN
                                b['state'] = 'run'
                                b['msg'] = "Got away safely!"
                                b['timer'] = 60
                    
                    elif b['state'] == 'moves':
                        mc = len(b['player']['moves'])
                        if k == pygame.K_UP: b['msel'] = (b['msel']-2) % mc
                        elif k == pygame.K_DOWN: b['msel'] = (b['msel']+2) % mc
                        elif k == pygame.K_LEFT: b['msel'] = (b['msel']-1) % mc
                        elif k == pygame.K_RIGHT: b['msel'] = (b['msel']+1) % mc
                        elif k in (pygame.K_RETURN, pygame.K_z):
                            mv = b['player']['moves'][b['msel']]
                            if mv['pp'] > 0:
                                mv['pp'] -= 1
                                dmg = calc_dmg(b['player'], b['enemy'], mv)
                                b['enemy']['hp'] = max(0, b['enemy']['hp'] - dmg)
                                b['state'] = 'player_turn'
                                b['msg'] = f"Used {mv['id']}!"
                                b['timer'] = 60
                        elif k in (pygame.K_x, pygame.K_ESCAPE):
                            b['state'] = 'menu'
        
        # Update
        if G['scr'] == 'battle':
            battle_tick()
        
        # Draw
        if G['scr'] == 'title':
            draw_title()
        elif G['scr'] == 'starter':
            draw_starter()
        elif G['scr'] == 'world':
            draw_world()
        elif G['scr'] == 'battle':
            draw_battle()
        
        # Scale to window
        pygame.transform.scale(gb, (WIN_W, WIN_H), screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == '__main__':
    print("=" * 50)
    print("  POKEMON RED - Team Flames 2026")
    print("=" * 50)
    print("  Arrows = Move | Z = Confirm | X = Cancel")
    print("=" * 50)
    main()

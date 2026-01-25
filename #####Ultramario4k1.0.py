#!/usr/bin/env python3
"""
Super Mario Bros Clone - Complete Game
Team Flames / Samsoft
All 32 Levels (1-1 through 8-4)
"""

import pygame
import math
import random

# Initialize
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
TILE_SIZE = 32
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (92, 148, 252)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
SKIN = (255, 200, 150)
BRICK_COLOR = (200, 76, 12)
QUESTION_COLOR = (255, 200, 50)
GROUND_COLOR = (139, 90, 43)
PIPE_GREEN = (0, 168, 0)
CASTLE_GRAY = (128, 128, 128)
LAVA_COLOR = (255, 100, 0)
GOOMBA_BROWN = (165, 82, 41)
KOOPA_GREEN = (0, 200, 0)

# Background colors
SKY_BLUE = (92, 148, 252)
UNDERGROUND = (0, 0, 0)
CASTLE_BG = (0, 0, 0)
NIGHT_SKY = (32, 32, 64)

# ═══════════════════════════════════════════════════════════════
# LEVEL DATA - All 32 Levels
# ═══════════════════════════════════════════════════════════════

LEVELS = {
    '1-1': {
        'bg': SKY_BLUE,
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                      ?                                                                                                                                                                     ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "              ?    B?B?B                                           ?                       BBB                                         ?B?                                                  ",
            "                                                                                                                                                                                          F ",
            "                                          PP                                  PP                         PP              PP                                     PP                         F ",
            "                          E            E  PP        E     E                   PP       E        E        PP     E        PP        E                   E        PP           E     E       F ",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG       GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG       GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '1-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X            ?          BBB?BBB                                     BBBBB                                                  BBBBBBB                                                         ",
            "X                                                                                                                                                                                          ",
            "X                                                     ?   ?   ?                      XXXX                                                          ?????                                   ",
            "X                                                                                    XXXX          XXXX                                                                                   F",
            "X                     XXXX              XXXX                                         XXXX          XXXX                XXXX                                                               F",
            "X          PP                           XXXX      E          E         E             XXXX    E     XXXX       E        XXXX             E                     E        E           E      F",
            "X     E    PP     E              E      XXXX                                   K                   XXXX                XXXX                   K         K                                  F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '1-3': {
        'bg': SKY_BLUE,
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                               BBB                                        BBB                                                                               ",
            "                                                                                                                                      BBB                                                   ",
            "                                    BBB           ?                      BBB                                          BBB                                                                   ",
            "               BBB                                                                        BBB                                                                                               ",
            "                          BBB              BBB                                                        BBB                       BBB              ?                                          ",
            "      BBB                                                                                                                                                             BBB                  F",
            "                     K                            E           K                   E                                       K                                  E                             F",
            "GGGG          GGGG             GGGG         GGGG        GGGG          GGGGG            GGGG       GGGG         GGGG             GGGG       GGGG        GGGG                   GGGGGGGGGGGGGF",
            "GGGG          GGGG             GGGG         GGGG        GGGG          GGGGG            GGGG       GGGG         GGGG             GGGG       GGGG        GGGG                   GGGGGGGGGGGGG ",
            "GGGG          GGGG             GGGG         GGGG        GGGG          GGGGG            GGGG       GGGG         GGGG             GGGG       GGGG        GGGG                   GGGGGGGGGGGGG ",
            "GGGG          GGGG             GGGG         GGGG        GGGG          GGGGG            GGGG       GGGG         GGGG             GGGG       GGGG        GGGG                   GGGGGGGGGGGGG ",
        ]
    },
    
    '1-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                       XXXXX                                                             X",
            "X                                                                       XXXXX                                           X   X                                                             X",
            "X                       XXXXX                                           X   X                     XXXXX                 X   X                      XXXXX                                  X",
            "X                       X   X                   XXXXX                   X   X                     X   X                 X   X                      X   X                                  X",
            "X                       X   X                   X   X                   X   X                     X   X                 X   X                      X   X                                  X",
            "X  XXXXX       XXXXX    X   X       XXXXX       X   X         XXXXX     X   X           XXXXX     X   X       XXXXX     X   X            XXXXX     X   X                         XXXXXAX  X",
            "X         E            E         E            E         E             E         E               E         E            E         E               E              E       E       E        X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '2-1': {
        'bg': (252, 216, 168),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                    ?                                                                         ?                                                             ",
            "                  ?                                                                   B?B                                                                                                   ",
            "                                     B?B?B                                                                                                   BBB?BBB                                        ",
            "            B?B                                                                                                                                                                            F",
            "                                                          PP                                   PP                                                                     PP                   F",
            "                     E     K     E        E     K    E    PP        E   E   K     E    K        PP      E    K      E     K        E      K       E    E    K     E    PP       E    K     F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '2-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                  BBB                                                                                                                                                                     ",
            "X                                                          BBB             ?                                                                                                               ",
            "X            ?                           ?????                                                        BBBBB                                                                                ",
            "X                           BBB                                    BBB                                                                            BBBBBBB                                 ",
            "X                                                                                     BBB                                  BBB                                                             ",
            "X                XXXX                                         XXXX                                XXXX               XXXX               XXXX                                              F",
            "X                XXXX           XXXX                          XXXX       XXXX                     XXXX               XXXX               XXXX                    XXXX                      F",
            "X     E    K     XXXX   E   K   XXXX    E    K    E      K    XXXX   E   XXXX    K    E      K    XXXX    E    K     XXXX    E     K    XXXX     E     K     E   XXXX    E    K    E      F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '2-3': {
        'bg': (252, 216, 168),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                        BBB?BBB                                                                                                             ",
            "                                                                                                                     B?B                                                                    ",
            "                               BBB                                                                                                                         BBB                              ",
            "                                                     BBB                           BBB                                          BBB                                                         ",
            "            BBB       ?                                                                        BBB                                            ?                                             ",
            "                                       BBB                      BBB                                        BBB                         BBB                        BBB                      F",
            "     E  K            K      E        K        E    K        E          K       E         K          E   K          E      K        E         K     E    K        E         K    E    K    F",
            "GGG       GGGG          GGGG      GGGGG         GGGG          GGGG         GGGG      GGGG        GGGG        GGGG       GGGG          GGGG         GGGG       GGGG      GGGG        GGGGGGGGF",
            "GGG       GGGG          GGGG      GGGGG         GGGG          GGGG         GGGG      GGGG        GGGG        GGGG       GGGG          GGGG         GGGG       GGGG      GGGG        GGGGGGGG ",
            "GGG       GGGG          GGGG      GGGGG         GGGG          GGGG         GGGG      GGGG        GGGG        GGGG       GGGG          GGGG         GGGG       GGGG      GGGG        GGGGGGGG ",
            "GGG       GGGG          GGGG      GGGGG         GGGG          GGGG         GGGG      GGGG        GGGG        GGGG       GGGG          GGGG         GGGG       GGGG      GGGG        GGGGGGGG ",
        ]
    },
    
    '2-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                    XXXXX                                                              XXXXX                                                                             X",
            "X                                    X   X                           XXXXX                              X   X                                                                             X",
            "X           XXXXX                    X   X                           X   X               XXXXX          X   X                                        XXXXX                                X",
            "X           X   X       XXXXX        X   X          XXXXX            X   X               X   X          X   X            XXXXX                       X   X                                X",
            "X           X   X       X   X        X   X          X   X            X   X               X   X          X   X            X   X                       X   X                                X",
            "X  XXXXX    X   X       X   X        X   X          X   X            X   X     XXXXX     X   X          X   X    XXXXX   X   X     XXXXX             X   X            XXXXX     XXXXXAX   X",
            "X      E       E           E            E    K          E      K         E           E           K          E        K        E           K     E        E      E       E           E    X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '3-1': {
        'bg': (92, 168, 92),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                   B?B                                                                      ",
            "                                                                                                                                                                                            ",
            "                                                        BBB?BBB                                                                           BBB                                               ",
            "                      ?                                                                                    BBB                                                                              ",
            "                                    BBB                                                 BBB                                                                                                 ",
            "              BBB                                              ?                                                                                  ?????                                      ",
            "                          PP                        BBB                                                                        PP                                  PP                       F",
            "                          PP                                             PP                   PP                               PP        W             W           PP                       F",
            "     E    K    E          PP      E     K      E    K                    PP       E    K      PP      E      K      E          PP       E      K      E      K     PP        E     K       F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '3-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                            ?????                                                                                                         ",
            "X                                     BBBBB                                                                         BBBBBBB                                                                ",
            "X                                                                 BBB                                                                                                                      ",
            "X                  ?                                                                          BBB                                                    BBB                                   ",
            "X                                                  BBB                                                                                                                                     ",
            "X                         BBB                                             BBB                            BBB                                                   BBB                         ",
            "X         XXXX                           XXXX                 XXXX                  XXXX                        XXXX                  XXXX                             XXXX                F",
            "X         XXXX    XXXX                   XXXX        XXXX     XXXX       XXXX       XXXX         XXXX           XXXX       XXXX       XXXX          XXXX               XXXX                F",
            "X    E    XXXX K  XXXX    E    K    E    XXXX  E  K  XXXX  E  XXXX   K   XXXX   E   XXXX    K    XXXX  E   K    XXXX   E   XXXX   K   XXXX     E    XXXX    E   K      XXXX   E    K       F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '3-3': {
        'bg': (92, 168, 92),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                      B?B                                                   ",
            "                                                                   BBB                                                                                                                      ",
            "                                                                                                             BBB                                            BBB                             ",
            "                        B?B                                                        BBB                                                        BBB                                           ",
            "                                       BBB              BBB                                                                                                                                 ",
            "              BBB                                                        BBB                    BBB                       BBB                        BBB                                   F",
            "                                                              W                           W                   W                     W                             W                        F",
            "GGGG      GGGGG        GGGG        GGGG       GGGG        GGGGG      GGGG      GGGG       GGGG      GGGG       GGGG      GGGG        GGGG       GGGG       GGGG        GGGG       GGGGGGGGGF",
            "GGGG      GGGGG        GGGG        GGGG       GGGG        GGGGG      GGGG      GGGG       GGGG      GGGG       GGGG      GGGG        GGGG       GGGG       GGGG        GGGG       GGGGGGGGG ",
            "GGGG      GGGGG        GGGG        GGGG       GGGG        GGGGG      GGGG      GGGG       GGGG      GGGG       GGGG      GGGG        GGGG       GGGG       GGGG        GGGG       GGGGGGGGG ",
            "GGGG      GGGGG        GGGG        GGGG       GGGG        GGGGG      GGGG      GGGG       GGGG      GGGG       GGGG      GGGG        GGGG       GGGG       GGGG        GGGG       GGGGGGGGG ",
        ]
    },
    
    '3-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                        XXXXX                                                                                            XXXXX                           X",
            "X                              XXXXX                      X   X                                    XXXXX                                                   X   X                           X",
            "X                              X   X                      X   X           XXXXX                    X   X                                 XXXXX            X   X                           X",
            "X          XXXXX               X   X        XXXXX         X   X           X   X                    X   X          XXXXX                  X   X            X   X          XXXXX            X",
            "X          X   X               X   X        X   X         X   X           X   X                    X   X          X   X                  X   X            X   X          X   X            X",
            "X  XXXXX   X   X      XXXXX    X   X        X   X         X   X   XXXXX   X   X         XXXXX      X   X  XXXXX   X   X        XXXXX     X   X    XXXXX   X   X  XXXXX   X   X    XXXXXAX X",
            "X   E  K      E   K      E   K     E    K      E    K        E       E   K       E   K        E       E      E K       E   K        E K       E      E   K     E      E        E          X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '4-1': {
        'bg': (200, 220, 255),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                            ?                                                                                                                               ",
            "                    ?                                                                        B?B                                                                                           ",
            "                                     BBB?BBB                              BBB                                              BBB?BBB                                                          ",
            "              BBB                                                                                                                                                                          F",
            "                              PP                                                      PP                                                            PP                                     F",
            "     E  K     E    K   E      PP      E     K    E     K       E    K     E      K    PP      E      K      E    K    E     E      K     E    K     PP       E     K      E     K          F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG       GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG       GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG      GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG       GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '4-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                             BBB                                                                                                                                                          ",
            "X                                                        ?????                                                    BBB                                                                      ",
            "X            ?                          BBB                                       BBB                                                              BBB                                     ",
            "X                      BBB                                           BBB                                                         BBB                                                       ",
            "X         XXXX                   XXXX              XXXX                     XXXX              XXXX                      XXXX              XXXX                   XXXX                      F",
            "X         XXXX      XXXX         XXXX     XXXX     XXXX        XXXX         XXXX     XXXX     XXXX         XXXX         XXXX     XXXX     XXXX        XXXX        XXXX                      F",
            "X   E K   XXXX  K   XXXX    E    XXXX  E  XXXX K   XXXX   K    XXXX    E    XXXX  K  XXXX E   XXXX    E    XXXX    K    XXXX E   XXXX K   XXXX   E    XXXX   K    XXXX     E   K    E      F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '4-3': {
        'bg': (200, 220, 255),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                        BBB                                                                 ",
            "                                                                         B?B                                                                                                                ",
            "                                             BBB                                                                                        BBB                                                 ",
            "                       BBB                                                             BBB                     BBB                                                                          ",
            "              ?                                           BBB                                                                                              ?                                ",
            "        BBB                      BBB                                         BBB                                          BBB                    BBB                                       F",
            "                   W                      W                       W                      W                  W                       W                      W                               F",
            "GGG        GGGG        GGGG         GGGG       GGGG         GGGG        GGGG       GGGG       GGGG      GGGG        GGGG        GGGG       GGGG        GGGG       GGGG          GGGGGGGGGGGGF",
            "GGG        GGGG        GGGG         GGGG       GGGG         GGGG        GGGG       GGGG       GGGG      GGGG        GGGG        GGGG       GGGG        GGGG       GGGG          GGGGGGGGGGGGG",
            "GGG        GGGG        GGGG         GGGG       GGGG         GGGG        GGGG       GGGG       GGGG      GGGG        GGGG        GGGG       GGGG        GGGG       GGGG          GGGGGGGGGGGGG",
            "GGG        GGGG        GGGG         GGGG       GGGG         GGGG        GGGG       GGGG       GGGG      GGGG        GGGG        GGGG       GGGG        GGGG       GGGG          GGGGGGGGGGGGG",
        ]
    },
    
    '4-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                      XXXXX                                              X",
            "X                                           XXXXX                                              XXXXX                                    X   X                                              X",
            "X                       XXXXX               X   X               XXXXX                          X   X                       XXXXX        X   X                                              X",
            "X                       X   X               X   X               X   X                          X   X          XXXXX        X   X        X   X           XXXXX                              X",
            "X          XXXXX        X   X               X   X               X   X         XXXXX            X   X          X   X        X   X        X   X           X   X                              X",
            "X  XXXXX   X   X        X   X    XXXXX      X   X      XXXXX    X   X         X   X   XXXXX    X   X  XXXXX   X   X        X   X        X   X   XXXXX   X   X       XXXXX    XXXXX  XXXXXAX",
            "X   E  K      E    K        E        E  K        E K       E K       E   K       E        E K       E     E         E  K        E  K         E      E        E  K       E        E        X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '5-1': {
        'bg': (180, 200, 255),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                           ?                                                                                                                                ",
            "                    ?                                                                     ?????                                                                                             ",
            "                                    B?B?B                               BBB                                             B?B?B                                                               ",
            "              BBB                                                                                                                                           BBB                             ",
            "                                                                                                                                                                                           F",
            "                         PP                                                       PP                                                              PP                                       F",
            "     E   K    E    K     PP      E    K     E    K    E     K       E    K    E   PP      E    K     E     K     E    K     E    K     E     K    PP        E     K      E    K     E      F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '5-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                         BBB                                                                    BBBBB                                                                     ",
            "X                                                                     BBB                                                                                                                  ",
            "X               ?                                   ?????                                                                            BBB                                                   ",
            "X                            BBB                                                      BBB                                                                                                  ",
            "X                                                                            BBB                        BBB                                       BBB                                      ",
            "X        XXXX                     XXXX                    XXXX                    XXXX                        XXXX                   XXXX                   XXXX                           F",
            "X        XXXX       XXXX          XXXX      XXXX          XXXX       XXXX         XXXX        XXXX            XXXX      XXXX         XXXX       XXXX        XXXX           XXXX            F",
            "X  E K   XXXX  E K  XXXX     E K  XXXX  E K XXXX     E K  XXXX  E K  XXXX    E K  XXXX   E K  XXXX     E  K   XXXX  E K XXXX    E K  XXXX  E K  XXXX   E K  XXXX     E K   XXXX    E  K   F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '5-3': {
        'bg': (180, 200, 255),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                          BBB                                                               ",
            "                                                      BBB?BBB                                              BBB                                                                              ",
            "                       BBB                                                     BBB                                                           BBB                                            ",
            "                                    BBB                           BBB                          BBB                                                      ?                                   ",
            "        BBB                                                                                                     BBB                    BBB                                                 F",
            "                    W            W              W           W            W             W              W                W          W              W            W                            F",
            "GGG         GGGG        GGGG         GGGG          GGGG         GGGG         GGGG          GGGG          GGGG         GGGG         GGGG        GGGG       GGGG         GGGG       GGGGGGGGGGF",
            "GGG         GGGG        GGGG         GGGG          GGGG         GGGG         GGGG          GGGG          GGGG         GGGG         GGGG        GGGG       GGGG         GGGG       GGGGGGGGGGG",
            "GGG         GGGG        GGGG         GGGG          GGGG         GGGG         GGGG          GGGG          GGGG         GGGG         GGGG        GGGG       GGGG         GGGG       GGGGGGGGGGG",
            "GGG         GGGG        GGGG         GGGG          GGGG         GGGG         GGGG          GGGG          GGGG         GGGG         GGGG        GGGG       GGGG         GGGG       GGGGGGGGGGG",
        ]
    },
    
    '5-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                     XXXXX                                                     XXXXX                     X",
            "X                                   XXXXX                              XXXXX                          X   X                                                     X   X                     X",
            "X                                   X   X          XXXXX               X   X              XXXXX       X   X                  XXXXX                              X   X         XXXXX       X",
            "X        XXXXX                      X   X          X   X               X   X              X   X       X   X                  X   X          XXXXX               X   X         X   X       X",
            "X        X   X         XXXXX        X   X          X   X               X   X              X   X       X   X       XXXXX      X   X          X   X               X   X         X   X       X",
            "X  XXXXX X   X         X   X        X   X   XXXXX  X   X       XXXXX   X   X    XXXXX     X   X       X   X       X   X      X   X   XXXXX  X   X    XXXXX      X   X  XXXXX  X   X  XXXXXAX",
            "X  E  K       E   K         E   K        E     E        E  K       E K       E       E K       E  K        E  K        E  K       E      E        E       E  K       E     E        E     X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '6-1': {
        'bg': (80, 40, 40),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                      ?                                                                 ?                                                                                                   ",
            "                                             B?B?B                                                                        BBB?BBB                                                          ",
            "                               BBB                                          BBB                                                                                  BBB                        ",
            "             BBB                                                                                                                                                                           F",
            "                          PP                                                        PP                                                                   PP                                F",
            "    E   K    E     K      PP        E    K     E    K    E     K    E    K    E     PP        E    K    E    K     E     K    E    K    E     K    E     PP        E    K     E     K      F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG        GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '6-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                  BBBBB                                                                                   ",
            "X                                  BBB                                      BBB                                                                                                            ",
            "X             ?                                   ?????                                                                          BBB                                                       ",
            "X                          BBB                                                          BBB                                                                      BBB                       ",
            "X                                            BBB                    BBB                                      BBB                             BBB                                           ",
            "X       XXXX                    XXXX                  XXXX                   XXXX                 XXXX                  XXXX                       XXXX                   XXXX             F",
            "X       XXXX      XXXX          XXXX      XXXX        XXXX      XXXX         XXXX      XXXX       XXXX       XXXX       XXXX       XXXX            XXXX       XXXX        XXXX             F",
            "X  E K  XXXX E K  XXXX    E  K  XXXX E K  XXXX   E K  XXXX E K  XXXX    E K  XXXX E K  XXXX  E K  XXXX  E K  XXXX  E K  XXXX  E K  XXXX     E  K   XXXX  E K  XXXX   E K  XXXX    E  K    F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '6-3': {
        'bg': (80, 40, 40),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                               ?????                                                                                                                        ",
            "                                                                                                                          BBB                                                               ",
            "                      BBB                                                                     BBB                                                   BBB                                     ",
            "                                      BBB                               BBB                                                         BBB                             ?                        ",
            "         BBB                                        BBB                           BBB                       BBB                                                                            F",
            "                  W              W              W             W              W              W             W              W              W              W             W                      F",
            "GGG         GGGG       GGGG          GGGG          GGGG          GGGG          GGGG           GGGG          GGGG          GGGG           GGGG         GGGG         GGGG          GGGGGGGGGGGF",
            "GGG         GGGG       GGGG          GGGG          GGGG          GGGG          GGGG           GGGG          GGGG          GGGG           GGGG         GGGG         GGGG          GGGGGGGGGGGG",
            "GGG         GGGG       GGGG          GGGG          GGGG          GGGG          GGGG           GGGG          GGGG          GGGG           GGGG         GGGG         GGGG          GGGGGGGGGGGG",
            "GGG         GGGG       GGGG          GGGG          GGGG          GGGG          GGGG           GGGG          GGGG          GGGG           GGGG         GGGG         GGGG          GGGGGGGGGGGG",
        ]
    },
    
    '6-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                       XXXXX                                                                              XXXXX                          X",
            "X                          XXXXX                                        X   X                         XXXXX                                                X   X                          X",
            "X                          X   X                      XXXXX             X   X                         X   X                        XXXXX                   X   X                          X",
            "X       XXXXX              X   X         XXXXX        X   X             X   X          XXXXX          X   X            XXXXX       X   X                   X   X           XXXXX          X",
            "X       X   X              X   X         X   X        X   X             X   X          X   X          X   X            X   X       X   X                   X   X           X   X          X",
            "X  XXXXX X  X     XXXXX    X   X  XXXXX  X   X XXXXX  X   X    XXXXX    X   X  XXXXX   X   X   XXXXX  X   X    XXXXX   X   X XXXXX X   X   XXXXX    XXXXX  X   X    XXXXX  X   X   XXXXXAX X",
            "X  E K       E K       E K      E     E       E    E       E K      E K      E     E        E      E       E K     E        E   E       E      E K      E       E K     E       E        X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '7-1': {
        'bg': NIGHT_SKY,
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                       ?                                               ?                                                     ?                                                              ",
            "                                          B?B?B                                                  BBB?BBB                                                   B?B?B                           ",
            "                  BBB                                            BBB                                                                       BBB                                              ",
            "          BBB                                                                                                                                                                              F",
            "                             PP                                                          PP                                                                          PP                    F",
            "   E   K   E    K    E       PP      E    K    E   K    E    K    E   K    E    K    E   PP      E   K    E   K    E    K   E   K    E   K   E    K    E   K    E    PP     E   K    E     F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG         GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG         GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG         GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG         GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG         GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG         GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '7-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                            BBB                                                                                        BBBBB                                                              ",
            "X             ?                                   ?????                                  BBB                                                                                               ",
            "X                      BBB                                        BBB                                                                               BBB                                    ",
            "X                                      BBB                                     BBB                           BBB                          BBB                                               ",
            "X      XXXX                   XXXX                 XXXX                   XXXX                  XXXX                   XXXX                     XXXX                   XXXX                F",
            "X      XXXX     XXXX          XXXX      XXXX       XXXX      XXXX         XXXX      XXXX        XXXX      XXXX         XXXX       XXXX          XXXX       XXXX        XXXX                F",
            "X  EK  XXXX EK  XXXX    EK    XXXX  EK  XXXX  EK   XXXX  EK  XXXX    EK   XXXX  EK  XXXX   EK   XXXX  EK  XXXX    EK   XXXX   EK  XXXX    EK    XXXX  EK   XXXX   EK   XXXX    EK    EK   F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '7-3': {
        'bg': NIGHT_SKY,
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                              ?????                                                                     BBB                                                 ",
            "                                                                                                        BBB                                                                                 ",
            "                      BBB                                                            BBB                                                          BBB                                       ",
            "                                     BBB                              BBB                                            BBB                                                                    ",
            "         BBB                                        BBB                                         BBB                              BBB                                 BBB                   F",
            "                 W              W              W              W             W              W              W              W             W              W              W                      F",
            "GGG         GGGG      GGGG          GGGG         GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGGF",
            "GGG         GGGG      GGGG          GGGG         GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGGG",
            "GGG         GGGG      GGGG          GGGG         GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGGG",
            "GGG         GGGG      GGGG          GGGG         GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGGG",
        ]
    },
    
    '7-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                                                                                                                                         X",
            "X                                                                  XXXXX                                                                                       XXXXX                      X",
            "X                          XXXXX                                   X   X                              XXXXX                                                    X   X                      X",
            "X                          X   X                    XXXXX          X   X                              X   X                         XXXXX                      X   X                      X",
            "X       XXXXX              X   X        XXXXX       X   X          X   X           XXXXX              X   X             XXXXX       X   X                      X   X          XXXXX       X",
            "X       X   X              X   X        X   X       X   X          X   X           X   X              X   X             X   X       X   X                      X   X          X   X       X",
            "X  XXXXX X  X     XXXXX    X   X XXXXX  X   X XXXXX X   X   XXXXX  X   X   XXXXX   X   X    XXXXX     X   X    XXXXX    X   X XXXXX X   X   XXXXX    XXXXX     X   X   XXXXX  X   X  XXXXXAX",
            "X  EK       EK        EK       E    EK      E   EK       EK    EK       EK    EK        EK       EK        EK      EK       E   EK      EK      EK       EK        EK     EK       E      X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXXXXXX",
        ]
    },
    
    '8-1': {
        'bg': (40, 20, 20),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                       ?                                                      ?                                                       ?                                                     ",
            "                                          BBB?BBB                                                  B?B?B?B                                                    BBB?BBB                      ",
            "                  BBB                                                  BBB                                                    BBB                                                           ",
            "          BBB                                                                                                                                                                              F",
            "                             PP                                                               PP                                                                        PP                 F",
            "   EK  EK  EK  EK  EK        PP     EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK    PP     EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK  EK        PP     EK  EK  EK   F",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG          GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG          GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG          GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG          GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG          GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG          GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '8-2': {
        'bg': UNDERGROUND,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                                                                                                                                                                                          ",
            "X                              BBB                                                                                                    BBBBB                                                ",
            "X             ?                                      ?????                                      BBB                                                                                        ",
            "X                        BBB                                               BBB                                                                                 BBB                         ",
            "X                                         BBB                                         BBB                          BBB                            BBB                                      ",
            "X     XXXX                     XXXX                    XXXX                    XXXX                  XXXX                    XXXX                        XXXX                   XXXX       F",
            "X     XXXX      XXXX           XXXX       XXXX         XXXX       XXXX         XXXX       XXXX       XXXX       XXXX         XXXX        XXXX            XXXX        XXXX       XXXX       F",
            "X EK  XXXX  EK  XXXX    EK     XXXX  EK   XXXX    EK   XXXX  EK   XXXX    EK   XXXX  EK   XXXX  EK   XXXX  EK   XXXX    EK   XXXX   EK   XXXX     EK     XXXX   EK   XXXX  EK   XXXX  EK   F",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "XGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
    },
    
    '8-3': {
        'bg': (40, 20, 20),
        'map': [
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                                                                                                                                            ",
            "                                                                ?????                                                                                                                       ",
            "                                                                                                                            BBB                                                             ",
            "                       BBB                                                                        BBB                                                      BBB                              ",
            "                                        BBB                                  BBB                                                            BBB                                             ",
            "         BBB                                            BBB                             BBB                       BBB                                                BBB                    F",
            "                  W              W               W              W              W              W              W             W              W              W              W                   F",
            "GGG         GGGG       GGGG          GGGG          GGGG           GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGF",
            "GGG         GGGG       GGGG          GGGG          GGGG           GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGG",
            "GGG         GGGG       GGGG          GGGG          GGGG           GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGG",
            "GGG         GGGG       GGGG          GGGG          GGGG           GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGG          GGGGGGGGGGGG",
        ]
    },
    
    '8-4': {
        'bg': CASTLE_BG,
        'map': [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "X                                                                                                                                                                                                                                  X",
            "X                                                                                                                                                                                                                                  X",
            "X                                                                                                                                                                                                                                  X",
            "X                                                                                                                                       XXXXX                                                             XXXXX                    X",
            "X                                      XXXXX                                                      XXXXX                                 X   X                                    XXXXX                    X   X                    X",
            "X                                      X   X                           XXXXX                      X   X                                 X   X                                    X   X                    X   X                    X",
            "X           XXXXX                      X   X           XXXXX           X   X                      X   X            XXXXX                X   X             XXXXX                  X   X           XXXXX    X   X          XXXXX     X",
            "X           X   X                      X   X           X   X           X   X                      X   X            X   X                X   X             X   X                  X   X           X   X    X   X          X   X     X",
            "X  XXXXX    X   X      XXXXX           X   X    XXXXX  X   X    XXXXX  X   X    XXXXX   XXXXX     X   X    XXXXX   X   X    XXXXX       X   X    XXXXX    X   X    XXXXX  XXXXX  X   X   XXXXX   X   X    X   X   XXXXX  X   X  XXAX",
            "X  EK  EK       EK EK      EK  EK  EK       EK      EK      EK      EK      EK      EK      EK EK      EK      EK      EK      EK  EK       EK       EK       EK       EK    EK       EK     EK      EK       EK      EK      EK   X",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXX",
            "XLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLXXXXXXX",
        ]
    },
}

LEVEL_ORDER = [
    '1-1', '1-2', '1-3', '1-4',
    '2-1', '2-2', '2-3', '2-4',
    '3-1', '3-2', '3-3', '3-4',
    '4-1', '4-2', '4-3', '4-4',
    '5-1', '5-2', '5-3', '5-4',
    '6-1', '6-2', '6-3', '6-4',
    '7-1', '7-2', '7-3', '7-4',
    '8-1', '8-2', '8-3', '8-4',
]

def get_next_level(current_level):
    try:
        idx = LEVEL_ORDER.index(current_level)
        if idx + 1 < len(LEVEL_ORDER):
            return LEVEL_ORDER[idx + 1]
        return None
    except ValueError:
        return '1-1'


# ═══════════════════════════════════════════════════════════════
# GRAPHICS GENERATOR - Procedural Textures
# ═══════════════════════════════════════════════════════════════

class Graphics:
    def __init__(self):
        self.textures = {}
        self.generate_textures()
    
    def generate_textures(self):
        # Brick Block
        brick = pygame.Surface((TILE_SIZE, TILE_SIZE))
        brick.fill(BRICK_COLOR)
        pygame.draw.line(brick, (100, 50, 0), (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
        pygame.draw.line(brick, (100, 50, 0), (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE//2), 2)
        pygame.draw.line(brick, (100, 50, 0), (0, 0), (0, TILE_SIZE), 2)
        pygame.draw.line(brick, (100, 50, 0), (TILE_SIZE-1, 0), (TILE_SIZE-1, TILE_SIZE), 2)
        pygame.draw.rect(brick, (80, 40, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        self.textures['B'] = brick
        
        # Question Block
        question = pygame.Surface((TILE_SIZE, TILE_SIZE))
        question.fill(QUESTION_COLOR)
        pygame.draw.rect(question, (200, 150, 0), (0, 0, TILE_SIZE, TILE_SIZE), 3)
        font = pygame.font.Font(None, 28)
        q_text = font.render("?", True, WHITE)
        question.blit(q_text, (TILE_SIZE//2 - q_text.get_width()//2, TILE_SIZE//2 - q_text.get_height()//2))
        self.textures['?'] = question
        
        # Ground Block
        ground = pygame.Surface((TILE_SIZE, TILE_SIZE))
        ground.fill(GROUND_COLOR)
        pygame.draw.rect(ground, (100, 60, 30), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        for i in range(0, TILE_SIZE, 8):
            pygame.draw.line(ground, (80, 50, 20), (i, 0), (i, TILE_SIZE), 1)
            pygame.draw.line(ground, (80, 50, 20), (0, i), (TILE_SIZE, i), 1)
        self.textures['G'] = ground
        
        # Pipe Block
        pipe = pygame.Surface((TILE_SIZE, TILE_SIZE))
        pipe.fill(PIPE_GREEN)
        pygame.draw.rect(pipe, (0, 200, 0), (2, 0, TILE_SIZE-4, TILE_SIZE), 0)
        pygame.draw.rect(pipe, (0, 100, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        pygame.draw.line(pipe, (0, 220, 0), (4, 0), (4, TILE_SIZE), 2)
        self.textures['P'] = pipe
        
        # Castle/Stone Block
        stone = pygame.Surface((TILE_SIZE, TILE_SIZE))
        stone.fill(CASTLE_GRAY)
        pygame.draw.rect(stone, (100, 100, 100), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        pygame.draw.line(stone, (80, 80, 80), (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 1)
        pygame.draw.line(stone, (80, 80, 80), (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE), 1)
        self.textures['X'] = stone
        
        # Lava
        lava = pygame.Surface((TILE_SIZE, TILE_SIZE))
        lava.fill(LAVA_COLOR)
        for i in range(4):
            y = i * 8
            pygame.draw.arc(lava, (255, 200, 0), (0, y, TILE_SIZE, 16), 0, 3.14, 2)
        self.textures['L'] = lava
        
        # Axe (level end)
        axe = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(axe, (139, 69, 19), (12, 8, 8, 20))  # Handle
        pygame.draw.polygon(axe, (192, 192, 192), [(8, 4), (24, 4), (28, 12), (4, 12)])  # Blade
        self.textures['A'] = axe
    
    def create_mario_sprite(self, big=False):
        """Create Mario sprite"""
        h = 48 if big else 32
        mario = pygame.Surface((24, h), pygame.SRCALPHA)
        
        # Hat
        pygame.draw.rect(mario, RED, (4, 0, 16, 8))
        # Face  
        pygame.draw.rect(mario, SKIN, (4, 8, 16, 10))
        # Eyes
        pygame.draw.rect(mario, BLACK, (6, 10, 4, 4))
        pygame.draw.rect(mario, BLACK, (14, 10, 4, 4))
        # Mustache
        pygame.draw.rect(mario, BROWN, (4, 16, 16, 4))
        # Body
        pygame.draw.rect(mario, RED, (2, 20, 20, 12 if not big else 16))
        # Overalls
        pygame.draw.rect(mario, BLUE, (4, 26 if not big else 30, 16, 8 if not big else 12))
        # Legs
        if big:
            pygame.draw.rect(mario, BLUE, (4, 38, 6, 10))
            pygame.draw.rect(mario, BLUE, (14, 38, 6, 10))
        else:
            pygame.draw.rect(mario, BLUE, (4, 28, 6, 4))
            pygame.draw.rect(mario, BLUE, (14, 28, 6, 4))
        
        return mario
    
    def create_goomba_sprite(self):
        """Create Goomba enemy sprite"""
        goomba = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Body (mushroom shape)
        pygame.draw.ellipse(goomba, GOOMBA_BROWN, (2, 4, 28, 20))
        # Feet
        pygame.draw.ellipse(goomba, (100, 50, 25), (2, 22, 12, 10))
        pygame.draw.ellipse(goomba, (100, 50, 25), (18, 22, 12, 10))
        # Eyes
        pygame.draw.ellipse(goomba, WHITE, (6, 8, 8, 10))
        pygame.draw.ellipse(goomba, WHITE, (18, 8, 8, 10))
        pygame.draw.ellipse(goomba, BLACK, (8, 12, 4, 6))
        pygame.draw.ellipse(goomba, BLACK, (20, 12, 4, 6))
        # Eyebrows
        pygame.draw.line(goomba, BLACK, (6, 6), (14, 10), 2)
        pygame.draw.line(goomba, BLACK, (26, 6), (18, 10), 2)
        return goomba
    
    def create_koopa_sprite(self):
        """Create Koopa enemy sprite"""
        koopa = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Shell
        pygame.draw.ellipse(koopa, KOOPA_GREEN, (4, 8, 24, 20))
        pygame.draw.ellipse(koopa, (0, 150, 0), (8, 12, 16, 12))
        # Head
        pygame.draw.ellipse(koopa, (255, 220, 180), (6, 0, 12, 12))
        # Eyes
        pygame.draw.circle(koopa, WHITE, (10, 4), 3)
        pygame.draw.circle(koopa, BLACK, (11, 4), 1)
        # Feet
        pygame.draw.ellipse(koopa, (255, 220, 180), (4, 26, 10, 6))
        pygame.draw.ellipse(koopa, (255, 220, 180), (18, 26, 10, 6))
        return koopa
    
    def create_flying_sprite(self):
        """Create flying enemy sprite (Paratroopa/Cheep)"""
        flying = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(flying, (255, 100, 100), (4, 8, 24, 18))
        # Wings
        pygame.draw.ellipse(flying, WHITE, (0, 4, 12, 8))
        pygame.draw.ellipse(flying, WHITE, (20, 4, 12, 8))
        # Eye
        pygame.draw.circle(flying, WHITE, (22, 14), 5)
        pygame.draw.circle(flying, BLACK, (24, 14), 2)
        # Tail
        pygame.draw.polygon(flying, (255, 100, 100), [(4, 16), (0, 12), (0, 20)])
        return flying


# ═══════════════════════════════════════════════════════════════
# PLAYER CLASS
# ═══════════════════════════════════════════════════════════════

class Player:
    def __init__(self, x, y, graphics):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        self.big = False
        self.dead = False
        self.won = False
        self.invincible = 0
        
        self.graphics = graphics
        self.sprite = graphics.create_mario_sprite(self.big)
        self.width = 24
        self.height = 32
        
        # Physics constants (NES-accurate-ish)
        self.gravity = 0.6
        self.max_fall = 12
        self.run_accel = 0.15
        self.run_decel = 0.1
        self.max_walk = 3
        self.max_run = 5
        self.jump_power = -12
        self.jump_hold = -0.4
    
    def update(self, keys, tiles, level_width, level_height):
        if self.dead or self.won:
            return
        
        # Horizontal movement
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        max_speed = self.max_run if running else self.max_walk
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= self.run_accel
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += self.run_accel
            self.facing_right = True
        else:
            # Deceleration
            if self.vx > 0:
                self.vx = max(0, self.vx - self.run_decel)
            elif self.vx < 0:
                self.vx = min(0, self.vx + self.run_decel)
        
        self.vx = max(-max_speed, min(max_speed, self.vx))
        
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
        
        # Variable jump height
        if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.vy < 0:
            self.vy += self.jump_hold
        
        # Gravity
        self.vy += self.gravity
        self.vy = min(self.vy, self.max_fall)
        
        # Movement with collision
        self.x += self.vx
        self.collide_horizontal(tiles)
        
        self.y += self.vy
        self.collide_vertical(tiles)
        
        # Screen bounds
        if self.x < 0:
            self.x = 0
            self.vx = 0
        if self.x > level_width - self.width:
            self.x = level_width - self.width
        
        # Death by falling
        if self.y > level_height:
            self.dead = True
        
        # Invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
    
    def collide_horizontal(self, tiles):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for tile in tiles:
            if rect.colliderect(tile):
                if self.vx > 0:
                    self.x = tile.left - self.width
                elif self.vx < 0:
                    self.x = tile.right
                self.vx = 0
                rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def collide_vertical(self, tiles):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = False
        for tile in tiles:
            if rect.colliderect(tile):
                if self.vy > 0:
                    self.y = tile.top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile.bottom
                    self.vy = 0
                rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen, camera_x):
        if self.dead:
            return
        if self.invincible > 0 and self.invincible % 4 < 2:
            return  # Blink
        
        sprite = self.sprite
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        screen.blit(sprite, (self.x - camera_x, self.y))


# ═══════════════════════════════════════════════════════════════
# ENEMY CLASS
# ═══════════════════════════════════════════════════════════════

class Enemy:
    def __init__(self, x, y, enemy_type, graphics):
        self.x = x
        self.y = y
        self.vx = -1.5  # Move left by default
        self.vy = 0
        self.type = enemy_type
        self.alive = True
        self.squished = False
        self.squish_timer = 0
        
        if enemy_type == 'E':
            self.sprite = graphics.create_goomba_sprite()
        elif enemy_type == 'K':
            self.sprite = graphics.create_koopa_sprite()
        elif enemy_type == 'W':
            self.sprite = graphics.create_flying_sprite()
            self.base_y = y
            self.fly_timer = random.random() * 6.28
        
        self.width = TILE_SIZE
        self.height = TILE_SIZE
    
    def update(self, tiles, level_height):
        if not self.alive:
            if self.squished:
                self.squish_timer -= 1
                if self.squish_timer <= 0:
                    return False
            return True
        
        if self.type == 'W':
            # Flying enemy - sine wave movement
            self.fly_timer += 0.08
            self.y = self.base_y + math.sin(self.fly_timer) * 30
            self.x += self.vx * 0.7
        else:
            # Ground enemy
            self.x += self.vx
            
            # Gravity
            self.vy += 0.5
            self.vy = min(self.vy, 10)
            self.y += self.vy
            
            # Collision with tiles
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            for tile in tiles:
                if rect.colliderect(tile):
                    if self.vy > 0:
                        self.y = tile.top - self.height
                        self.vy = 0
                    elif self.vx > 0:
                        self.x = tile.left - self.width
                        self.vx = -self.vx
                    elif self.vx < 0:
                        self.x = tile.right
                        self.vx = -self.vx
                    rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Fall death
        if self.y > level_height:
            return False
        
        return True
    
    def stomp(self):
        self.alive = False
        self.squished = True
        self.squish_timer = 30
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen, camera_x):
        if self.squished:
            # Draw squished sprite
            squished = pygame.transform.scale(self.sprite, (TILE_SIZE, TILE_SIZE // 4))
            screen.blit(squished, (self.x - camera_x, self.y + self.height - TILE_SIZE // 4))
        elif self.alive:
            screen.blit(self.sprite, (self.x - camera_x, self.y))


# ═══════════════════════════════════════════════════════════════
# GAME CLASS
# ═══════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros - Team Flames")
        self.clock = pygame.time.Clock()
        
        self.graphics = Graphics()
        
        self.state = 'menu'  # menu, debug, playing, gameover, victory
        self.current_world = '1-1'
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.debug_cursor = 0  # For debug menu level selection
        
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.tiles = []
        self.decorations = []
        self.enemies = []
        self.player = None
        self.camera_x = 0
        self.level_width = 0
        self.level_height = 0
        self.bg_color = SKY_BLUE
        
        self.flagpole_rect = None
        self.axe_rect = None
    
    def load_level(self, world_key):
        if world_key not in LEVELS:
            print(f"Level {world_key} not found, restarting at 1-1")
            world_key = '1-1'
        
        self.current_world = world_key
        level_data = LEVELS[world_key]
        self.bg_color = level_data['bg']
        raw_map = level_data['map']
        
        self.tiles = []
        self.decorations = []
        self.enemies = []
        self.flagpole_rect = None
        self.axe_rect = None
        
        self.level_width = len(raw_map[0]) * TILE_SIZE
        self.level_height = len(raw_map) * TILE_SIZE
        
        for r, row in enumerate(raw_map):
            for c, char in enumerate(row):
                x, y = c * TILE_SIZE, r * TILE_SIZE
                
                if char in ['B', '?', 'G', 'P', 'X', 'L']:
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    if char != 'L':  # Lava is deadly, not solid
                        self.tiles.append(rect)
                    texture = self.graphics.textures.get(char, None)
                    if texture:
                        self.decorations.append({'rect': rect, 'img': texture, 'type': char})
                
                elif char in ['E', 'K', 'W']:
                    enemy = Enemy(x, y, char, self.graphics)
                    self.enemies.append(enemy)
                
                elif char == 'F':
                    # Flagpole
                    self.flagpole_rect = pygame.Rect(x, y - TILE_SIZE * 8, 8, TILE_SIZE * 9)
                
                elif char == 'A':
                    # Axe (castle end)
                    self.axe_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.decorations.append({'rect': self.axe_rect, 'img': self.graphics.textures.get('A'), 'type': 'A'})
        
        # Find spawn position - scan for ground at start of level
        spawn_y = 0
        spawn_x = 48
        
        # For castle levels (starting with X border), find first platform
        first_row = raw_map[0] if raw_map else ""
        is_castle = first_row.startswith('X') and 'L' in ''.join(raw_map[-3:])  # Castle has X border AND lava
        
        if is_castle:
            # Castle levels: find first XXXXX platform (not border walls)
            for r in range(len(raw_map)):
                row = raw_map[r]
                # Look for platform pattern: space followed by X followed by space (platforms, not walls)
                for c in range(2, min(20, len(row) - 1)):
                    if row[c] == 'X' and c > 0:
                        # Check if this is a platform (has space above)
                        if r > 0 and raw_map[r-1][c] == ' ':
                            spawn_x = c * TILE_SIZE + 8
                            spawn_y = r * TILE_SIZE - 40
                            break
                if spawn_y > 0:
                    break
        else:
            # Regular levels: find ground tiles
            for r in range(len(raw_map) - 1, -1, -1):  # Scan from bottom up
                row = raw_map[r]
                for c in range(0, min(10, len(row))):
                    char = row[c] if c < len(row) else ' '
                    if char == 'G':
                        # Check if this is actual floor (has air above)
                        if r > 0:
                            above_char = raw_map[r-1][c] if c < len(raw_map[r-1]) else ' '
                            if above_char == ' ' or above_char == 'E' or above_char == 'K':
                                ground_y = r * TILE_SIZE
                                spawn_y = ground_y - 48
                                spawn_x = c * TILE_SIZE + 4
                                break
                if spawn_y > 0:
                    break
        
        # Fallback - find any ground tile
        if spawn_y <= 0 or spawn_y > self.level_height - 100:
            for r, row in enumerate(raw_map):
                for c, char in enumerate(row):
                    if char == 'G':
                        spawn_y = r * TILE_SIZE - 48
                        spawn_x = c * TILE_SIZE + 4
                        break
                if spawn_y > 0 and spawn_y < self.level_height - 100:
                    break
        
        # Final fallback for castle levels
        if spawn_y <= 0 or spawn_y > self.level_height - 100:
            spawn_y = TILE_SIZE * 9 - 40  # Row 9 typically has platforms
            spawn_x = TILE_SIZE * 3
        
        self.player = Player(spawn_x, spawn_y, self.graphics)
        self.camera_x = 0
    
    def check_enemy_collision(self):
        if self.player.dead or self.player.won:
            return
        
        player_rect = self.player.get_rect()
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            enemy_rect = enemy.get_rect()
            if player_rect.colliderect(enemy_rect):
                # Check if stomping
                if self.player.vy > 0 and player_rect.bottom < enemy_rect.centery + 8:
                    enemy.stomp()
                    self.player.vy = -8  # Bounce
                    self.score += 100
                else:
                    # Player hit
                    if self.player.invincible <= 0:
                        if self.player.big:
                            self.player.big = False
                            self.player.height = 32
                            self.player.sprite = self.graphics.create_mario_sprite(False)
                            self.player.invincible = 120
                        else:
                            self.player.dead = True
    
    def check_hazards(self):
        """Check for lava and pit deaths"""
        if self.player.dead:
            return
        
        player_rect = self.player.get_rect()
        
        for deco in self.decorations:
            if deco['type'] == 'L':
                if player_rect.colliderect(deco['rect']):
                    self.player.dead = True
                    return
    
    def check_flagpole(self):
        """Check if player reached flagpole or axe"""
        if self.player.dead or self.player.won:
            return
        
        player_rect = self.player.get_rect()
        
        if self.flagpole_rect and player_rect.colliderect(self.flagpole_rect):
            self.player.won = True
            self.score += 500
        
        if self.axe_rect and player_rect.colliderect(self.axe_rect):
            self.player.won = True
            self.score += 1000
    
    def run_menu(self):
        """Main menu screen"""
        self.screen.fill((0, 0, 0))
        
        # Title
        title = self.font_large.render("SUPER MARIO BROS", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
        
        subtitle = self.font_small.render("Team Flames / Samsoft", True, (150, 150, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 120))
        
        # Draw Mario
        mario = self.graphics.create_mario_sprite(True)
        mario_big = pygame.transform.scale(mario, (72, 144))
        self.screen.blit(mario_big, (SCREEN_WIDTH//2 - 36, 150))
        
        # Menu buttons with boxes
        button_y = 310
        button_width = 300
        button_height = 40
        
        # Start Game Button
        start_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (60, 60, 60), start_rect)
        pygame.draw.rect(self.screen, WHITE, start_rect, 3)
        start_text = self.font_small.render("[ENTER] Start Game", True, WHITE)
        self.screen.blit(start_text, (start_rect.centerx - start_text.get_width()//2, start_rect.centery - start_text.get_height()//2))
        
        # World Select Button  
        button_y += 55
        world_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (60, 60, 60), world_rect)
        pygame.draw.rect(self.screen, YELLOW, world_rect, 3)
        world_text = self.font_small.render(f"[1-8] World Select: {self.current_world[0]}", True, YELLOW)
        self.screen.blit(world_text, (world_rect.centerx - world_text.get_width()//2, world_rect.centery - world_text.get_height()//2))
        
        # Debug Menu Button
        button_y += 55
        debug_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (60, 60, 60), debug_rect)
        pygame.draw.rect(self.screen, (100, 200, 100), debug_rect, 3)
        debug_text = self.font_small.render("[D] Level Select (Debug)", True, (100, 200, 100))
        self.screen.blit(debug_text, (debug_rect.centerx - debug_text.get_width()//2, debug_rect.centery - debug_text.get_height()//2))
        
        # Controls
        controls = self.font_small.render("Arrow/WASD: Move | Space/Z: Jump | Shift/X: Run", True, (150, 150, 150))
        self.screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, 470))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.lives = 3
                    self.score = 0
                    self.load_level(self.current_world)
                    self.state = 'playing'
                elif event.key == pygame.K_d:
                    self.debug_cursor = LEVEL_ORDER.index(self.current_world) if self.current_world in LEVEL_ORDER else 0
                    self.state = 'debug'
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                   pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]:
                    world_num = event.key - pygame.K_0
                    self.current_world = f'{world_num}-1'
        
        return True
    
    def run_debug(self):
        """Debug level select menu"""
        self.screen.fill((20, 20, 40))
        
        # Title
        title = self.font_large.render("LEVEL SELECT", True, (100, 200, 100))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        subtitle = self.font_small.render("Debug Menu - Use Arrow Keys + Enter", True, (150, 150, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 70))
        
        # Draw level grid (8 worlds x 4 levels)
        start_x = 80
        start_y = 120
        box_width = 80
        box_height = 60
        gap_x = 10
        gap_y = 10
        
        for i, level_key in enumerate(LEVEL_ORDER):
            world = int(level_key[0])
            stage = int(level_key[2])
            
            col = world - 1
            row = stage - 1
            
            x = start_x + col * (box_width + gap_x)
            y = start_y + row * (box_height + gap_y)
            
            # Determine box color based on level type
            if stage == 4:
                box_color = (80, 40, 40)  # Castle - dark red
                border_color = (200, 100, 100)
            elif stage == 2:
                box_color = (40, 40, 60)  # Underground - dark blue
                border_color = (100, 100, 200)
            elif stage == 3:
                box_color = (40, 60, 40)  # Athletic - dark green
                border_color = (100, 200, 100)
            else:
                box_color = (40, 60, 80)  # Overworld - blue
                border_color = (100, 150, 200)
            
            rect = pygame.Rect(x, y, box_width, box_height)
            pygame.draw.rect(self.screen, box_color, rect)
            
            # Highlight selected level
            if i == self.debug_cursor:
                pygame.draw.rect(self.screen, YELLOW, rect, 4)
            else:
                pygame.draw.rect(self.screen, border_color, rect, 2)
            
            # Level text
            level_text = self.font_small.render(level_key, True, WHITE)
            self.screen.blit(level_text, (x + box_width//2 - level_text.get_width()//2, 
                                          y + box_height//2 - level_text.get_height()//2))
        
        # World labels at top
        for w in range(1, 9):
            label = self.font_small.render(f"W{w}", True, (150, 150, 150))
            x = start_x + (w - 1) * (box_width + gap_x) + box_width//2 - label.get_width()//2
            self.screen.blit(label, (x, start_y - 25))
        
        # Selected level info
        selected = LEVEL_ORDER[self.debug_cursor]
        info_text = self.font_medium.render(f"Selected: World {selected}", True, YELLOW)
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 400))
        
        # Controls
        controls1 = self.font_small.render("[Arrow Keys] Navigate | [Enter] Play Level", True, WHITE)
        self.screen.blit(controls1, (SCREEN_WIDTH//2 - controls1.get_width()//2, 440))
        
        controls2 = self.font_small.render("[ESC] Back to Menu", True, (150, 150, 150))
        self.screen.blit(controls2, (SCREEN_WIDTH//2 - controls2.get_width()//2, 465))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = 'menu'
                elif event.key == pygame.K_RETURN:
                    self.current_world = LEVEL_ORDER[self.debug_cursor]
                    self.lives = 3
                    self.score = 0
                    self.load_level(self.current_world)
                    self.state = 'playing'
                elif event.key == pygame.K_UP:
                    # Move up one stage (subtract 1, wrap within world)
                    if self.debug_cursor % 4 > 0:
                        self.debug_cursor -= 1
                elif event.key == pygame.K_DOWN:
                    # Move down one stage
                    if self.debug_cursor % 4 < 3:
                        self.debug_cursor += 1
                elif event.key == pygame.K_LEFT:
                    # Move to previous world
                    if self.debug_cursor >= 4:
                        self.debug_cursor -= 4
                elif event.key == pygame.K_RIGHT:
                    # Move to next world
                    if self.debug_cursor < len(LEVEL_ORDER) - 4:
                        self.debug_cursor += 4
        
        return True
    
    def run_playing(self):
        """Main gameplay"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = 'menu'
        
        keys = pygame.key.get_pressed()
        
        # Update
        self.player.update(keys, self.tiles, self.level_width, self.level_height)
        
        # Update enemies
        self.enemies = [e for e in self.enemies if e.update(self.tiles, self.level_height)]
        
        # Collisions
        self.check_enemy_collision()
        self.check_hazards()
        self.check_flagpole()
        
        # Camera follow
        target_camera = self.player.x - SCREEN_WIDTH // 3
        self.camera_x = max(0, min(target_camera, self.level_width - SCREEN_WIDTH))
        
        # Check death
        if self.player.dead:
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'gameover'
            else:
                # Respawn
                self.load_level(self.current_world)
        
        # Check victory
        if self.player.won:
            next_level = get_next_level(self.current_world)
            if next_level:
                self.current_world = next_level
                self.load_level(next_level)
            else:
                self.state = 'victory'
        
        # Draw
        self.screen.fill(self.bg_color)
        
        # Draw decorations/tiles
        for deco in self.decorations:
            if deco['rect'].x - self.camera_x > -TILE_SIZE and deco['rect'].x - self.camera_x < SCREEN_WIDTH + TILE_SIZE:
                if deco['img']:
                    self.screen.blit(deco['img'], (deco['rect'].x - self.camera_x, deco['rect'].y))
        
        # Draw flagpole
        if self.flagpole_rect:
            pygame.draw.rect(self.screen, GREEN, 
                           (self.flagpole_rect.x - self.camera_x, self.flagpole_rect.y,
                            self.flagpole_rect.width, self.flagpole_rect.height))
            # Flag
            pygame.draw.polygon(self.screen, RED, [
                (self.flagpole_rect.x - self.camera_x + 8, self.flagpole_rect.y),
                (self.flagpole_rect.x - self.camera_x + 40, self.flagpole_rect.y + 20),
                (self.flagpole_rect.x - self.camera_x + 8, self.flagpole_rect.y + 40)
            ])
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # Draw player
        self.player.draw(self.screen, self.camera_x)
        
        # HUD
        hud_text = self.font_small.render(f"WORLD {self.current_world}  LIVES: {self.lives}  SCORE: {self.score}", True, WHITE)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (0, 0, SCREEN_WIDTH, 40))
        self.screen.blit(hud_text, (20, 10))
        
        pygame.display.flip()
        return True
    
    def run_gameover(self):
        """Game over screen"""
        self.screen.fill(BLACK)
        
        text = self.font_large.render("GAME OVER", True, RED)
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 180))
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 280))
        
        restart = self.font_small.render("Press ENTER to return to menu", True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 380))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.current_world = '1-1'
                    self.state = 'menu'
        
        return True
    
    def run_victory(self):
        """Victory screen"""
        self.screen.fill(BLACK)
        
        text = self.font_large.render("CONGRATULATIONS!", True, YELLOW)
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 120))
        
        text2 = self.font_medium.render("You saved the Princess!", True, WHITE)
        self.screen.blit(text2, (SCREEN_WIDTH//2 - text2.get_width()//2, 200))
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 280))
        
        # Draw big Mario and Princess (simple)
        mario = self.graphics.create_mario_sprite(True)
        mario_big = pygame.transform.scale(mario, (48, 96))
        self.screen.blit(mario_big, (SCREEN_WIDTH//2 - 80, 320))
        
        # Simple princess
        princess = pygame.Surface((32, 64), pygame.SRCALPHA)
        pygame.draw.ellipse(princess, (255, 200, 200), (8, 0, 16, 16))  # Head
        pygame.draw.rect(princess, (255, 100, 150), (4, 16, 24, 40))    # Dress
        pygame.draw.polygon(princess, YELLOW, [(12, 0), (16, -8), (20, 0)])  # Crown
        princess_big = pygame.transform.scale(princess, (48, 96))
        self.screen.blit(princess_big, (SCREEN_WIDTH//2 + 32, 320))
        
        restart = self.font_small.render("Press ENTER to return to menu", True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 440))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.current_world = '1-1'
                    self.state = 'menu'
        
        return True
    
    def run(self):
        running = True
        while running:
            if self.state == 'menu':
                running = self.run_menu()
            elif self.state == 'debug':
                running = self.run_debug()
            elif self.state == 'playing':
                running = self.run_playing()
            elif self.state == 'gameover':
                running = self.run_gameover()
            elif self.state == 'victory':
                running = self.run_victory()
            
            self.clock.tick(FPS)
        
        pygame.quit()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    game = Game()
    game.run()

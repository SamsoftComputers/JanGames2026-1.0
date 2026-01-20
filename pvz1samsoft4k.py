import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 1000, 750
GRID_X, GRID_Y = 220, 100
CELL_SIZE_X, CELL_SIZE_Y = 80, 100
COLS, ROWS = 9, 5

# Colors
SKY_BLUE = (135, 206, 235)
NIGHT_BLUE = (20, 20, 80)
GRASS_GREEN = (34, 139, 34)
DARK_GRASS_GREEN = (0, 100, 0)
PEA_GREEN = (124, 252, 0)
SNOW_BLUE = (176, 224, 230)
SUN_YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (200, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
SILVER = (192, 192, 192)
PINK = (255, 105, 180)
FIRE_RED = (255, 69, 0)

# Plant Data
PLANT_DATA = {
    'peashooter': {'cost': 100, 'cooldown': 450, 'unlock_level': 0},
    'sunflower': {'cost': 50, 'cooldown': 450, 'unlock_level': 1},
    'cherrybomb': {'cost': 150, 'cooldown': 2000, 'unlock_level': 2},
    'wallnut': {'cost': 50, 'cooldown': 1800, 'unlock_level': 3},
    'potatomine': {'cost': 25, 'cooldown': 1800, 'unlock_level': 4},
    'snowpea': {'cost': 175, 'cooldown': 450, 'unlock_level': 5},
    'chomper': {'cost': 150, 'cooldown': 450, 'unlock_level': 6},
    'repeater': {'cost': 200, 'cooldown': 450, 'unlock_level': 7},
    'puffshroom': {'cost': 0, 'cooldown': 300, 'unlock_level': 8},
    'squash': {'cost': 50, 'cooldown': 1800, 'unlock_level': 9},
    'threepeater': {'cost': 325, 'cooldown': 450, 'unlock_level': 10},
    'jalapeno': {'cost': 125, 'cooldown': 2000, 'unlock_level': 11}
}

# Fonts
font_sm = pygame.font.SysFont("Arial", 14, bold=True)
font_md = pygame.font.SysFont("Arial", 20, bold=True)
font_lg = pygame.font.SysFont("Arial", 36, bold=True)
font_xl = pygame.font.SysFont("Arial", 72, bold=True)

class Sun:
    def __init__(self, x, y, falling=False, target_y=None):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.falling = falling
        self.target_y = target_y if target_y else random.randint(GRID_Y + 50, HEIGHT - 100)
        self.timer = 0
        self.value = 25

    def update(self):
        if self.falling and self.rect.y < self.target_y:
            self.rect.y += 3
        self.timer += 1
        return self.timer > 800

    def draw(self, surface):
        angle = (pygame.time.get_ticks() // 10) % 360
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(surf, ORANGE, (30, 30), 25)
        pygame.draw.circle(surf, SUN_YELLOW, (30, 30), 20)
        surface.blit(surf, (self.rect.x - 5, self.rect.y - 5))

class Projectile:
    def __init__(self, row, x, ptype='pea', dy=0):
        self.row = row
        self.x = x
        self.y = GRID_Y + row * CELL_SIZE_Y + 40
        self.type = ptype
        self.dy = dy
        self.radius = 10
        self.speed = 8
        self.active = True

    def update(self, game):
        self.x += self.speed
        self.y += self.dy
        
        if self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
            return

        rect = pygame.Rect(self.x - 10, self.y - 10, 20, 20)
        for z in game.zombies:
            row_hit = z.row == self.row
            if self.dy != 0:
                row_hit = abs(z.rect.centery - self.y) < 50

            if row_hit and z.x < WIDTH and z.rect.colliderect(rect):
                damage = 20
                if self.type == 'snowpea':
                    z.apply_slow()
                z.take_damage(damage)
                self.active = False
                break

    def draw(self, surface):
        color = SNOW_BLUE if self.type == 'snowpea' else PEA_GREEN
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 10)
        pygame.draw.circle(surface, WHITE, (int(self.x-3), int(self.y-3)), 3)

class LawnMower:
    def __init__(self, row):
        self.row = row
        self.x = GRID_X - 50
        self.y = GRID_Y + row * CELL_SIZE_Y + 40
        self.active = True
        self.moving = False
        self.rect = pygame.Rect(self.x, self.y, 50, 40)

    def update(self, game):
        if not self.active: return
        if self.moving:
            self.x += 12
            self.rect.x = int(self.x)
            for z in game.zombies:
                if z.row == self.row and self.rect.colliderect(z.rect):
                    z.take_damage(9999)
            if self.x > WIDTH: self.active = False
        else:
            for z in game.zombies:
                if z.row == self.row and z.x < self.x + 40:
                    self.moving = True

    def draw(self, surface):
        if not self.active: return
        pygame.draw.rect(surface, RED, self.rect)
        pygame.draw.circle(surface, BLACK, (int(self.x+10), int(self.y+40)), 10)
        pygame.draw.circle(surface, BLACK, (int(self.x+40), int(self.y+40)), 10)
        pygame.draw.rect(surface, BLACK, (self.x-10, self.y-20, 10, 50))

class Plant:
    def __init__(self, row, col, ptype):
        self.row = row
        self.col = col
        self.type = ptype
        self.x = GRID_X + col * CELL_SIZE_X + 10
        self.y = GRID_Y + row * CELL_SIZE_Y + 10
        self.rect = pygame.Rect(self.x, self.y, 60, 80)
        self.health = 300
        self.max_health = 300
        self.timer = 0
        self.state = 'idle'

        if ptype == 'wallnut':
            self.health = 4000; self.max_health = 4000
        elif ptype == 'potatomine':
            self.health = 300
        elif ptype == 'chomper':
            self.health = 300
        elif ptype == 'jalapeno':
            self.health = 1000
        
    def update(self, game):
        self.timer += 1
        
        if self.type in ['peashooter', 'snowpea', 'repeater', 'threepeater']:
            rate = 90
            if self.timer >= rate:
                should_shoot = False
                if self.type == 'threepeater':
                    rows_to_check = [r for r in [self.row-1, self.row, self.row+1] if 0 <= r < ROWS]
                    if any(z.row in rows_to_check and z.x > self.x for z in game.zombies):
                        should_shoot = True
                else:
                    if any(z.row == self.row and z.x > self.x for z in game.zombies):
                        should_shoot = True
                
                if should_shoot:
                    p_type = 'snowpea' if self.type == 'snowpea' else 'pea'
                    
                    if self.type == 'threepeater':
                        for r_offset, dy in [(-1, -1), (0, 0), (1, 1)]:
                            if 0 <= self.row + r_offset < ROWS:
                                game.projectiles.append(Projectile(self.row + r_offset, self.x + 40, p_type, dy=dy))
                    else:
                        game.projectiles.append(Projectile(self.row, self.x + 40, p_type))
                        if self.type == 'repeater':
                            game.projectiles.append(Projectile(self.row, self.x + 20, p_type))
                    
                    self.timer = 0

        elif self.type == 'puffshroom':
            if self.timer >= 90:
                if any(z.row == self.row and self.x < z.x < self.x + 250 for z in game.zombies):
                    game.projectiles.append(Projectile(self.row, self.x + 40, 'pea'))
                    self.timer = 0

        elif self.type == 'sunflower':
            if self.timer >= 1440:
                game.suns.append(Sun(self.x, self.y, falling=False))
                self.timer = 0

        elif self.type == 'cherrybomb':
            if self.timer >= 60:
                cx, cy = self.rect.center
                for z in game.zombies[:]:
                    if math.hypot(z.rect.centerx - cx, z.rect.centery - cy) < 180:
                        z.take_damage(1800)
                game.plants.remove(self)

        elif self.type == 'jalapeno':
            if self.timer >= 45:
                for z in game.zombies[:]:
                    if z.row == self.row:
                        z.take_damage(9999)
                game.plants.remove(self)

        elif self.type == 'potatomine':
            if self.state == 'idle' and self.timer >= 900:
                self.state = 'armed'
            if self.state == 'armed':
                for z in game.zombies:
                    if z.row == self.row and abs(z.rect.centerx - self.rect.centerx) < 40:
                        z.take_damage(1800)
                        game.plants.remove(self)
                        break

        elif self.type == 'squash':
            for z in game.zombies:
                if z.row == self.row and 0 < z.x - self.x < 80:
                    z.take_damage(1800)
                    game.plants.remove(self)
                    break

        elif self.type == 'chomper':
            if self.state == 'idle':
                for z in game.zombies:
                    if z.row == self.row and 0 < z.x - self.x < 120 and z.type != 'gargantuar':
                        game.zombies.remove(z)
                        self.state = 'chewing'
                        self.timer = 0
                        break
            elif self.state == 'chewing':
                if self.timer >= 2400:
                    self.state = 'idle'
                    self.timer = 0

    def draw(self, surface):
        pygame.draw.ellipse(surface, (0,0,0,100), (self.x+10, self.y+70, 40, 15))
        
        if self.type in ['peashooter', 'repeater', 'snowpea', 'threepeater']:
            count = 3 if self.type == 'threepeater' else 1
            col = SNOW_BLUE if self.type == 'snowpea' else PEA_GREEN
            
            for i in range(count):
                off_y = 0
                if count == 3: off_y = (i-1) * 20
                pygame.draw.circle(surface, col, (self.x+30, self.y+20+off_y), 20)
                pygame.draw.rect(surface, DARK_GRASS_GREEN, (self.x+40, self.y+10+off_y, 20, 20))
                if self.type == 'repeater':
                    pygame.draw.line(surface, BLACK, (self.x+15, self.y+10+off_y), (self.x+35, self.y+15+off_y), 3)

        elif self.type == 'sunflower':
            pygame.draw.circle(surface, ORANGE, (self.x+30, self.y+30), 25)
            pygame.draw.circle(surface, BROWN, (self.x+30, self.y+30), 20)
            for i in range(0, 360, 45):
                rad = math.radians(i)
                pygame.draw.circle(surface, SUN_YELLOW, (int(self.x+30+math.cos(rad)*25), int(self.y+30+math.sin(rad)*25)), 8)

        elif self.type == 'wallnut':
            c = BROWN
            if self.health < 2000: c = (120, 80, 40)
            if self.health < 1000: c = (100, 60, 30)
            pygame.draw.rect(surface, c, (self.x+10, self.y+10, 40, 60), border_radius=15)
            pygame.draw.circle(surface, WHITE, (self.x+20, self.y+25), 8)
            pygame.draw.circle(surface, WHITE, (self.x+40, self.y+25), 8)
            pygame.draw.circle(surface, BLACK, (self.x+22, self.y+25), 3)
            pygame.draw.circle(surface, BLACK, (self.x+38, self.y+25), 3)

        elif self.type == 'potatomine':
            if self.state == 'armed': pygame.draw.circle(surface, RED, (self.x+30, self.y+40), 5)
            pygame.draw.ellipse(surface, (160, 100, 50), (self.x+10, self.y+50, 40, 30))

        elif self.type == 'cherrybomb':
            pygame.draw.circle(surface, RED, (self.x+15, self.y+50), 20)
            pygame.draw.circle(surface, RED, (self.x+45, self.y+45), 20)
            pygame.draw.lines(surface, GRASS_GREEN, False, [(self.x+15, self.y+30), (self.x+30, self.y+10), (self.x+45, self.y+25)], 3)

        elif self.type == 'chomper':
            color = PURPLE
            if self.state == 'chewing': color = (80, 0, 80)
            pygame.draw.circle(surface, color, (self.x+30, self.y+20), 25)
            pygame.draw.rect(surface, color, (self.x+20, self.y+40, 20, 30))
            pygame.draw.polygon(surface, WHITE, [(self.x+30, self.y), (self.x+50, self.y-10), (self.x+50, self.y+10)])
            
        elif self.type == 'squash':
            pygame.draw.rect(surface, GRASS_GREEN, (self.x+10, self.y+10, 40, 50), border_radius=10)
            pygame.draw.line(surface, BLACK, (self.x+20, self.y+30), (self.x+40, self.y+30), 2)
            pygame.draw.circle(surface, WHITE, (self.x+20, self.y+20), 5)
            pygame.draw.circle(surface, WHITE, (self.x+40, self.y+20), 5)

        elif self.type == 'jalapeno':
            pygame.draw.ellipse(surface, FIRE_RED, (self.x+15, self.y+10, 30, 60))
            pygame.draw.rect(surface, DARK_GRASS_GREEN, (self.x+25, self.y+5, 10, 10))
            pygame.draw.line(surface, BLACK, (self.x+20, self.y+25), (self.x+25, self.y+30), 2)
            pygame.draw.line(surface, BLACK, (self.x+40, self.y+25), (self.x+35, self.y+30), 2)
            pygame.draw.line(surface, BLACK, (self.x+25, self.y+50), (self.x+35, self.y+50), 2)

        elif self.type == 'puffshroom':
            pygame.draw.circle(surface, PURPLE, (self.x+30, self.y+40), 15)
            pygame.draw.rect(surface, WHITE, (self.x+25, self.y+40, 10, 20))

class Zombie:
    def __init__(self, row, ztype='basic'):
        self.row = row
        self.x = WIDTH + random.randint(10, 100)
        self.y = GRID_Y + row * CELL_SIZE_Y + 10
        self.rect = pygame.Rect(self.x, self.y, 50, 90)
        self.type = ztype
        
        self.max_health = 200
        self.speed = 0.5
        self.eating = False
        self.slow_timer = 0
        self.vaulted = False
        self.has_newspaper = False
        
        if ztype == 'conehead': self.max_health = 560
        elif ztype == 'buckethead': self.max_health = 1300
        elif ztype == 'newspaper': 
            self.max_health = 420; self.speed = 0.6; self.has_newspaper = True
        elif ztype == 'football':
            self.max_health = 1600; self.speed = 1.2
        elif ztype == 'polevault':
            self.max_health = 340; self.speed = 1.5
        
        self.health = self.max_health

    def update(self, game):
        cur_speed = self.speed
        if self.slow_timer > 0:
            cur_speed *= 0.5
            self.slow_timer -= 1
        
        if self.type == 'newspaper' and self.has_newspaper and self.health < 150:
            self.has_newspaper = False
            self.speed = 2.0

        if self.type == 'polevault' and not self.vaulted:
            for p in game.plants:
                if p.row == self.row and 0 < p.x - self.x < 40:
                    self.x += 100
                    self.vaulted = True
                    self.speed = 0.5
                    break

        if not self.eating:
            self.x -= cur_speed
            self.rect.x = int(self.x)

        self.eating = False
        hitbox = pygame.Rect(self.x, self.y, 40, 90)
        for p in game.plants:
            if p.row == self.row and hitbox.colliderect(p.rect):
                if self.type == 'polevault' and not self.vaulted:
                    pass 
                else:
                    self.eating = True
                    p.health -= 1
                    if p.health <= 0:
                        game.plants.remove(p)
                    break
        
        return self.x < GRID_X - 50

    def take_damage(self, amt):
        self.health -= amt

    def apply_slow(self):
        self.slow_timer = 120

    def draw(self, surface):
        color = (100, 150, 100)
        if self.slow_timer > 0: color = (100, 100, 200)
        
        if self.type == 'football': color = (200, 50, 50) 
        
        off_x = math.sin(pygame.time.get_ticks()/100) * 2
        
        pygame.draw.rect(surface, color, (self.x+off_x, self.y, 50, 90))
        pygame.draw.circle(surface, color, (int(self.x+25+off_x), int(self.y)), 20)
        
        if self.type == 'conehead' and self.health > 200:
            pygame.draw.polygon(surface, ORANGE, [(self.x+5, self.y-15), (self.x+45, self.y-15), (self.x+25, self.y-55)])
        elif self.type == 'buckethead' and self.health > 200:
            pygame.draw.rect(surface, SILVER, (self.x+5, self.y-40, 40, 30))
        elif self.type == 'football':
            pygame.draw.circle(surface, RED, (int(self.x+25), int(self.y)), 22)
            pygame.draw.line(surface, WHITE, (self.x+25, self.y-20), (self.x+25, self.y+20), 2)
        elif self.type == 'polevault':
            if not self.vaulted:
                pygame.draw.line(surface, PINK, (self.x+10, self.y+90), (self.x-20, self.y-50), 4)
        elif self.type == 'newspaper' and self.has_newspaper:
            pygame.draw.rect(surface, WHITE, (self.x+10, self.y+30, 30, 40))

class Game:
    def __init__(self):
        self.state = 'intro_samsoft'
        self.intro_timer = 0
        self.level = 1
        self.unlocked_plants = ['peashooter']
        self.reset_level()
        
    def reset_level(self):
        self.plants = []
        self.zombies = []
        self.projectiles = []
        self.suns = [Sun(300, 0, falling=True), Sun(400, -100, falling=True)]
        self.lawn_mowers = [LawnMower(i) for i in range(ROWS)]
        self.sun = 50
        
        self.wave_timer = 0
        self.current_wave = 0
        self.zombies_spawned_in_wave = 0
        self.huge_wave_approaching = False
        self.huge_wave_timer = 0
        
        self.waves_in_level = 10
        if self.level > 1: self.waves_in_level = 10 + self.level * 2
        
        self.selected_plant = None
        self.shovel_active = False
        self.ticks = 0
        self.plant_cooldowns = {name: -9999 for name in PLANT_DATA}
        
        self.night = self.level in [4, 5, 6]

    def get_available_plants(self):
        avail = [p for p in PLANT_DATA if PLANT_DATA[p]['unlock_level'] < self.level]
        return sorted(avail, key=lambda x: PLANT_DATA[x]['cost'])

    def spawn_zombie(self, huge_wave=False):
        rows = list(range(ROWS))
        r = random.choice(rows)
        
        types = ['basic']
        if self.level > 1: types.append('conehead')
        if self.level > 2: types.append('buckethead')
        if self.level > 3: types.append('polevault')
        if self.level > 4: types.append('newspaper')
        if self.level > 6: types.append('football')
        
        w = [10, 4, 3, 2, 2, 1][:len(types)]
        z_type = random.choices(types, weights=w, k=1)[0]
        
        self.zombies.append(Zombie(r, z_type))

    def update(self):
        if self.state.startswith('intro'):
            self.intro_timer += 1
            if self.intro_timer > 120:
                if self.state == 'intro_samsoft': self.state = 'intro_popcap'
                elif self.state == 'intro_popcap': self.state = 'intro_ea'
                elif self.state == 'intro_ea': self.state = 'menu'
                self.intro_timer = 0
            return

        if self.state == 'menu': return
        if self.state == 'victory': return
        if self.state == 'game_over': return

        self.ticks += 1
        
        if self.current_wave >= self.waves_in_level and len(self.zombies) == 0:
            self.state = 'victory'
            for p, data in PLANT_DATA.items():
                if data['unlock_level'] == self.level:
                    if p not in self.unlocked_plants:
                        self.unlocked_plants.append(p)
            return

        if not self.huge_wave_approaching and self.current_wave < self.waves_in_level:
            self.wave_timer += 1
            
            spawn_delay = max(60, 600 - (self.level * 30))
            if self.wave_timer > spawn_delay:
                self.spawn_zombie()
                self.wave_timer = 0
                self.current_wave += 0.5
                
                if int(self.current_wave) == int(self.waves_in_level / 2) and self.zombies_spawned_in_wave == 0:
                    self.huge_wave_approaching = True
                    self.huge_wave_timer = 180
                    self.zombies_spawned_in_wave = 1

        if self.huge_wave_approaching:
            self.huge_wave_timer -= 1
            if self.huge_wave_timer <= 0:
                self.huge_wave_approaching = False
                count = 5 + self.level
                for _ in range(count):
                    self.spawn_zombie()

        sun_freq = 1200 if self.night else 400
        if self.ticks % sun_freq == 0:
            self.suns.append(Sun(random.randint(GRID_X, WIDTH-50), 0, falling=True))

        for p in self.plants: p.update(self)
        for m in self.lawn_mowers: m.update(self)
        for pr in self.projectiles[:]: 
            pr.update(self)
            if not pr.active: self.projectiles.remove(pr)
        for s in self.suns[:]: 
            if s.update(): self.suns.remove(s)
        
        for z in self.zombies[:]:
            if z.update(self):
                self.state = 'game_over'
            if z.health <= 0:
                self.zombies.remove(z)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            if self.state.startswith('intro'):
                self.state = 'menu'
                return

            if self.state == 'menu':
                if WIDTH//2-100 < mx < WIDTH//2+100 and HEIGHT//2-30 < my < HEIGHT//2+30:
                    self.state = 'playing'
                    self.level = 1
                    self.reset_level()
                return

            if self.state == 'victory':
                if WIDTH//2-100 < mx < WIDTH//2+100 and HEIGHT//2+50 < my < HEIGHT//2+100:
                    self.level += 1
                    self.state = 'playing'
                    self.reset_level()
                return
            
            if self.state == 'game_over':
                self.state = 'menu'
                return

            for s in self.suns[:]:
                if s.rect.collidepoint(mx, my):
                    self.suns.remove(s)
                    self.sun += s.value
                    return
            
            if 140 < mx < 200 and 10 < my < 70:
                self.shovel_active = not self.shovel_active
                self.selected_plant = None
                return

            available = self.get_available_plants()
            if mx < GRID_X:
                idx = 0
                for p_name in available:
                    r = pygame.Rect(10, 80 + idx*70, 190, 60)
                    if r.collidepoint(mx, my):
                        cost = PLANT_DATA[p_name]['cost']
                        cd = PLANT_DATA[p_name]['cooldown']
                        on_cd = (self.ticks - self.plant_cooldowns[p_name]) < cd
                        
                        if self.sun >= cost and not on_cd:
                            self.selected_plant = p_name
                            self.shovel_active = False
                    idx += 1
                return

            if GRID_X < mx < WIDTH and GRID_Y < my < HEIGHT:
                c = (mx - GRID_X) // CELL_SIZE_X
                r = (my - GRID_Y) // CELL_SIZE_Y
                
                if 0 <= c < COLS and 0 <= r < ROWS:
                    existing = None
                    for p in self.plants:
                        if p.row == r and p.col == c:
                            existing = p
                            break
                    
                    if self.shovel_active:
                        if existing:
                            self.plants.remove(existing)
                            self.shovel_active = False
                    
                    elif self.selected_plant:
                        if not existing:
                            cost = PLANT_DATA[self.selected_plant]['cost']
                            self.plants.append(Plant(r, c, self.selected_plant))
                            self.sun -= cost
                            self.plant_cooldowns[self.selected_plant] = self.ticks
                            self.selected_plant = None

    def draw(self, surface):
        if self.state.startswith('intro'):
            surface.fill(BLACK)
            txt = font_xl.render(self.state.split('_')[1].upper(), True, WHITE)
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
            return

        if self.state == 'menu':
            surface.fill(BLACK)
            t = font_xl.render("PLANTS vs ZOMBIES", True, PEA_GREEN)
            surface.blit(t, (WIDTH//2 - t.get_width()//2, 150))
            btn = pygame.Rect(WIDTH//2-120, HEIGHT//2-30, 240, 60)
            pygame.draw.rect(surface, GRASS_GREEN, btn, border_radius=10)
            pygame.draw.rect(surface, WHITE, btn, 3, border_radius=10)
            bt = font_lg.render("ADVENTURE", True, WHITE)
            surface.blit(bt, (WIDTH//2 - bt.get_width()//2, HEIGHT//2 - 20))
            return

        bg_col = NIGHT_BLUE if self.night else SKY_BLUE
        surface.fill(bg_col)
        
        pygame.draw.rect(surface, (80, 50, 20), (0,0, GRID_X, HEIGHT))
        
        lawn_col = (20, 100, 20) if self.night else GRASS_GREEN
        alt_col = (10, 80, 10) if self.night else (40, 140, 40)
        
        for r in range(ROWS):
            for c in range(COLS):
                color = lawn_col if (r+c)%2==0 else alt_col
                pygame.draw.rect(surface, color, (GRID_X+c*CELL_SIZE_X, GRID_Y+r*CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))
        
        for m in self.lawn_mowers: m.draw(surface)
        for p in self.plants: p.draw(surface)
        for z in self.zombies: z.draw(surface)
        for proj in self.projectiles: proj.draw(surface)
        for s in self.suns: s.draw(surface)

        if self.huge_wave_approaching:
            t = font_xl.render("A HUGE WAVE OF ZOMBIES IS APPROACHING!", True, RED)
            off = random.randint(-2, 2)
            surface.blit(t, (WIDTH//2 - t.get_width()//2 + off, HEIGHT//2 + off))

        pygame.draw.rect(surface, (60, 30, 10), (10, 10, 120, 40), border_radius=5)
        st = font_lg.render(str(self.sun), True, WHITE)
        surface.blit(st, (50, 15))
        pygame.draw.circle(surface, SUN_YELLOW, (30, 30), 15)
        
        lt = font_md.render(f"Level {self.level // 10 + 1}-{self.level % 10 if self.level%10!=0 else 10}", True, WHITE)
        surface.blit(lt, (10, HEIGHT-30))

        s_col = (200, 200, 100) if self.shovel_active else (150, 150, 150)
        pygame.draw.rect(surface, s_col, (140, 10, 60, 60), border_radius=5)
        pygame.draw.polygon(surface, SILVER, [(170, 50), (150, 30), (190, 30)])
        pygame.draw.line(surface, BROWN, (170, 30), (170, 15), 5)
        
        avail = self.get_available_plants()
        idx = 0
        for name in avail:
            r = pygame.Rect(10, 80 + idx*70, 190, 60)
            cost = PLANT_DATA[name]['cost']
            cd = PLANT_DATA[name]['cooldown']
            on_cd = (self.ticks - self.plant_cooldowns[name]) < cd
            
            c_col = (150, 150, 120)
            if self.sun < cost: c_col = (100, 100, 100)
            if self.selected_plant == name: c_col = (200, 255, 200)
            
            pygame.draw.rect(surface, c_col, r, border_radius=5)
            pygame.draw.rect(surface, BLACK, r, 2, border_radius=5)
            
            nt = font_md.render(name.upper(), True, BLACK)
            ct = font_md.render(str(cost), True, BLACK)
            surface.blit(nt, (r.x+5, r.y+5))
            surface.blit(ct, (r.x+150, r.y+35))
            
            if on_cd:
                pct = (self.ticks - self.plant_cooldowns[name]) / cd
                h = int(60 * (1-pct))
                s = pygame.Surface((190, h), pygame.SRCALPHA)
                s.fill((0, 0, 0, 128))
                surface.blit(s, (r.x, r.y + (60-h)))
            
            idx += 1

        mx, my = pygame.mouse.get_pos()
        if self.selected_plant:
            pygame.draw.circle(surface, GRASS_GREEN, (mx, my), 20)
        elif self.shovel_active:
            pygame.draw.circle(surface, RED, (mx, my), 20)

        if self.state == 'victory':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            surface.blit(overlay, (0,0))
            
            vt = font_xl.render("LEVEL COMPLETE!", True, GRASS_GREEN)
            surface.blit(vt, (WIDTH//2 - vt.get_width()//2, HEIGHT//2 - 50))
            
            if self.level in [1, 2, 3, 4, 5, 6, 7]:
                ut = font_lg.render("New Plant Unlocked!", True, ORANGE)
                surface.blit(ut, (WIDTH//2 - ut.get_width()//2, HEIGHT//2 + 20))
            
            nt = font_lg.render("Click for Next Level", True, BLACK)
            surface.blit(nt, (WIDTH//2 - nt.get_width()//2, HEIGHT//2 + 80))

        elif self.state == 'game_over':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0,0))
            t = font_xl.render("THE ZOMBIES ATE YOUR BRAINS!", True, RED)
            surface.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2))

# Main Game Loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Plants vs Zombies")
    clock = pygame.time.Clock()
    
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_input(event)
                
        game.update()
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

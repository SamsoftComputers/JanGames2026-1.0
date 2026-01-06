import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isometric Super Mario RPG-Inspired Demo")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
PATH_BROWN = (165, 120, 80)
WALL_GRAY = (100, 100, 100)
PLAYER_RED = (255, 0, 0)
ENEMY_BLUE = (0, 0, 255)
COIN_GOLD = (255, 215, 0)

# Isometric settings
TILE_WIDTH = 64
TILE_HEIGHT = 32
TW_HALF = TILE_WIDTH // 2
TH_HALF = TILE_HEIGHT // 2

# Map size and data (0 = grass, 1 = path, 2 = wall)
MAP_SIZE = 30
map_data = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

# Create borders and some paths/walls
for x in range(MAP_SIZE):
    for y in range(MAP_SIZE):
        if x == 0 or x == MAP_SIZE-1 or y == 0 or y == MAP_SIZE-1:
            map_data[y][x] = 2  # walls
        elif (x - 15)**2 + (y - 15)**2 < 50:
            map_data[y][x] = 1  # central path area
        elif abs(x - 10) < 3 and abs(y - 20) < 10:
            map_data[y][x] = 1  # extra path

# Player start (in tile units, float for smooth movement)
player_x, player_y = 15.0, 15.0
speed = 0.15

# Coins (tile positions)
coins = [(10, 10), (20, 10), (10, 20), (20, 20), (15, 5), (25, 25), (5, 25)]

# Enemy
enemy_x, enemy_y = 20.0, 20.0
enemy_speed = 0.05
enemy_dir = 1  # simple back-and-forth

# Score
score = 0

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Movement input (isometric directions)
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]: dx -= speed; dy -= speed  # northwest
    if keys[pygame.K_s]: dx += speed; dy += speed  # southeast
    if keys[pygame.K_a]: dx -= speed; dy += speed  # southwest
    if keys[pygame.K_d]: dx += speed; dy -= speed  # northeast

    # Attempt move and check collision
    new_x = player_x + dx
    new_y = player_y + dy
    tile_x, tile_y = int(new_x), int(new_y)
    if 0 <= tile_x < MAP_SIZE and 0 <= tile_y < MAP_SIZE and map_data[tile_y][tile_x] != 2:
        player_x, player_y = new_x, new_y

    # Enemy simple movement
    enemy_x += enemy_speed * enemy_dir
    if enemy_x > 25 or enemy_x < 15:
        enemy_dir *= -1

    # Coin collection
    player_tile_x, player_tile_y = int(player_x), int(player_y)
    if (player_tile_x, player_tile_y) in coins:
        coins.remove((player_tile_x, player_tile_y))
        score += 1

    # Enemy collision (reset)
    if abs(player_x - enemy_x) < 0.8 and abs(player_y - enemy_y) < 0.8:
        player_x, player_y = 15.0, 15.0
        score = max(0, score - 1)

    # Camera origin (centers player)
    origin_x = SCREEN_WIDTH // 2 - (player_x - player_y) * TW_HALF
    origin_y = SCREEN_HEIGHT // 2 - (player_x + player_y) * TH_HALF + 50  # offset for visual balance

    # Fill background
    screen.fill(SKY_BLUE)

    # Prepare tiles for depth sorting (farther first)
    tiles = [(tx + ty, tx, ty) for ty in range(MAP_SIZE) for tx in range(MAP_SIZE)]
    tiles.sort(reverse=True)

    # Draw tiles
    for _, tx, ty in tiles:
        color = GRASS_GREEN if map_data[ty][tx] == 0 else PATH_BROWN if map_data[ty][tx] == 1 else WALL_GRAY
        iso_x = origin_x + (tx - ty) * TW_HALF
        iso_y = origin_y + (tx + ty) * TH_HALF
        points = [
            (iso_x, iso_y - TH_HALF),                     # top
            (iso_x - TW_HALF, iso_y),                     # left
            (iso_x, iso_y + TH_HALF),                     # bottom
            (iso_x + TW_HALF, iso_y)                      # right
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)  # outline

    # Draw coins
    for cx, cy in coins:
        iso_x = origin_x + (cx - cy) * TW_HALF
        iso_y = origin_y + (cx + cy) * TH_HALF
        pygame.draw.circle(screen, COIN_GOLD, (int(iso_x), int(iso_y) - 10), 12)
        pygame.draw.circle(screen, (255, 255, 255), (int(iso_x), int(iso_y) - 10), 12, 3)

    # Draw enemy
    iso_x = origin_x + (enemy_x - enemy_y) * TW_HALF
    iso_y = origin_y + (enemy_x + enemy_y) * TH_HALF
    pygame.draw.circle(screen, ENEMY_BLUE, (int(iso_x), int(iso_y) - 20), 20)
    pygame.draw.circle(screen, (0, 0, 0), (int(iso_x) - 8, int(iso_y) - 25), 5)  # eyes

    # Draw player (simple Mario-like)
    iso_x = origin_x + (player_x - player_y) * TW_HALF
    iso_y = origin_y + (player_x + player_y) * TH_HALF
    pygame.draw.circle(screen, (255, 255, 200), (int(iso_x), int(iso_y) - 30), 15)  # head
    pygame.draw.rect(screen, PLAYER_RED, (int(iso_x) - 15, int(iso_y) - 20, 30, 40))  # body
    pygame.draw.rect(screen, PLAYER_RED, (int(iso_x) - 12, int(iso_y) - 45, 24, 15))  # hat
    pygame.draw.circle(screen, (0, 0, 0), (int(iso_x) + 8, int(iso_y) - 32), 4)  # eye

    # Score
    score_text = font.render(f"Coins: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()   

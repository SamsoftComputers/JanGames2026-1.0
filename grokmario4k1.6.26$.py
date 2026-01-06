import pygame

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Mario-Inspired Platformer")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
BRICK_BROWN = (165, 42, 42)
PLAYER_RED = (255, 0, 0)
ENEMY_BLUE = (0, 0, 255)
COIN_GOLD = (255, 215, 0)

# Player variables
player_x = 100
player_y = 400
player_width = 40
player_height = 60
player_vel_x = 0
player_vel_y = 0
gravity = 1
is_jumping = False

# Platforms (long ground + floating ones)
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH * 3, 50),  # Long ground
    pygame.Rect(300, 450, 250, 20),
    pygame.Rect(700, 350, 300, 20),
    pygame.Rect(1200, 400, 200, 20),
    pygame.Rect(1500, 300, 250, 20),
]

# Coins
coins = [
    pygame.Rect(350, 400, 20, 20),
    pygame.Rect(800, 300, 20, 20),
    pygame.Rect(1300, 350, 20, 20),
    pygame.Rect(1600, 250, 20, 20),
]

# Enemy
enemy_x = 900
enemy_y = SCREEN_HEIGHT - 40 - 40
enemy_width = 50
enemy_height = 40
enemy_speed = 2

# Score
score = 0

# Camera offset
camera_x = 0

# Main loop
running = True
while running:
    clock.tick(60)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input
    keys = pygame.key.get_pressed()
    player_vel_x = 0
    if keys[pygame.K_LEFT]:
        player_vel_x = -6
    if keys[pygame.K_RIGHT]:
        player_vel_x = 6
    if keys[pygame.K_SPACE] and not is_jumping:
        player_vel_y = -16
        is_jumping = True

    # Apply gravity
    player_vel_y += gravity

    # Update player position
    player_x += player_vel_x
    player_y += player_vel_y

    # Player rect for collisions
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    # Platform collision (simple top landing + basic sides)
    is_jumping = True
    for plat in platforms:
        if player_rect.colliderect(plat):
            # Landing on top
            if player_vel_y >= 0 and player_rect.bottom - player_vel_y <= plat.top + 10:
                player_y = plat.top - player_height
                player_vel_y = 0
                is_jumping = False
            # Basic side collision
            else:
                if player_vel_x > 0:
                    player_x = plat.left - player_width
                elif player_vel_x < 0:
                    player_x = plat.right

    # Fall off screen reset
    if player_y > SCREEN_HEIGHT + 100:
        player_x = 100
        player_y = 400
        player_vel_y = 0
        score = max(0, score - 1)  # Penalty

    # Enemy movement (back and forth on ground)
    enemy_x += enemy_speed
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
    if enemy_x <= 800 or enemy_x >= 1200:
        enemy_speed *= -1

    # Enemy collision (reset position)
    if player_rect.colliderect(enemy_rect):
        player_x = 100
        player_y = 400
        player_vel_y = 0
        score = 0

    # Coin collection
    for coin in coins[:]:
        if player_rect.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Camera follows player
    camera_x = max(0, player_x - SCREEN_WIDTH // 2)

    # Drawing
    screen.fill(SKY_BLUE)

    # Draw platforms
    for plat in platforms:
        draw_rect = plat.copy()
        draw_rect.x -= camera_x
        color = GROUND_GREEN if plat.width > SCREEN_WIDTH else BRICK_BROWN
        pygame.draw.rect(screen, color, draw_rect)

    # Draw coins
    for coin in coins:
        draw_coin = coin.copy()
        draw_coin.x -= camera_x
        pygame.draw.circle(screen, COIN_GOLD, draw_coin.center, 12)
        pygame.draw.circle(screen, (255, 255, 255), draw_coin.center, 12, 3)

    # Draw enemy (simple Goomba-like)
    draw_enemy = enemy_rect.copy()
    draw_enemy.x -= camera_x
    pygame.draw.rect(screen, ENEMY_BLUE, draw_enemy)
    pygame.draw.circle(screen, (0, 0, 0), (draw_enemy.centerx, draw_enemy.top + 10), 10)  # Eyes

    # Draw player (simple Mario look)
    draw_player = player_rect.copy()
    draw_player.x -= camera_x
    pygame.draw.rect(screen, PLAYER_RED, draw_player)  # Body
    pygame.draw.rect(screen, PLAYER_RED, (draw_player.x + 8, draw_player.y - 12, 24, 15))  # Hat
    pygame.draw.circle(screen, (255, 255, 200), (draw_player.x + 30, draw_player.y + 15), 8)  # Face
    pygame.draw.circle(screen, (0, 0, 0), (draw_player.x + 33, draw_player.y + 13), 3)  # Eye

    # Score display
    score_text = font.render(f"Coins: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()

pygame.quit()

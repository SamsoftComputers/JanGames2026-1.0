import pygame
import math
import random
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5
TILE_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
BROWN = (165, 42, 42)
SKY_BLUE = (135, 206, 235)
BRICK_RED = (200, 70, 50)
QUESTION_BOX = (255, 200, 50)
PIPE_GREEN = (30, 180, 30)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3
        self.coins = 0
        self.power_up = "small"
        self.invincible = 0
        self.animation_frame = 0
        self.animation_timer = 0
        
    def update(self, platforms, enemies, items, level_data):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Horizontal movement
        self.rect.x += self.velocity_x
        
        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
        
        # Vertical movement
        self.rect.y += self.velocity_y
        self.on_ground = False
        
        # Check vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
        
        # Check screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.die()
            
        # Check item collisions
        for item in items[:]:
            if self.rect.colliderect(item.rect):
                if item.type == "coin":
                    self.coins += 1
                    self.score += 100
                    items.remove(item)
                elif item.type == "mushroom":
                    self.power_up = "big"
                    self.score += 1000
                    items.remove(item)
                elif item.type == "flower":
                    self.power_up = "fire"
                    self.score += 1000
                    items.remove(item)
                    
        # Check enemy collisions
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                if self.velocity_y > 0 and self.rect.bottom < enemy.rect.centery + 20:
                    # Jump on enemy
                    self.velocity_y = JUMP_STRENGTH * 0.7
                    self.score += 200
                    enemies.remove(enemy)
                elif self.invincible > 0:
                    # Invincible - kill enemy
                    self.score += 200
                    enemies.remove(enemy)
                elif self.power_up == "big":
                    # Hit enemy, shrink
                    self.power_up = "small"
                    self.invincible = 60
                elif self.power_up == "fire":
                    # Hit enemy, lose fire power
                    self.power_up = "big"
                    self.invincible = 60
                else:
                    # Die
                    self.die()
                    
        # Update invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
            
        # Animation
        if abs(self.velocity_x) > 0:
            self.animation_timer += 1
            if self.animation_timer >= 10:
                self.animation_frame = (self.animation_frame + 1) % 3
                self.animation_timer = 0
        else:
            self.animation_frame = 0
            
    def die(self):
        self.lives -= 1
        if self.lives > 0:
            self.rect.x = 100
            self.rect.y = 400
            self.velocity_y = 0
            self.power_up = "small"
            self.invincible = 60
        else:
            return "game_over"
        return None
            
    def draw(self, screen, camera_x):
        # Calculate position relative to camera
        draw_x = self.rect.x - camera_x
        
        # Draw invincibility flash
        if self.invincible > 0 and self.invincible % 6 < 3:
            return
            
        # Draw player based on power-up state
        if self.power_up == "small":
            color = RED
            height = 40
        else:
            color = RED
            height = 50
            
        # Draw body
        pygame.draw.rect(screen, color, (draw_x, self.rect.y, self.rect.width, height))
        
        # Draw face
        face_x = draw_x + (self.rect.width - 10) if self.facing_right else draw_x
        pygame.draw.rect(screen, WHITE, (face_x, self.rect.y + 10, 10, 8))
        pygame.draw.rect(screen, BLACK, (face_x + (2 if self.facing_right else 0), 
                                         self.rect.y + 12, 4, 4))
        
        # Draw hat
        pygame.draw.rect(screen, RED, (draw_x - 5, self.rect.y - 5, self.rect.width + 10, 10))
        
    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH

class Platform:
    def __init__(self, x, y, width, height, type="ground"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type
        
    def draw(self, screen, camera_x):
        draw_x = self.rect.x - camera_x
        
        if self.type == "ground":
            # Ground block
            pygame.draw.rect(screen, BROWN, (draw_x, self.rect.y, self.rect.width, self.rect.height))
            pygame.draw.rect(screen, GREEN, (draw_x, self.rect.y, self.rect.width, 10))
            
        elif self.type == "brick":
            # Brick block
            for i in range(0, self.rect.width, TILE_SIZE):
                for j in range(0, self.rect.height, TILE_SIZE):
                    pygame.draw.rect(screen, BRICK_RED, 
                                    (draw_x + i, self.rect.y + j, TILE_SIZE-2, TILE_SIZE-2))
                    pygame.draw.rect(screen, (BRICK_RED[0]-30, BRICK_RED[1]-30, BRICK_RED[2]-30),
                                    (draw_x + i, self.rect.y + j, TILE_SIZE-2, 4))
                    
        elif self.type == "question":
            # Question block
            pygame.draw.rect(screen, QUESTION_BOX, 
                           (draw_x, self.rect.y, self.rect.width, self.rect.height))
            pygame.draw.rect(screen, YELLOW, 
                           (draw_x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10))
            font = pygame.font.Font(None, 30)
            text = font.render("?", True, BLACK)
            screen.blit(text, (draw_x + 15, self.rect.y + 10))

class Enemy:
    def __init__(self, x, y, enemy_type="goomba"):
        self.rect = pygame.Rect(x, y, 35, 35)
        self.velocity_x = random.choice([-1, 1]) * 2
        self.velocity_y = 0
        self.type = enemy_type
        
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Horizontal movement
        self.rect.x += self.velocity_x
        
        # Check horizontal collisions with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                    self.velocity_x *= -1
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
                    self.velocity_x *= -1
        
        # Vertical movement
        self.rect.y += self.velocity_y
        
        # Check vertical collisions with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
        
        # Check screen bounds
        if self.rect.left < 0 or self.rect.right > 3000:
            self.velocity_x *= -1
            
    def draw(self, screen, camera_x):
        draw_x = self.rect.x - camera_x
        
        if self.type == "goomba":
            # Brown goomba
            pygame.draw.rect(screen, (150, 100, 50), 
                           (draw_x, self.rect.y, self.rect.width, self.rect.height))
            pygame.draw.rect(screen, BLACK, 
                           (draw_x + 10, self.rect.y + 10, 5, 5))
            pygame.draw.rect(screen, BLACK, 
                           (draw_x + 20, self.rect.y + 10, 5, 5))

class Item:
    def __init__(self, x, y, item_type="coin"):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = item_type
        self.bounce = 0
        self.bounce_dir = 1
        
    def update(self):
        if self.type == "coin":
            self.bounce += 0.2 * self.bounce_dir
            if self.bounce > 5 or self.bounce < 0:
                self.bounce_dir *= -1
                
    def draw(self, screen, camera_x):
        draw_x = self.rect.x - camera_x
        
        if self.type == "coin":
            pygame.draw.circle(screen, YELLOW, 
                             (int(draw_x + 10), int(self.rect.y + 10 - self.bounce)), 10)
            pygame.draw.circle(screen, (200, 150, 0), 
                             (int(draw_x + 10), int(self.rect.y + 10 - self.bounce)), 8)
        elif self.type == "mushroom":
            # Red mushroom
            pygame.draw.rect(screen, RED, 
                           (draw_x, self.rect.y, self.rect.width, self.rect.height))
            pygame.draw.rect(screen, WHITE, 
                           (draw_x, self.rect.y, self.rect.width, 8))

class Level:
    def __init__(self, world, level, player):
        self.world = world
        self.level = level
        self.player = player
        self.platforms = []
        self.enemies = []
        self.items = []
        self.camera_x = 0
        self.level_width = 3000
        self.goal_x = 2800
        self.create_level()
        
    def create_level(self):
        # Clear existing objects
        self.platforms = []
        self.enemies = []
        self.items = []
        
        # Ground platform
        for i in range(0, self.level_width, TILE_SIZE):
            self.platforms.append(Platform(i, 550, TILE_SIZE, TILE_SIZE, "ground"))
            
        # Create level based on world and level number
        if self.world == 1:
            if self.level == 1:
                self.create_world_1_1()
            elif self.level == 2:
                self.create_world_1_2()
            elif self.level == 3:
                self.create_world_1_3()
            elif self.level == 4:
                self.create_world_1_4()
        elif self.world == 8:
            if self.level == 4:
                self.create_world_8_4()
                
    def create_world_1_1(self):
        # Basic level 1-1 layout
        # Platforms
        for i in range(200, 400, TILE_SIZE):
            self.platforms.append(Platform(i, 450, TILE_SIZE, TILE_SIZE, "brick"))
            
        # Question blocks
        self.platforms.append(Platform(300, 350, TILE_SIZE, TILE_SIZE, "question"))
        self.platforms.append(Platform(400, 350, TILE_SIZE, TILE_SIZE, "question"))
        
        # Enemies
        self.enemies.append(Enemy(500, 500))
        self.enemies.append(Enemy(700, 500))
        
        # Items
        self.items.append(Item(300, 300, "coin"))
        self.items.append(Item(400, 300, "mushroom"))
        
    def create_world_1_2(self):
        # More challenging level
        for i in range(300, 600, TILE_SIZE):
            self.platforms.append(Platform(i, 400, TILE_SIZE, TILE_SIZE, "brick"))
        for i in range(800, 1000, TILE_SIZE):
            self.platforms.append(Platform(i, 300, TILE_SIZE, TILE_SIZE, "brick"))
            
        self.enemies.append(Enemy(400, 500))
        self.enemies.append(Enemy(600, 500))
        self.enemies.append(Enemy(900, 250))
        
        for i in range(5):
            self.items.append(Item(350 + i*100, 350, "coin"))
            
    def create_world_8_4(self):
        # Final challenging level
        # Create floating platforms
        for i in range(0, 2000, 300):
            platform_height = 300 + math.sin(i/100) * 100
            for j in range(i, i+100, TILE_SIZE):
                self.platforms.append(Platform(j, platform_height, TILE_SIZE, TILE_SIZE, "brick"))
                
        # More enemies
        for i in range(200, 2500, 200):
            self.enemies.append(Enemy(i, 400))
            
        # Power-ups
        self.items.append(Item(500, 200, "flower"))
        self.items.append(Item(1500, 200, "mushroom"))
        
        # Goal platform
        for i in range(2800, 2900, TILE_SIZE):
            self.platforms.append(Platform(i, 300, TILE_SIZE, TILE_SIZE, "question"))
            
    def update(self):
        # Update player
        result = self.player.update(self.platforms, self.enemies, self.items, self)
        if result == "game_over":
            return "game_over"
            
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.platforms)
            
        # Update items
        for item in self.items:
            item.update()
            
        # Update camera
        self.camera_x = max(0, min(self.player.rect.centerx - SCREEN_WIDTH // 2, 
                                 self.level_width - SCREEN_WIDTH))
        
        # Check if level completed
        if self.player.rect.x >= self.goal_x:
            return "level_complete"
            
        return None
        
    def draw(self, screen):
        # Draw sky background
        screen.fill(SKY_BLUE)
        
        # Draw clouds (background decoration)
        for i in range(0, self.level_width, 400):
            cloud_x = i - self.camera_x * 0.5
            if cloud_x > -100 and cloud_x < SCREEN_WIDTH + 100:
                pygame.draw.circle(screen, WHITE, (int(cloud_x + 50), 80), 30)
                pygame.draw.circle(screen, WHITE, (int(cloud_x + 80), 70), 40)
                pygame.draw.circle(screen, WHITE, (int(cloud_x + 110), 80), 30)
        
        # Draw platforms
        for platform in self.platforms:
            if platform.rect.right > self.camera_x and platform.rect.left < self.camera_x + SCREEN_WIDTH:
                platform.draw(screen, self.camera_x)
                
        # Draw enemies
        for enemy in self.enemies:
            if enemy.rect.right > self.camera_x and enemy.rect.left < self.camera_x + SCREEN_WIDTH:
                enemy.draw(screen, self.camera_x)
                
        # Draw items
        for item in self.items:
            if item.rect.right > self.camera_x and item.rect.left < self.camera_x + SCREEN_WIDTH:
                item.draw(screen, self.camera_x)
                
        # Draw player
        self.player.draw(screen, self.camera_x)
        
        # Draw HUD
        self.draw_hud(screen)
        
    def draw_hud(self, screen):
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"SCORE: {self.player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Coins
        coin_text = font.render(f"COINS: {self.player.coins}", True, YELLOW)
        screen.blit(coin_text, (10, 50))
        
        # Lives
        lives_text = font.render(f"LIVES: {self.player.lives}", True, GREEN)
        screen.blit(lives_text, (10, 90))
        
        # World
        world_text = font.render(f"WORLD {self.world}-{self.level}", True, WHITE)
        screen.blit(world_text, (SCREEN_WIDTH - 150, 10))
        
        # Power-up status
        power_text = font.render(f"POWER: {self.player.power_up.upper()}", True, RED)
        screen.blit(power_text, (SCREEN_WIDTH - 150, 50))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ULTRA MARIO 2D BROS.")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "main_menu"
        self.player = None
        self.current_level = None
        self.world = 1
        self.level = 1
        
    def main_menu(self):
        """Display main menu screen"""
        title_font = pygame.font.Font(None, 82)
        font = pygame.font.Font(None, 36)
        
        while self.state == "main_menu" and self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        self.start_game()
                    elif event.key == K_1:
                        self.world = 1
                        self.level = 1
                        self.start_game()
                    elif event.key == K_8:
                        self.world = 8
                        self.level = 4
                        self.start_game()
                    elif event.key == K_ESCAPE:
                        self.running = False
                        
            # Draw main menu
            self.screen.fill(SKY_BLUE)
            
            # Title with shadow
            title = title_font.render("ULTRA MARIO 2D BROS.", True, BLACK)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2 + 4, SCREEN_HEIGHT//4 + 4))
            self.screen.blit(title, title_rect)
            
            title = title_font.render("ULTRA MARIO 2D BROS.", True, RED)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
            self.screen.blit(title, title_rect)
            
            # Subtitle
            subtitle = font.render("A Complete 1-1 to 8-4 Adventure!", True, YELLOW)
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 70))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Menu options
            options = [
                "Press ENTER to Start (World 1-1)",
                "Press 1 for World 1-1",
                "Press 8 for World 8-4 (Final Level)",
                "Press ESC to Quit"
            ]
            
            for i, option in enumerate(options):
                text = font.render(option, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i*40))
                self.screen.blit(text, text_rect)
                
            # Draw Mario character
            pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 150, 30, 50))
            pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH//2 - 150 - 5, SCREEN_HEIGHT//2 + 150 - 5, 40, 10))
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def start_game(self):
        """Initialize player and start the game"""
        self.player = Player(100, 400)
        self.current_level = Level(self.world, self.level, self.player)
        self.state = "playing"
        
    def game_loop(self):
        """Main game loop"""
        while self.state == "playing" and self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.state = "main_menu"
                    elif event.key == K_SPACE:
                        self.player.jump()
                    elif event.key == K_r:
                        # Restart level
                        self.current_level = Level(self.world, self.level, self.player)
                        
            # Get key states for movement
            keys = pygame.key.get_pressed()
            self.player.velocity_x = 0
            
            if keys[K_LEFT] or keys[K_a]:
                self.player.velocity_x = -PLAYER_SPEED
                self.player.facing_right = False
            if keys[K_RIGHT] or keys[K_d]:
                self.player.velocity_x = PLAYER_SPEED
                self.player.facing_right = True
                
            # Update level
            result = self.current_level.update()
            
            if result == "game_over":
                self.game_over()
            elif result == "level_complete":
                self.level_complete()
                
            # Draw everything
            self.current_level.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def game_over(self):
        """Handle game over"""
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        game_over = True
        while game_over and self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    game_over = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        # Restart from beginning
                        self.world = 1
                        self.level = 1
                        self.start_game()
                        return
                    elif event.key == K_ESCAPE:
                        self.state = "main_menu"
                        return
                        
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            # Game Over text
            text = font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text, text_rect)
            
            # Score
            score_text = small_font.render(f"Final Score: {self.player.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(score_text, score_rect)
            
            # Instructions
            inst_text = small_font.render("Press ENTER to Restart or ESC for Menu", True, YELLOW)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(inst_text, inst_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def level_complete(self):
        """Handle level completion"""
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        # Progress to next level
        if self.level < 4:
            self.level += 1
        elif self.world < 8:
            self.world += 1
            self.level = 1
        else:
            # Game completed!
            self.game_completed()
            return
            
        complete = True
        while complete and self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    complete = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        self.start_game()
                        return
                    elif event.key == K_ESCAPE:
                        self.state = "main_menu"
                        return
                        
            # Draw level complete screen
            self.screen.fill(SKY_BLUE)
            
            # Level Complete text
            text = font.render("LEVEL COMPLETE!", True, GREEN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(text, text_rect)
            
            # Next level info
            next_text = small_font.render(f"Next: World {self.world}-{self.level}", True, WHITE)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(next_text, next_rect)
            
            # Score
            score_text = small_font.render(f"Score: {self.player.score}", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(score_text, score_rect)
            
            # Instructions
            inst_text = small_font.render("Press ENTER to Continue or ESC for Menu", True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(inst_text, inst_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def game_completed(self):
        """Handle game completion (all 8 worlds)"""
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        completed = True
        while completed and self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    completed = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        self.state = "main_menu"
                        return
                    elif event.key == K_ESCAPE:
                        self.state = "main_menu"
                        return
                        
            # Draw completion screen
            self.screen.fill(SKY_BLUE)
            
            # Congratulations text
            text = font.render("CONGRATULATIONS!", True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(text, text_rect)
            
            # Completion message
            msg_text = small_font.render("You completed all 8 worlds!", True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(msg_text, msg_rect)
            
            # Final score
            score_text = small_font.render(f"Final Score: {self.player.score}", True, GREEN)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(score_text, score_rect)
            
            # Coins collected
            coins_text = small_font.render(f"Coins Collected: {self.player.coins}", True, YELLOW)
            coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(coins_text, coins_rect)
            
            # Instructions
            inst_text = small_font.render("Press ENTER to Return to Menu", True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
            self.screen.blit(inst_text, inst_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def run(self):
        """Main game loop"""
        print("=" * 50)
        print("ULTRA MARIO 2D BROS.")
        print("Complete 1-1 to 8-4 Adventure!")
        print("=" * 50)
        print("\nCONTROLS:")
        print("LEFT/RIGHT or A/D: Move")
        print("SPACE: Jump")
        print("ESC: Menu/Back")
        print("R: Restart Level")
        print("=" * 50)
        
        while self.running:
            if self.state == "main_menu":
                self.main_menu()
            elif self.state == "playing":
                self.game_loop()
                
        pygame.quit()
        sys.exit()

# Main program entry
if __name__ == "__main__":
    game = Game()
    game.run()

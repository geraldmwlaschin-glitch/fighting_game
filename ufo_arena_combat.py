
# UFO Arena Combat - Web Version

import pygame
import sys
import random
import math
import asyncio
from player import Player
from level import Level
from powerups import Powerup, RapidFirePowerup, ScorePowerup

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UFO.io - Arena Combat")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Game state
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
player.is_ufo_mode = True
player.bullets = []
player.boost = False
player.vel_y = 1
player.gravity_enabled = False
player.last_shot = 0
player.rapid_fire = False
player.rapid_fire_end_time = 0
enemies = []
powerups = []
score = 0
start_time = pygame.time.get_ticks()
paused = False
enemy_spawn_counter = 0
difficulty = 0
combo = 0
combo_timer = 0
game_over = False
game_over_time = 0

def spawn_enemy():
    """Spawn an enemy at random edge position"""
    try:
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, SCREEN_WIDTH)
            y = -30
        elif side == 'bottom':
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 30
        elif side == 'left':
            x = -30
            y = random.randint(0, SCREEN_HEIGHT)
        else:
            x = SCREEN_WIDTH + 30
            y = random.randint(0, SCREEN_HEIGHT)
        
        enemy = {}
        enemy['x'] = float(x)
        enemy['y'] = float(y)
        enemy['speed'] = 1.5 + (difficulty * 0.2)
        enemy['health'] = 1
        enemy['radius'] = 12
        enemies.append(enemy)
    except Exception as e:
        print(f"Error spawning enemy: {e}")

def spawn_powerup(x, y):
    """Spawn a random powerup at position"""
    powerup_type = random.choice([RapidFirePowerup, ScorePowerup])
    powerups.append(powerup_type(x, y))

def update_enemies():
    """Update all enemies"""
    global score, combo, combo_timer, game_over
    
    for enemy in enemies[:]:
        try:
            dx = player.rect.centerx - enemy['x']
            dy = player.rect.centery - enemy['y']
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 1:
                enemy['x'] += (dx / dist) * enemy['speed']
                enemy['y'] += (dy / dist) * enemy['speed']
            
            hit = False
            bullets_to_remove = []
            for bullet in player.bullets[:]:
                try:
                    bullet_dist = math.sqrt((bullet['x'] - enemy['x'])**2 + (bullet['y'] - enemy['y'])**2)
                    if bullet_dist < 25:
                        enemy['health'] -= 1
                        bullets_to_remove.append(bullet)
                        hit = True
                        break
                except:
                    bullets_to_remove.append(bullet)
            
            for bullet in bullets_to_remove:
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
            
            if hit and enemy['health'] <= 0:
                if enemy in enemies:
                    enemies.remove(enemy)
                combo += 1
                combo_timer = 120
                bonus = 10 + (combo * 5)
                score += bonus
                if random.random() < 0.3:
                    spawn_powerup(enemy['x'], enemy['y'])
                continue
            
            player_dist = math.sqrt((player.rect.centerx - enemy['x'])**2 + (player.rect.centery - enemy['y'])**2)
            if player_dist < 40:
                if not getattr(player, "invincible", False):
                    game_over = True
                    game_over_time = pygame.time.get_ticks()
        except Exception as e:
            print(f"Error updating enemy: {e}")
            if enemy in enemies:
                enemies.remove(enemy)

def create_bullet(x, y):
    """Create a bullet that shoots toward mouse"""
    bullet = {}
    bullet['x'] = float(x)
    bullet['y'] = float(y)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - x
    dy = mouse_y - y
    dist = math.sqrt(dx**2 + dy**2)
    
    if dist > 0:
        bullet['vx'] = (dx / dist) * 8
        bullet['vy'] = (dy / dist) * 8
    else:
        bullet['vx'] = 0
        bullet['vy'] = -8
    
    bullet['radius'] = 4
    player.bullets.append(bullet)

def update_powerups():
    """Update powerups and check collection"""
    global score
    
    for powerup in powerups[:]:
        if not powerup.update():
            powerups.remove(powerup)
            continue
        
        dist = math.sqrt((powerup.x - player.rect.centerx)**2 + (powerup.y - player.rect.centery)**2)
        if dist < 35:
            if isinstance(powerup, ScorePowerup):
                score += 50
            else:
                powerup.apply(player)
            powerups.remove(powerup)

async def main():
    """Main async game loop for Pygbag compatibility"""
    global paused, game_over, enemy_spawn_counter, difficulty, combo_timer, combo, score, start_time
    
    running = True
    print("Controls: WASD to move, Space for speed boost, Mouse to aim and shoot, C to pause/resume, R to restart")
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = not paused
                if event.key == pygame.K_r and game_over:
                    game_over = False
                    enemies.clear()
                    powerups.clear()
                    score = 0
                    combo = 0
                    start_time = pygame.time.get_ticks()
                    difficulty = 0
                    enemy_spawn_counter = 0
                    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    player.bullets.clear()
                    player.rapid_fire = False
                if not paused and not game_over:
                    if event.key == pygame.K_SPACE:
                        player.boost = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.boost = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            if not paused:
                dx = 0
                dy = 0
                if keys[pygame.K_a]:
                    dx = -4
                if keys[pygame.K_d]:
                    dx = 4
                if keys[pygame.K_w]:
                    dy = -4
                if keys[pygame.K_s]:
                    dy = 4
                
                if getattr(player, 'boost', False):
                    dx = int(dx * 1.5)
                    dy = int(dy * 1.5)
                
                new_x = player.rect.x + dx
                new_y = player.rect.y + dy
                player.rect.x = max(10, min(new_x, SCREEN_WIDTH - 30))
                player.rect.y = max(10, min(new_y, SCREEN_HEIGHT - 30))
                
                current_time = pygame.time.get_ticks()
                mouse_buttons = pygame.mouse.get_pressed()
                fire_cooldown = 20 if player.rapid_fire else 50
                if mouse_buttons[0] and current_time - player.last_shot > fire_cooldown:
                    create_bullet(player.rect.centerx, player.rect.centery)
                    player.last_shot = current_time
        
        if not paused:
            for bullet in player.bullets[:]:
                bullet['x'] += bullet['vx']
                bullet['y'] += bullet['vy']
                if bullet['y'] < -10 or bullet['y'] > SCREEN_HEIGHT + 10 or bullet['x'] < -10 or bullet['x'] > SCREEN_WIDTH + 10:
                    player.bullets.remove(bullet)
            
            update_enemies()
            update_powerups()
            
            if combo_timer > 0:
                combo_timer -= 1
            else:
                combo = 0
            
            enemy_spawn_counter += 1
            spawn_rate = max(20, 100 - int(difficulty * 8))
            if enemy_spawn_counter > spawn_rate:
                enemy_spawn_counter = 0
                spawn_enemy()
            
            elapsed_s = (pygame.time.get_ticks() - start_time) / 1000.0
            difficulty = elapsed_s / 15.0
        
        if player.rapid_fire and pygame.time.get_ticks() > player.rapid_fire_end_time:
            player.rapid_fire = False
        
        # Drawing
        screen.fill((20, 20, 50))
        
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (40, 40, 70), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (40, 40, 70), (0, y), (SCREEN_WIDTH, y), 1)
        
        if not game_over:
            for enemy in enemies:
                pygame.draw.circle(screen, (255, 100, 100), (int(enemy['x']), int(enemy['y'])), enemy['radius'])
            
            for powerup in powerups:
                pygame.draw.circle(screen, powerup.get_color(), (int(powerup.x), int(powerup.y)), powerup.radius)
                pygame.draw.circle(screen, (255, 255, 255), (int(powerup.x), int(powerup.y)), powerup.radius, 2)
            
            if player.bullets:
                for bullet in player.bullets:
                    pygame.draw.circle(screen, (0, 255, 0), (int(bullet['x']), int(bullet['y'])), bullet['radius'])
            
            pygame.draw.circle(screen, (0, 255, 255), player.rect.center, 20)
            pygame.draw.circle(screen, (100, 255, 255), player.rect.center, 20, 2)
            
            elapsed_s = (pygame.time.get_ticks() - start_time) / 1000.0
            time_text = font.render(f"Time: {int(elapsed_s)}s", True, (255, 255, 255))
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            enemies_text = small_font.render(f"Enemies: {len(enemies)}", True, (255, 100, 100))
            
            screen.blit(time_text, (10, 10))
            screen.blit(score_text, (10, 50))
            screen.blit(enemies_text, (10, 90))
            
            if combo > 0:
                combo_color = (255, 255, 100) if combo_timer > 60 else (255, 150, 50)
                combo_text = font.render(f"COMBO x{combo}!", True, combo_color)
                screen.blit(combo_text, (SCREEN_WIDTH - 250, 10))
            
            if player.rapid_fire:
                remaining_ms = max(0, player.rapid_fire_end_time - pygame.time.get_ticks())
                remaining_s = remaining_ms / 1000.0
                rapid_text = small_font.render(f"Rapid Fire: {remaining_s:.1f}s", True, (255, 200, 100))
                screen.blit(rapid_text, (10, 120))
            
            if paused:
                pause_surf = font.render("Miracles are possible, your one of them! (press C to resume)", True, (255, 255, 255))
                pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                screen.blit(overlay, (0, 0))
                screen.blit(pause_surf, pause_rect)
        else:
            elapsed_s = (pygame.time.get_ticks() - start_time) / 1000.0
            game_over_text = font.render("YOU DIED!", True, (255, 50, 50))
            final_score = font.render(f"Final Score: {score}", True, (255, 255, 255))
            time_text = font.render(f"Survived: {int(elapsed_s)}s", True, (255, 255, 255))
            restart_text = small_font.render("Press R to restart", True, (255, 255, 255))
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 80))
            screen.blit(final_score, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 10))
            screen.blit(time_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 + 100))
        
        pygame.display.flip()
        await asyncio.sleep(0)  # Yield to browser event loop

if __name__ == "__main__":
    asyncio.run(main())

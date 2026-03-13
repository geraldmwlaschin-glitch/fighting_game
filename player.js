# Player class for UFO game

import pygame
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 48))
        self.image.fill((9, 0, 0)) # 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.start_x = x
        self.start_y = y
        self.gravity = 0.6
        self.jump_power = -12
        self.direction = 1  # 1 for right, -1 for left
        self.has_shoot_power = False
        self.shoot_cooldown = 0
        self.bullets = pygame.sprite.Group()

        # NEW: shooting power-up counter and invincibility state
        self.shoot_power_count = 0
        self.invincible = False
        self.invincible_end_time = 0  # pygame.time.get_ticks() when invincibility ends
        self.INVINCIBLE_DURATION_MS = 4000
    
    def move_left(self):
        self.vel_x = -5
        self.direction = -1
    
    def move_right(self):
        self.vel_x = 5
        self.direction = 1
    
    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
    
    def shoot(self):
        if self.has_shoot_power and self.shoot_cooldown <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
            self.bullets.add(bullet)
            self.shoot_cooldown = 10

    def activate_power_up(self, power_type):
        if power_type == "shoot":
            # increment number of shoot powerups collected
            self.shoot_power_count += 1
            self.has_shoot_power = True

            # If collected more than one, trigger invincibility
            if self.shoot_power_count > 1:
                now = pygame.time.get_ticks()
                # extend or set invincibility end time
                self.invincible_end_time = max(self.invincible_end_time, now) + self.INVINCIBLE_DURATION_MS
                self.invincible = True
                # reset counter so additional single pickups can retrigger extension when collected twice again
                self.shoot_power_count = 0
    
    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vel_y = 0
        self.has_shoot_power = False
        self.bullets.empty()

        # reset invincibility and counters on death/level reset
        self.shoot_power_count = 0
        self.invincible = False
        self.invincible_end_time = 0
    
    def update(self, platforms, enemies):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.vel_x = 0
        self.rect.y += self.vel_y
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update invincibility state
        if self.invincible:
            if pygame.time.get_ticks() >= self.invincible_end_time:
                self.invincible = False
                # keep shoot power but invincibility ended
        self.on_ground = False
        
        # Collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        # Collision with enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                # only reset if not invincible
                if not self.invincible:
                    self.reset()
                else:
                    # Optionally, while invincible we can remove the enemy
                    enemy.kill()
        
        # Update bullets
        self.bullets.update()
        
        # Bullet collision with enemies
        for bullet in self.bullets:
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    enemy.kill()

import pygame
from game.constants import *

class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                              PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.is_moving = False
        self.fast_falling = False
        self.jump_buffer = 0
        self.coyote_time = 0
        self.is_dead = False
        self.fall_distance = 0
        self.last_ground_y = 0
        
        self.highest_y = self.rect.y
        self.last_score_y = self.rect.y
        self.current_score = 0
        
        self.high_jump_active = False
        self.high_jump_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = max(self.velocity.x - 0.5, -PLAYER_SPEED)
            self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = min(self.velocity.x + 0.5, PLAYER_SPEED)
            self.is_moving = True
        else:
            self.velocity.x *= 0.9
            if abs(self.velocity.x) < 0.1:
                self.velocity.x = 0
            self.is_moving = False

        self.fast_falling = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            if self.on_ground or self.coyote_time > 0:
                jump_force = PLAYER_JUMP_FORCE * (HIGH_JUMP_MULTIPLIER if self.high_jump_active else 1.0)
                self.velocity.y = jump_force
                self.on_ground = False
                self.coyote_time = 0
            else:
                self.jump_buffer = 5

    def calculate_height_score(self, current_y):
        """Вычисляет очки на основе пройденной высоты"""
        height_diff = self.last_score_y - current_y
        if height_diff <= 0:
            return 0
            
        height_level = int((self.highest_y - current_y) / HEIGHT_SCORE_INTERVAL)
        multiplier = min(HEIGHT_SCORE_MULTIPLIER ** height_level, MAX_HEIGHT_MULTIPLIER)
        
        score = int(height_diff * SCORE_PER_HEIGHT_UNIT * multiplier)
        self.last_score_y = current_y
        
        return score

    def update(self, level, camera):
        if self.is_dead:
            return False

        self.handle_input()
        
        if self.high_jump_active:
            self.high_jump_timer -= 1
            if self.high_jump_timer <= 0:
                self.high_jump_active = False
        
        gravity = PLAYER_GRAVITY * (PLAYER_FAST_FALL_MULTIPLIER if self.fast_falling else 1.0)
        self.velocity.y += gravity

        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        if self.rect.y < self.highest_y:
            self.highest_y = self.rect.y
            score = self.calculate_height_score(self.rect.y)
            if score > 0:
                self.current_score += score

        if not self.on_ground:
            self.fall_distance = self.rect.y - self.last_ground_y
        else:
            self.last_ground_y = self.rect.y
            self.fall_distance = 0

        self.on_ground = False
        platform_landed = False

        for platform in level.platforms:
            if platform.power_up and platform.power_up.is_active:
                if self.rect.colliderect(platform.power_up.rect):
                    if platform.power_up.type == "high_jump":
                        self.high_jump_active = True
                        self.high_jump_timer = HIGH_JUMP_DURATION
                        self.current_score += 50
                        platform.power_up.is_active = False
            
            if platform.is_visible and self.rect.colliderect(platform.rect):
                if self.velocity.y < 0:
                    continue
                elif self.velocity.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.coyote_time = 5
                    
                    self.velocity.y = PLAYER_JUMP_FORCE * (HIGH_JUMP_MULTIPLIER if self.high_jump_active else 1.0)
                    self.on_ground = False
                    
                    if platform.type == PLATFORM_DISAPPEARING:
                        platform.disappear_timer = 1

        if not self.on_ground:
            self.coyote_time = max(0, self.coyote_time - 1)

        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self.on_ground:
                self.velocity.y = PLAYER_JUMP_FORCE * (HIGH_JUMP_MULTIPLIER if self.high_jump_active else 1.0)
                self.on_ground = False
                self.jump_buffer = 0

        if self.fall_distance > SCREEN_HEIGHT * 3:
            self.is_dead = True
            return False

        screen_y = self.rect.y - camera.y
        if screen_y > SCREEN_HEIGHT:
            self.is_dead = True
            return False

        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0

        return True

    def render(self, screen, camera):
        screen_x = self.rect.x
        screen_y = self.rect.y - camera.y
        
        pygame.draw.rect(screen, PLAYER_COLOR, 
                        (screen_x, screen_y, self.rect.width, self.rect.height))
        
        if self.high_jump_active:
            pygame.draw.rect(screen, HIGH_JUMP_COLOR,
                           (screen_x - 2, screen_y - 2,
                            self.rect.width + 4, self.rect.height + 4), 2) 
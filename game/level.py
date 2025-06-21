import pygame
import random
from game.constants import *

class PowerUp:
    def __init__(self, x, y, power_up_type):
        """Создает бонус с указанными координатами и типом."""
        self.rect = pygame.Rect(x, y, POWER_UP_SIZE, POWER_UP_SIZE)
        self.type = power_up_type
        self.is_active = True

    def get_color(self):
        """Возвращает цвет бонуса в зависимости от его типа."""
        if self.type == "high_jump":
            return HIGH_JUMP_COLOR
        return WHITE

class Platform:
    def __init__(self, x, y, width, height, platform_type=PLATFORM_NORMAL):
        """Создает платформу с возможными бонусами и особым поведением."""
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        self.original_x = x
        self.original_y = y
        self.disappear_timer = 0
        self.reappear_timer = 0
        self.is_visible = True
        self.movement_direction = 1
        self.movement_progress = 0
        self.power_up = None
        if random.random() < POWER_UP_SPAWN_CHANCE:
            power_up_x = x + width // 2 - POWER_UP_SIZE // 2
            power_up_y = y - POWER_UP_SIZE - 5
            self.power_up = PowerUp(power_up_x, power_up_y, "high_jump")

    def update(self):
        """Обновляет состояние платформы (движение, исчезновение)."""
        if self.type == PLATFORM_DISAPPEARING:
            if not self.is_visible:
                self.reappear_timer += 1
                if self.reappear_timer >= REAPPEAR_DELAY:
                    self.is_visible = True
                    self.reappear_timer = 0
            elif self.disappear_timer > 0:
                self.disappear_timer += 1
                if self.disappear_timer >= DISAPPEAR_DELAY:
                    self.is_visible = False
                    self.disappear_timer = 0
        elif self.type == PLATFORM_MOVING:
            self.movement_progress += MOVING_PLATFORM_SPEED * self.movement_direction
            if abs(self.movement_progress) >= MOVING_PLATFORM_DISTANCE:
                self.movement_direction *= -1
            self.rect.x = self.original_x + self.movement_progress
            if self.power_up:
                self.power_up.rect.x = self.rect.x + self.rect.width // 2 - POWER_UP_SIZE // 2

    def get_color(self):
        """Возвращает цвет платформы в зависимости от ее типа и состояния."""
        if not self.is_visible:
            return BACKGROUND_COLOR
        if self.type == PLATFORM_NORMAL:
            return PLATFORM_COLOR
        elif self.type == PLATFORM_DISAPPEARING:
            return DISAPPEARING_PLATFORM_COLOR
        elif self.type == PLATFORM_MOVING:
            return MOVING_PLATFORM_COLOR
        return PLATFORM_COLOR

class Level:
    def __init__(self):
        """Инициализирует уровень с начальной платформой."""
        self.platforms = []
        self.generate_initial_platform()

    def generate_initial_platform(self):
        """Создает стартовую платформу внизу экрана."""
        initial_platform = Platform(
            SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            PLATFORM_WIDTH,
            PLATFORM_HEIGHT,
            PLATFORM_NORMAL
        )
        self.platforms.append(initial_platform)

    def generate_next_platform(self):
        """Генерирует новую платформу выше предыдущей со случайными параметрами."""
        if not self.platforms:
            return
        last_platform = self.platforms[-1]
        platform_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
        new_x = int(random.gauss(SCREEN_WIDTH / 2, SCREEN_WIDTH / 4))
        new_x = max(0, min(new_x, SCREEN_WIDTH - platform_width))
        new_y = last_platform.rect.top - random.randint(MIN_PLATFORM_DISTANCE, MAX_PLATFORM_DISTANCE)
        platform_type = random.choices(
            [PLATFORM_NORMAL, PLATFORM_DISAPPEARING, PLATFORM_MOVING],
            weights=[0.6, 0.2, 0.2]
        )[0]
        new_platform = Platform(
            int(new_x),
            int(new_y),
            platform_width,
            PLATFORM_HEIGHT,
            platform_type
        )
        self.platforms.append(new_platform)

    def update(self, camera):
        """Обновляет состояние уровня и генерирует новые платформы."""
        self.platforms = [p for p in self.platforms if p.rect.bottom > camera.y - SCREEN_HEIGHT]
        for platform in self.platforms:
            platform.update()
        if len(self.platforms) < 10 or self.platforms[-1].rect.top < camera.y + SCREEN_HEIGHT:
            self.generate_next_platform()

    def render(self, screen, camera):
        """Отрисовывает все платформы и бонусы с учетом камеры."""
        for platform in self.platforms:
            if platform.is_visible:
                screen_platform = camera.apply(platform.rect)
                pygame.draw.rect(screen, platform.get_color(), screen_platform)
                if platform.power_up and platform.power_up.is_active:
                    screen_power_up = camera.apply(platform.power_up.rect)
                    pygame.draw.rect(screen, platform.power_up.get_color(), screen_power_up)
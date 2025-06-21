import pygame
from game.constants import *

class Camera:
    def __init__(self):
        """Инициализирует камеру с начальной позицией и смещением."""
        self.y = 0
        self.player_offset = int(SCREEN_HEIGHT * 0.5)

    def update(self, player):
        """Обновляет позицию камеры, следуя за игроком только вверх."""
        target_y = player.rect.top - self.player_offset
        if target_y < self.y:
            self.y = target_y

    def get_offset(self):
        """Возвращает текущее смещение камеры."""
        return pygame.math.Vector2(0, self.y)

    def apply(self, rect):
        """Применяет смещение камеры к прямоугольнику для отрисовки."""
        return pygame.Rect(
            rect.x,
            rect.y - self.y,
            rect.width,
            rect.height
        )

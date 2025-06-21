import pygame
import sys
from game.player import Player
from game.camera import Camera
from game.level import Level
from game.constants import *

class Game:
    def __init__(self):
        """Инициализирует игру, создает окно, игрока, камеру и уровень."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Infinite Platformer")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.camera = Camera()
        self.level = Level()
        self.running = True
        self.game_over = False
        self.score_font = pygame.font.Font(None, 36)

    def handle_events(self):
        """Обрабатывает события ввода (закрытие окна, нажатия клавиш)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def reset_game(self):
        """Сбрасывает состояние игры для начала заново."""
        self.player = Player()
        self.camera = Camera()
        self.level = Level()
        self.game_over = False

    def update(self):
        """Обновляет состояние всех игровых объектов (игрок, камера, уровень)."""
        self.camera.update(self.player)
        self.level.update(self.camera)
        if not self.player.update(self.level, self.camera):
            self.game_over = True

    def render(self):
        """Отрисовывает все игровые объекты и интерфейс."""
        self.screen.fill(BACKGROUND_COLOR)
        self.level.render(self.screen, self.camera)
        self.player.render(self.screen, self.camera)
        self.render_hud()
        if self.game_over:
            self.render_game_over()
        pygame.display.flip()

    def render_hud(self):
        """Отображает текущий счет игрока."""
        score_text = self.score_font.render(f"Score: {self.player.current_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

    def render_game_over(self):
        """Отображает экран завершения игры с итоговым счетом."""
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over!', True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.screen.blit(text, text_rect)
        score_text = font.render(f'Final Score: {self.player.current_score}', True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
        self.screen.blit(score_text, score_rect)
        restart_text = pygame.font.Font(None, 36).render('Press R to restart', True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Главный игровой цикл."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
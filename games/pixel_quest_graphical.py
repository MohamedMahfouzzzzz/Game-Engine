"""Pixel Quest - Graphical version with pygame.

A fully playable 2D platformer with graphics rendered in a window.

Requirements:
    pip install pygame

Run:
    python pixel_quest_graphical.py
"""

import pygame
import sys
import math
import random
from enum import Enum


# ============================================================================
# CONSTANTS
# ============================================================================

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 500  # pixels per second squared
GROUND_LEVEL = SCREEN_HEIGHT - 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
PURPLE = (147, 51, 234)
GRAY = (128, 128, 128)


# ============================================================================
# GAME ENTITY
# ============================================================================

class Entity:
    """Game entity with physics."""

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vx = 0
        self.vy = 0

    def update(self, delta_time):
        """Update position."""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

    def draw(self, screen):
        """Draw entity."""
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)

    def get_rect(self):
        """Get bounding rect."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def distance_to(self, other):
        """Distance to another entity."""
        dx = (self.x + self.width / 2) - (other.x + other.width / 2)
        dy = (self.y + self.height / 2) - (other.y + other.height / 2)
        return math.sqrt(dx * dx + dy * dy)


# ============================================================================
# MAIN GAME
# ============================================================================

class PixelQuestGame:
    """Pixel Quest - Graphical platformer game."""

    def __init__(self):
        """Initialize game."""
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎮 Pixel Quest - Game Engine Studio")

        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.running = True
        self.game_over = False
        self.won = False

        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.frames = 0
        self.time_elapsed = 0

        # Create entities
        self.player = Entity(50, GROUND_LEVEL - 40, 30, 40, BLUE)
        self.player.on_ground = True
        self.player.speed = 300
        self.player.jump_force = 600

        self.enemies = []
        for i in range(3):
            enemy = Entity(
                200 + i * 300, GROUND_LEVEL - 30, 35, 35, RED
            )
            enemy.speed = 150
            enemy.direction = 1
            enemy.patrol_distance = 200
            enemy.start_x = enemy.x
            self.enemies.append(enemy)

        self.coins = []
        for i in range(5):
            coin = Entity(
                150 + i * 170, GROUND_LEVEL - 150, 20, 20, YELLOW
            )
            coin.collected = False
            coin.value = 10
            self.coins.append(coin)

        self.goal = Entity(SCREEN_WIDTH - 80, GROUND_LEVEL - 50, 60, 60, GREEN)

    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over or self.won:
                        self.__init__()  # Restart game
                    elif self.player.on_ground:
                        self.player.vy = -self.player.jump_force
                        self.player.on_ground = False

    def update(self, delta_time):
        """Update game state."""
        if self.game_over or self.won:
            return

        self.time_elapsed += delta_time

        # Player input
        keys = pygame.key.get_pressed()
        self.player.vx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

        # Player physics
        if not self.player.on_ground:
            self.player.vy += GRAVITY * delta_time
        else:
            self.player.vy = 0

        # Update player
        self.player.update(delta_time)

        # Ground collision
        if self.player.y >= GROUND_LEVEL:
            self.player.y = GROUND_LEVEL
            self.player.on_ground = True
        else:
            self.player.on_ground = False

        # Boundary check
        self.player.x = max(0, min(SCREEN_WIDTH - self.player.width, self.player.x))

        # Update enemies
        for enemy in self.enemies:
            enemy.vx = enemy.speed * enemy.direction
            enemy.update(delta_time)

            distance = abs(enemy.x - enemy.start_x)
            if distance > enemy.patrol_distance:
                enemy.direction *= -1

        # Check coin collection
        for coin in self.coins:
            if not coin.collected:
                if self.player.distance_to(coin) < 50:
                    coin.collected = True
                    self.score += coin.value

        # Check enemy collision
        for enemy in self.enemies:
            if self.player.distance_to(enemy) < 60:
                self.lives -= 1
                self.player.x = 50
                self.player.y = GROUND_LEVEL - 40
                if self.lives <= 0:
                    self.game_over = True

        # Check win condition
        if self.player.distance_to(self.goal) < 80:
            self.won = True

    def draw(self):
        """Render game."""
        self.screen.fill(BLACK)

        # Draw ground
        pygame.draw.line(self.screen, GRAY, (0, GROUND_LEVEL), (SCREEN_WIDTH, GROUND_LEVEL), 3)

        # Draw entities
        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for coin in self.coins:
            if not coin.collected:
                coin.draw(self.screen)

        self.goal.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.game_over or self.won:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display."""
        hud_text = f"Score: {self.score}  Lives: {self.lives}  Level: {self.level}  Time: {self.time_elapsed:.1f}s"
        text_surface = self.font_small.render(hud_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))

        coins_text = f"Coins: {sum(1 for c in self.coins if c.collected)}/5"
        coins_surface = self.font_small.render(coins_text, True, YELLOW)
        self.screen.blit(coins_surface, (10, 40))

        fps = int(self.clock.get_fps())
        fps_text = f"FPS: {fps}"
        fps_surface = self.font_small.render(fps_text, True, PURPLE)
        self.screen.blit(fps_surface, (SCREEN_WIDTH - 150, 10))

    def draw_game_over_screen(self):
        """Draw game over / win screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        if self.won:
            title = self.font_large.render("🎉 LEVEL COMPLETE!", True, GREEN)
        else:
            title = self.font_large.render("💀 GAME OVER", True, RED)

        score_text = self.font_medium.render(
            f"Final Score: {self.score}", True, WHITE
        )
        coins_text = self.font_medium.render(
            f"Coins: {sum(1 for c in self.coins if c.collected)}/5", True, YELLOW
        )
        restart_text = self.font_small.render(
            "Press SPACE to restart", True, WHITE
        )

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 450))

        self.screen.blit(title, title_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(coins_text, coins_rect)
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Main game loop."""
        print("\n" + "=" * 70)
        print("🎮 PIXEL QUEST - Graphical Game Engine Demo")
        print("=" * 70)
        print("\nGame Controls:")
        print("  LEFT/A  - Move left")
        print("  RIGHT/D - Move right")
        print("  SPACE   - Jump")
        print("  Goal: Collect coins and reach the green goal!")
        print("\n" + "=" * 70 + "\n")

        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            self.frames += 1

            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()
        print(f"\n✓ Game ended. Frames: {self.frames}, Avg FPS: {self.frames / self.time_elapsed:.1f}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    try:
        game = PixelQuestGame()
        game.run()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

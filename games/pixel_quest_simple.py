"""Pixel Quest - Simple Game Demo

Complete working game demonstrating:
- Player physics and jumping
- Enemy AI
- Collectibles
- Scoring system
- Game loop and rendering
- Performance metrics
"""

import math
import time
import random


class Entity:
    """Simple game entity."""

    def __init__(self, name, x=0, y=0, width=20, height=20):
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = width
        self.height = height
        self.active = True

    def update(self, delta_time):
        """Update position."""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

    def distance_to(self, other):
        """Distance to another entity."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


class PixelQuestGame:
    """Pixel Quest game."""

    GRAVITY = 9.8
    GROUND_Y = 400
    WORLD_WIDTH = 900
    WORLD_HEIGHT = 500

    def __init__(self):
        print("\n" + "=" * 70)
        print("🎮 PIXEL QUEST - A Game Built with Game Engine Studio")
        print("=" * 70)
        print("\nBuilding game world...\n")

        # Create entities
        self.player = Entity("Player", x=50, y=self.GROUND_Y, width=20, height=30)
        self.player.props = {
            'on_ground': True,
            'speed': 200,
            'jump_force': 400,
            'health': 3,
        }

        self.enemies = []
        for i in range(3):
            enemy = Entity(f"Enemy_{i}", x=150 + i * 200, y=self.GROUND_Y, width=24, height=24)
            enemy.props = {
                'direction': 1,
                'speed': 100,
                'patrol_dist': 150,
                'start_x': enemy.x,
            }
            self.enemies.append(enemy)

        self.coins = []
        for i in range(5):
            coin = Entity(f"Coin_{i}", x=100 + i * 150, y=self.GROUND_Y - 80, width=16, height=16)
            coin.props = {'collected': False, 'value': 10}
            self.coins.append(coin)

        self.goal = Entity("Goal", x=self.WORLD_WIDTH - 50, y=self.GROUND_Y, width=40, height=40)

        # Game state
        self.score = 0
        self.lives = 3
        self.coins_collected = 0
        self.level = 1
        self.game_over = False
        self.won = False

        # Performance tracking
        self.frames = 0
        self.frame_times = []
        self.last_time = time.time()

        print("✓ Game world created!")
        print(f"  - 1 Player")
        print(f"  - {len(self.enemies)} Enemies")
        print(f"  - {len(self.coins)} Coins")
        print(f"  - 1 Goal")
        print("\n" + "=" * 70)
        print("Instructions:")
        print("  LEFT/RIGHT: Move  |  SPACE: Jump  |  Goal: Reach the right side!")
        print("  Collect coins for points, avoid enemies!")
        print("=" * 70 + "\n")

        time.sleep(1)

    def handle_input(self):
        """Handle player input (simulated)."""
        # Simulate random input for demo
        move_left = random.random() < 0.15
        move_right = random.random() < 0.25
        jump = random.random() < 0.12

        return move_left, move_right, jump

    def update(self, delta_time):
        """Update game state."""
        if self.game_over or self.won:
            return

        # Handle input
        move_left, move_right, jump = self.handle_input()

        # Update player
        self.player.vx = 0
        if move_left:
            self.player.vx = -self.player.props['speed']
        if move_right:
            self.player.vx = self.player.props['speed']

        # Gravity
        if not self.player.props['on_ground']:
            self.player.vy += self.GRAVITY
        else:
            self.player.vy = 0

        # Jump
        if jump and self.player.props['on_ground']:
            self.player.vy = -self.player.props['jump_force']
            self.player.props['on_ground'] = False

        # Update position
        self.player.x += self.player.vx * delta_time
        self.player.y += self.player.vy * delta_time

        # Boundary check
        self.player.x = max(0, min(self.WORLD_WIDTH, self.player.x))

        # Ground collision
        if self.player.y >= self.GROUND_Y:
            self.player.y = self.GROUND_Y
            self.player.props['on_ground'] = True
        else:
            self.player.props['on_ground'] = False

        # Update enemies
        for enemy in self.enemies:
            props = enemy.props
            enemy.vx = props['speed'] * props['direction']
            enemy.x += enemy.vx * delta_time

            distance = abs(enemy.x - props['start_x'])
            if distance > props['patrol_dist']:
                props['direction'] *= -1

        # Check collisions
        self.check_collisions()

    def check_collisions(self):
        """Check all collisions."""
        # Coin collection
        for coin in self.coins:
            if coin.props['collected']:
                continue

            if self.player.distance_to(coin) < 25:
                coin.props['collected'] = True
                self.score += coin.props['value']
                self.coins_collected += 1

        # Enemy collision
        for enemy in self.enemies:
            if self.player.distance_to(enemy) < 30:
                self.lives -= 1
                # Reset player position
                self.player.x = 50
                self.player.y = self.GROUND_Y
                if self.lives <= 0:
                    self.game_over = True

        # Goal collision (win condition)
        if self.player.distance_to(self.goal) < 50:
            self.won = True

    def render(self):
        """Render game (text-based)."""
        # Calculate FPS
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time

        if delta > 0:
            fps = 1.0 / delta
            self.frame_times.append(delta)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)

        avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0

        # Status bar
        bar = f"[Score: {self.score:5d} | Lives: {self.lives} | " \
              f"Coins: {self.coins_collected}/5 | FPS: {avg_fps:5.1f}]"

        print(f"\r{bar}", end='', flush=True)

    def run(self, duration=30):
        """Run game loop."""
        print("Starting game...\n\n")
        print("[ GAME RUNNING ]" + " " * 50)

        start_time = time.time()
        frames = 0

        try:
            while time.time() - start_time < duration:
                if self.game_over or self.won:
                    break

                # Update
                delta_time = 0.016  # Fixed timestep
                self.update(delta_time)
                self.render()

                frames += 1
                time.sleep(delta_time)

        except KeyboardInterrupt:
            print("\n\nGame interrupted!")
            return

        # Game over screen
        print("\n\n" + "=" * 70)

        if self.won:
            print("🎉 LEVEL COMPLETE! You reached the goal!")
        elif self.game_over:
            print("💀 GAME OVER - No lives remaining!")
        else:
            print("⏱️  TIME UP!")

        print(f"\nFinal Results:")
        print(f"  Score: {self.score}")
        print(f"  Coins: {self.coins_collected}/5")
        print(f"  Level: {self.level}")
        print(f"  Frames: {frames}")

        if self.frame_times:
            avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
            min_fps = 1.0 / max(self.frame_times)
            max_fps = 1.0 / min(self.frame_times)

            print(f"\nPerformance:")
            print(f"  Average FPS: {avg_fps:.1f}")
            print(f"  Min FPS: {min_fps:.1f}")
            print(f"  Max FPS: {max_fps:.1f}")

        print("=" * 70)
        print("\n✓ Game complete!\n")


def main():
    """Main entry point."""
    game = PixelQuestGame()
    game.run(duration=30)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

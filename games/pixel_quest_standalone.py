"""Pixel Quest - A complete playable game built with Game Engine Studio.

Standalone version that demonstrates core game systems:
- Player movement and jumping (physics)
- Enemy AI (patrol)
- Collectibles (coins)
- Save/Load system
- NPC dialogue
- Performance monitoring
"""

import sys
from pathlib import Path
import math
import time
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.database import SaveManager
from engine.dialogue import DialogueManager, DialogueNode, DialogueType, DialogueChoice
from engine.project import ProjectManager
from engine.diagnostics import PerformanceMetrics, EventLogger
from engine.gd_lang import GDArray, GDDictionary, Type


# ============================================================================
# SIMPLE GAME COMPONENTS
# ============================================================================

class Entity:
    """Simple game entity."""

    def __init__(self, name, x=0, y=0):
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 20
        self.height = 20
        self.properties = {}

    def update(self, delta_time):
        """Update entity position."""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

    def distance_to(self, other):
        """Calculate distance to another entity."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


# ============================================================================
# MAIN GAME
# ============================================================================

class PixelQuestGame:
    """Pixel Quest - A complete game."""

    def __init__(self):
        print("\n" + "=" * 70)
        print("PIXEL QUEST - A Game Built with Game Engine Studio")
        print("=" * 70)
        print("\nInitializing game systems...\n")

        # Setup project
        self.project_mgr = ProjectManager()
        self.project = self.project_mgr.create_project("PixelQuest", "./games/projects")
        print(f"✓ Project initialized: {self.project.path}")

        # Setup game systems
        self.save_mgr = SaveManager(str(self.project.path))
        self.dialogue_mgr = DialogueManager(str(self.project.path))
        self.event_logger = EventLogger(str(self.project.path))
        self.metrics = PerformanceMetrics(max_history=300)

        # Game state using GD Language
        self.state = GDDictionary(value_type=Type.INT)
        self.state.set("score", 0)
        self.state.set("level", 1)
        self.state.set("lives", 3)
        self.state.set("coins_collected", 0)
        print("✓ GD Language dictionaries initialized")

        # Create entities
        self.player = Entity("Player", x=50, y=300)
        self.enemies = [
            Entity(f"Enemy_0", x=200, y=300),
            Entity(f"Enemy_1", x=350, y=300),
            Entity(f"Enemy_2", x=500, y=300),
        ]
        self.coins = [
            Entity(f"Coin_0", x=100, y=250),
            Entity(f"Coin_1", x=250, y=250),
            Entity(f"Coin_2", x=400, y=250),
            Entity(f"Coin_3", x=550, y=250),
            Entity(f"Coin_4", x=700, y=250),
        ]
        self.goal = Entity("Goal", x=800, y=300)
        self.goal.width = 40
        self.goal.height = 40

        # Initialize entity properties
        for coin in self.coins:
            coin.properties['collected'] = False
            coin.properties['value'] = 10

        for enemy in self.enemies:
            enemy.properties['direction'] = 1
            enemy.properties['patrol_distance'] = 150
            enemy.properties['speed'] = 100
            enemy.properties['start_x'] = enemy.x

        self.player.properties['on_ground'] = False
        self.player.properties['speed'] = 200
        self.player.properties['jump_force'] = 400

        print("✓ Game entities created")
        self.setup_dialogue()
        print("\n✓ Game initialized!\n")

    def setup_dialogue(self):
        """Setup NPC dialogue."""
        dialogue = self.dialogue_mgr.create_dialogue("welcome", "Welcome")

        start = DialogueNode(
            id="start",
            type=DialogueType.START,
            character="Elder",
            text="Welcome, brave adventurer! Collect coins and reach the goal!"
        )

        choice = DialogueNode(
            id="choice",
            type=DialogueType.CHOICE,
            character="You"
        )

        choice.add_choice(DialogueChoice(
            id="ready",
            text="I'm ready! Let's go!",
            next_node_id="tips",
            flag_set={"game_started": True}
        ))

        tips = DialogueNode(
            id="tips",
            type=DialogueType.DIALOGUE,
            character="Elder",
            text="Use LEFT/RIGHT to move, SPACE to jump. Avoid enemies!",
            next_node_id="end"
        )

        end = DialogueNode(
            id="end",
            type=DialogueType.END,
            character="Elder",
            text="Good luck, hero!"
        )

        for node in [start, choice, tips, end]:
            dialogue.add_node(node)

        self.dialogue_mgr.save_dialogue("welcome")

    def update(self, delta_time):
        """Update game state."""
        # Record frame
        self.metrics.record_frame(
            active_entities=len(self.enemies) + len(self.coins) + 2,
            draw_calls=100
        )

        # Update player physics
        self.update_player(delta_time)

        # Update enemies
        for enemy in self.enemies:
            self.update_enemy(enemy, delta_time)

        # Check collisions
        self.check_collisions()

    def update_player(self, delta_time):
        """Update player logic."""
        # Simulate input (simple pattern)
        import random
        move_right = random.random() < 0.3
        move_left = random.random() < 0.2
        should_jump = random.random() < 0.1

        # Movement
        self.player.vx = 0
        if move_left:
            self.player.vx = -self.player.properties['speed']
        if move_right:
            self.player.vx = self.player.properties['speed']

        # Gravity
        if not self.player.properties['on_ground']:
            self.player.vy += 9.8
        else:
            self.player.vy = 0

        # Jumping
        if should_jump and self.player.properties['on_ground']:
            self.player.vy = -self.player.properties['jump_force']
            self.player.properties['on_ground'] = False

        # Update position
        self.player.x += self.player.vx * delta_time
        self.player.y += self.player.vy * delta_time

        # Boundaries
        self.player.x = max(0, min(800, self.player.x))

        # Ground collision
        if self.player.y >= 400:
            self.player.y = 400
            self.player.properties['on_ground'] = True
        else:
            self.player.properties['on_ground'] = False

    def update_enemy(self, enemy, delta_time):
        """Update enemy patrol."""
        props = enemy.properties

        # Patrol movement
        enemy.vx = props['speed'] * props['direction']
        enemy.x += enemy.vx * delta_time

        # Change direction
        distance = abs(enemy.x - props['start_x'])
        if distance > props['patrol_distance']:
            props['direction'] *= -1

    def check_collisions(self):
        """Check collisions."""
        # Check coin collection
        for coin in self.coins:
            if coin.properties['collected']:
                continue

            if self.player.distance_to(coin) < 25:
                coin.properties['collected'] = True
                score_increase = coin.properties['value']
                current_score = self.state.get("score", 0)
                self.state.set("score", current_score + score_increase)

                coins = self.state.get("coins_collected", 0)
                self.state.set("coins_collected", coins + 1)

                self.event_logger.info("Coin collected", {
                    'score': self.state.get("score", 0)
                })

        # Check enemy collision
        for enemy in self.enemies:
            if self.player.distance_to(enemy) < 30:
                lives = self.state.get("lives", 3)
                self.state.set("lives", lives - 1)
                self.event_logger.warning("Hit by enemy", {
                    'lives_remaining': self.state.get("lives", 0)
                })
                # Reset player
                self.player.x = 50
                self.player.y = 300

        # Check win condition
        if self.player.distance_to(self.goal) < 50:
            return "WIN"

        if self.state.get("lives", 0) <= 0:
            return "LOSE"

        return None

    def render(self):
        """Render game state."""
        score = self.state.get("score", 0)
        lives = self.state.get("lives", 3)
        coins = self.state.get("coins_collected", 0)
        fps = self.metrics.get_average_fps()

        print(f"\r[Score: {score:5d} | Lives: {lives} | " +
              f"Coins: {coins}/5 | FPS: {fps:5.1f}]", end='', flush=True)

    def play(self, duration=30):
        """Run game loop."""
        # Show welcome dialogue
        current = self.dialogue_mgr.start_dialogue("welcome")
        print(f"\n{current.character}: {current.text}\n")

        choices = self.dialogue_mgr.get_current_choices()
        for choice in choices:
            print(f"  > {choice.text}")

        self.dialogue_mgr.advance_dialogue(choice_id="ready")
        print()

        # Game loop
        start_time = time.time()
        last_time = start_time
        frames = 0
        result = None

        print("[Score:     0 | Lives: 3 | Coins: 0/5 | FPS:   0.0]", end='')

        try:
            while time.time() - start_time < duration and result is None:
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                self.update(delta_time)
                result = self.check_collisions()
                self.render()

                frames += 1
                time.sleep(0.016)  # ~60 FPS

        except KeyboardInterrupt:
            print("\n\nGame interrupted!")
            return

        # Game over screen
        print("\n\n" + "=" * 70)

        if result == "WIN":
            print("🎉 LEVEL COMPLETE! You reached the goal!")
        elif result == "LOSE":
            print("💀 GAME OVER - No lives remaining!")
        else:
            print("⏱️  TIME UP!")

        final_score = self.state.get("score", 0)
        final_coins = self.state.get("coins_collected", 0)

        print(f"\nFinal Score: {final_score}")
        print(f"Coins Collected: {final_coins}/5")
        print(f"Frames Rendered: {frames}")
        print(f"Average FPS: {self.metrics.get_average_fps():.1f}")
        print(f"Peak Memory: {self.metrics.get_peak_memory():.1f} MB")

        # Performance stats
        stats = self.metrics.to_dict()
        print(f"\nPerformance Summary:")
        print(f"  Min FPS: {stats['min_fps']:.1f}")
        print(f"  Max FPS: {stats['max_fps']:.1f}")
        print(f"  Avg CPU: {stats['average_cpu_percent']:.1f}%")

        print("=" * 70)

        # Save final state
        self.save_progress()
        print("\n✓ Game progress saved to encrypted slot\n")

    def save_progress(self):
        """Save game progress."""
        game_state = {
            'score': self.state.get("score", 0),
            'level': self.state.get("level", 1),
            'lives': self.state.get("lives", 3),
            'coins': self.state.get("coins_collected", 0),
            'timestamp': time.time()
        }

        self.save_mgr.save_game(slot=1, game_state=game_state, encrypt=True)
        self.event_logger.info("Game progress saved", game_state)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    try:
        game = PixelQuestGame()
        game.play(duration=30)
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

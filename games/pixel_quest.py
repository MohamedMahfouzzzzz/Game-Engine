"""Pixel Quest - A complete playable game built with Game Engine Studio.

A simple 2D platformer demonstrating:
- Player movement and jumping
- Enemy AI
- Collectibles
- Save/Load system
- NPC dialogue
- Physics and collision
"""

import sys
from pathlib import Path
import math
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.core import Engine, Scene, Entity, Component
from engine.components import Transform, Sprite
from engine.database import SaveManager
from engine.dialogue import DialogueManager, DialogueNode, DialogueType, DialogueChoice
from engine.project import ProjectManager
from engine.diagnostics import PerformanceMetrics, EventLogger


# ============================================================================
# GAME COMPONENTS
# ============================================================================

class Velocity(Component):
    """Velocity component for movement."""

    def __init__(self, vx=0, vy=0):
        self.vx = vx
        self.vy = vy


class Physics(Component):
    """Simple physics component with gravity."""

    def __init__(self, mass=1.0, gravity=9.8, friction=0.1):
        self.mass = mass
        self.gravity = gravity
        self.friction = friction
        self.on_ground = False


class Collider(Component):
    """Collision component."""

    def __init__(self, width=32, height=32, is_trigger=False):
        self.width = width
        self.height = height
        self.is_trigger = is_trigger


class PlayerController(Component):
    """Player input and movement."""

    def __init__(self, speed=200, jump_force=400):
        self.speed = speed
        self.jump_force = jump_force
        self.is_jumping = False


class EnemyAI(Component):
    """Simple enemy AI."""

    def __init__(self, patrol_distance=200, speed=100):
        self.patrol_distance = patrol_distance
        self.speed = speed
        self.direction = 1
        self.start_x = 0


class Collectible(Component):
    """Collectible item (coin)."""

    def __init__(self, value=10):
        self.value = value
        self.collected = False


class HealthComponent(Component):
    """Health/Lives."""

    def __init__(self, health=3):
        self.health = health
        self.max_health = health


# ============================================================================
# GAME LOGIC
# ============================================================================

class GameState:
    """Global game state."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.score = 0
        self.level = 1
        self.lives = 3
        self.coins_collected = 0
        self.finished = False
        self.save_manager = SaveManager(str(project_path))
        self.dialogue_manager = DialogueManager(str(project_path))
        self.event_logger = EventLogger(str(project_path))
        self.metrics = PerformanceMetrics()

    def save_progress(self, slot=1):
        """Save game progress."""
        state = {
            'score': self.score,
            'level': self.level,
            'lives': self.lives,
            'coins': self.coins_collected,
            'timestamp': time.time()
        }
        self.save_manager.save_game(slot, state, encrypt=True)
        self.event_logger.info("Game saved", {'slot': slot, 'score': self.score})

    def load_progress(self, slot=1):
        """Load game progress."""
        try:
            state, _ = self.save_manager.load_game(slot)
            self.score = state.get('score', 0)
            self.level = state.get('level', 1)
            self.lives = state.get('lives', 3)
            self.coins_collected = state.get('coins', 0)
            self.event_logger.info("Game loaded", {'slot': slot})
            return True
        except:
            return False


class PixelQuestGame:
    """Main game class."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.game_state = GameState(str(project_path))
        self.entities = {}
        self.setup_game()

    def setup_game(self):
        """Initialize game entities."""
        print("\n" + "=" * 60)
        print("PIXEL QUEST - A Game Built with Game Engine Studio")
        print("=" * 60 + "\n")

        # Create player
        self.player = Entity("Player")
        self.player.add(Transform(position=(50, 300)))
        self.player.add(Velocity())
        self.player.add(Physics())
        self.player.add(Collider(width=20, height=32))
        self.player.add(PlayerController())
        self.player.add(HealthComponent(health=3))
        self.entities["player"] = self.player

        # Create enemies
        for i in range(3):
            enemy = Entity(f"Enemy_{i}")
            enemy.add(Transform(position=(200 + i * 150, 300)))
            enemy.add(Velocity())
            enemy.add(Physics())
            enemy.add(Collider(width=24, height=24))
            enemy.add(EnemyAI(patrol_distance=150, speed=100))
            self.entities[f"enemy_{i}"] = enemy

        # Create coins
        for i in range(5):
            coin = Entity(f"Coin_{i}")
            coin.add(Transform(position=(100 + i * 150, 250)))
            coin.add(Collider(width=16, height=16, is_trigger=True))
            coin.add(Collectible(value=10))
            self.entities[f"coin_{i}"] = coin

        # Create goal
        goal = Entity("Goal")
        goal.add(Transform(position=(800, 300)))
        goal.add(Collider(width=40, height=40, is_trigger=True))
        self.entities["goal"] = goal

        self.setup_dialogue()
        print("✓ Game initialized with player, enemies, coins, and goal\n")

    def setup_dialogue(self):
        """Setup NPC dialogue."""
        # Create welcome dialogue
        dialogue = self.game_state.dialogue_manager.create_dialogue(
            "welcome",
            "Welcome to Pixel Quest"
        )

        start = DialogueNode(
            id="start",
            type=DialogueType.START,
            character="Elder",
            text="Welcome, brave adventurer! Collect the coins and reach the goal!"
        )

        choice_node = DialogueNode(
            id="choice",
            type=DialogueType.CHOICE,
            character="You"
        )

        choice_node.add_choice(DialogueChoice(
            id="ready",
            text="I'm ready! Let's go!",
            next_node_id="end",
            flag_set={"game_started": True}
        ))

        end = DialogueNode(
            id="end",
            type=DialogueType.END,
            character="Elder",
            text="Good luck! Use arrow keys to move, space to jump!"
        )

        for node in [start, choice_node, end]:
            dialogue.add_node(node)

        self.game_state.dialogue_manager.save_dialogue("welcome")

    def update(self, delta_time):
        """Update game state."""
        # Record frame metrics
        self.game_state.metrics.record_frame(
            active_entities=len(self.entities),
            draw_calls=len(self.entities)
        )

        # Update player
        self.update_player(delta_time)

        # Update enemies
        self.update_enemies(delta_time)

        # Check collisions
        self.check_collisions()

        # Check win condition
        if self.check_win_condition():
            self.game_state.finished = True

    def update_player(self, delta_time):
        """Update player logic."""
        player = self.player
        transform = player.components.get('Transform')
        velocity = player.components.get('Velocity')
        physics = player.components.get('Physics')
        controller = player.components.get('PlayerController')

        if not all([transform, velocity, physics, controller]):
            return

        # Simple keyboard input simulation
        # In real game, would read actual input
        keys = self.get_input()

        # Horizontal movement
        velocity.vx = 0
        if keys.get('left'):
            velocity.vx = -controller.speed
        if keys.get('right'):
            velocity.vx = controller.speed

        # Apply gravity
        if not physics.on_ground:
            velocity.vy += physics.gravity
        else:
            velocity.vy = 0

        # Jumping
        if keys.get('jump') and physics.on_ground:
            velocity.vy = -controller.jump_force
            physics.on_ground = False

        # Update position
        transform.position[0] += velocity.vx * delta_time
        transform.position[1] += velocity.vy * delta_time

        # Boundary checking
        transform.position[0] = max(0, min(800, transform.position[0]))

        # Ground collision
        if transform.position[1] >= 400:
            transform.position[1] = 400
            physics.on_ground = True
        else:
            physics.on_ground = False

    def update_enemies(self, delta_time):
        """Update enemy AI."""
        for entity in self.entities.values():
            if "Enemy" not in entity.name:
                continue

            transform = entity.components.get('Transform')
            velocity = entity.components.get('Velocity')
            ai = entity.components.get('EnemyAI')

            if not all([transform, velocity, ai]):
                continue

            ai.start_x = ai.start_x or transform.position[0]

            # Patrol movement
            velocity.vx = ai.speed * ai.direction

            # Change direction at patrol limits
            distance = abs(transform.position[0] - ai.start_x)
            if distance > ai.patrol_distance:
                ai.direction *= -1

            # Update position
            transform.position[0] += velocity.vx * delta_time

    def check_collisions(self):
        """Check collisions between entities."""
        player = self.player
        player_transform = player.components.get('Transform')
        player_collider = player.components.get('Collider')

        if not all([player_transform, player_collider]):
            return

        # Check coin collection
        for entity in self.entities.values():
            if "Coin" not in entity.name:
                continue

            collectible = entity.components.get('Collectible')
            if collectible and collectible.collected:
                continue

            transform = entity.components.get('Transform')
            if self.check_collision(player_transform, transform, 20):
                if collectible and not collectible.collected:
                    collectible.collected = True
                    self.game_state.score += collectible.value
                    self.game_state.coins_collected += 1
                    self.game_state.event_logger.info(
                        "Coin collected",
                        {'score': self.game_state.score}
                    )

        # Check enemy collision
        for entity in self.entities.values():
            if "Enemy" not in entity.name:
                continue

            transform = entity.components.get('Transform')
            if self.check_collision(player_transform, transform, 30):
                health = player.components.get('HealthComponent')
                if health:
                    health.health -= 1
                    self.game_state.lives -= 1
                    self.game_state.event_logger.warning(
                        "Hit by enemy",
                        {'lives_remaining': self.game_state.lives}
                    )
                    if health.health <= 0:
                        self.game_state.finished = True

    def check_win_condition(self):
        """Check if player reached goal."""
        goal = self.entities.get("goal")
        if not goal:
            return False

        player = self.player
        player_transform = player.components.get('Transform')
        goal_transform = goal.components.get('Transform')

        if player_transform and goal_transform:
            return self.check_collision(player_transform, goal_transform, 50)

        return False

    def check_collision(self, transform1, transform2, distance_threshold=30):
        """Simple distance-based collision."""
        dx = transform1.position[0] - transform2.position[0]
        dy = transform1.position[1] - transform2.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < distance_threshold

    def get_input(self):
        """Get player input (simulated for demo)."""
        # In a real game, this would read actual keyboard input
        # For now, return a simple pattern
        import random
        return {
            'left': random.random() < 0.2,
            'right': random.random() < 0.3,
            'jump': random.random() < 0.1,
        }

    def render(self):
        """Render game state (text-based for demo)."""
        print(f"\r[Score: {self.game_state.score:4d} | " +
              f"Lives: {self.game_state.lives} | " +
              f"Coins: {self.game_state.coins_collected} | " +
              f"FPS: {self.game_state.metrics.get_average_fps():.0f}]", end='')

    def play(self, duration=30):
        """Run game loop."""
        print("\nStarting game...\n")

        # Show welcome dialogue
        current = self.game_state.dialogue_manager.start_dialogue("welcome")
        print(f"\n{current.character}: {current.text}\n")

        choices = self.game_state.dialogue_manager.get_current_choices()
        for choice in choices:
            print(f"  > {choice.text}")

        self.game_state.dialogue_manager.advance_dialogue(choice_id="ready")
        print()

        # Game loop
        start_time = time.time()
        last_time = start_time
        frames = 0

        print("Game running (press Ctrl+C to exit)...\n")
        print("[Score: 0000 | Lives: 3 | Coins: 0 | FPS: 60]", end='')

        try:
            while time.time() - start_time < duration and not self.game_state.finished:
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                self.update(delta_time)
                self.render()

                frames += 1
                time.sleep(0.016)  # ~60 FPS

        except KeyboardInterrupt:
            pass

        # Game over
        print("\n\n" + "=" * 60)
        if self.game_state.finished:
            if self.check_win_condition():
                print("🎉 LEVEL COMPLETE!")
                self.game_state.level += 1
            else:
                print("💀 GAME OVER - Lives Lost!")

        print(f"Final Score: {self.game_state.score}")
        print(f"Coins Collected: {self.game_state.coins_collected}")
        print(f"Level: {self.game_state.level}")
        print(f"Frames: {frames}")
        print(f"Average FPS: {self.game_state.metrics.get_average_fps():.1f}")
        print("=" * 60 + "\n")

        # Save progress
        self.game_state.save_progress(slot=1)
        print("✓ Game progress saved\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    # Create project
    print("Initializing Game Engine...")
    project_mgr = ProjectManager()
    project = project_mgr.create_project("PixelQuest", "./games/projects")
    print(f"✓ Project created: {project.path}\n")

    # Create and run game
    game = PixelQuestGame(str(project.path))

    # Play game (30 second demo)
    game.play(duration=30)

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""Example: Using the signal system for decoupled communication."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.signals import Signal, SignalManager
from engine.threading import ThreadPool


class Player:
    """Player character with signals."""
    
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.score = 0
        self.position = (0, 0)
        
        # Define signals
        self.health_changed = Signal(int)  # New health value
        self.score_changed = Signal(int)  # New score value
        self.position_changed = Signal(int, int)  # New x, y
        self.died = Signal()  # No arguments
        self.respawned = Signal(int, int)  # Respawn position
    
    def take_damage(self, amount):
        """Player takes damage."""
        old_health = self.health
        self.health = max(0, self.health - amount)
        self.health_changed.emit(self.health)
        
        if self.health == 0 and old_health > 0:
            self.died.emit()
    
    def heal(self, amount):
        """Player heals."""
        self.health = min(100, self.health + amount)
        self.health_changed.emit(self.health)
    
    def add_score(self, points):
        """Add score to player."""
        self.score += points
        self.score_changed.emit(self.score)
    
    def move_to(self, x, y):
        """Move player to position."""
        self.position = (x, y)
        self.position_changed.emit(x, y)
    
    def respawn(self, x, y):
        """Respawn player at position."""
        self.health = 100
        self.position = (x, y)
        self.respawned.emit(x, y)


class Enemy:
    """Enemy that responds to player signals."""
    
    def __init__(self, name, x, y):
        self.name = name
        self.position = (x, y)
        self.alive = True
    
    def on_player_died(self):
        """React to player death."""
        print(f"[{self.name}] Player died! Celebrating!")
        self.position = (self.position[0] + 10, self.position[1])
    
    def on_player_respawned(self, x, y):
        """React to player respawn."""
        print(f"[{self.name}] Player respawned at ({x}, {y})!")
        # Move towards player
        dx = x - self.position[0]
        dy = y - self.position[1]
        self.position = (self.position[0] + dx//2, self.position[1] + dy//2)


class UI:
    """UI system that displays game information."""
    
    def __init__(self):
        self.health_bar = 100
        self.score_text = "Score: 0"
        self.position_text = "Position: (0, 0)"
    
    def update_health(self, health):
        """Update health display."""
        self.health_bar = health
        print(f"[UI] Health: {'█' * (health//10)}{'░' * (10 - health//10)} ({health}/100)")
    
    def update_score(self, score):
        """Update score display."""
        self.score_text = f"Score: {score}"
        print(f"[UI] {self.score_text}")
    
    def update_position(self, x, y):
        """Update position display."""
        self.position_text = f"Position: ({x}, {y})"
        print(f"[UI] {self.position_text}")
    
    def show_death_message(self):
        """Show death message."""
        print("[UI] 💀 YOU DIED! 💀")
    
    def show_respawn_message(self, x, y):
        """Show respawn message."""
        print(f"[UI] ✨ Respawned at ({x}, {y})! ✨")


class AudioSystem:
    """Audio system for game sounds."""
    
    def play_damage_sound(self, health):
        """Play damage sound."""
        if health < 30:
            print("[Audio] 🔊 CRITICAL HEALTH SOUND!")
        elif health < 60:
            print("[Audio] 🔊 Damage sound")
        else:
            print("[Audio] 🔊 Light damage sound")
    
    def play_heal_sound(self):
        """Play heal sound."""
        print("[Audio] 🔊 Healing sound")
    
    def play_score_sound(self, score):
        """Play score sound."""
        if score % 100 == 0 and score > 0:
            print("[Audio] 🔊 MILESTONE REACHED!")
        else:
            print("[Audio] 🔊 Score increase")
    
    def play_death_sound(self):
        """Play death sound."""
        print("[Audio] 💀 DEATH SOUND!")
    
    def play_respawn_sound(self):
        """Play respawn sound."""
        print("[Audio] ✨ RESPAWN SOUND!")


class Game:
    """Main game class using signal manager."""
    
    def __init__(self):
        self.manager = SignalManager()
        self.player = None
        self.enemies = []
        self.ui = UI()
        self.audio = AudioSystem()
        self.running = True
        
        self.setup_signals()
    
    def setup_signals(self):
        """Setup global signals and connections."""
        # Add global signals
        self.manager.add_signal('game_over', Signal())
        self.manager.add_signal('level_complete', Signal(int))
        self.manager.add_signal('enemy_spawned', Signal(str, int, int))
        
        # Connect game over handler
        self.manager.connect('game_over', self.on_game_over)
    
    def create_player(self, name):
        """Create player and connect signals."""
        self.player = Player(name)
        
        # Connect UI signals
        self.player.health_changed.connect(self.ui.update_health)
        self.player.score_changed.connect(self.ui.update_score)
        self.player.position_changed.connect(self.ui.update_position)
        self.player.died.connect(self.ui.show_death_message)
        self.player.respawned.connect(self.ui.show_respawn_message)
        
        # Connect audio signals
        self.player.health_changed.connect(self.audio.play_damage_sound)
        self.player.score_changed.connect(self.audio.play_score_sound)
        self.player.died.connect(self.audio.play_death_sound)
        self.player.respawned.connect(self.audio.play_respawn_sound)
    
    def spawn_enemy(self, name, x, y):
        """Spawn enemy and connect to player signals."""
        enemy = Enemy(name, x, y)
        self.enemies.append(enemy)
        
        # Connect to player signals
        if self.player:
            self.player.died.connect(enemy.on_player_died)
            self.player.respawned.connect(enemy.on_player_respawned)
        
        # Emit global signal
        self.manager.emit('enemy_spawned', name, x, y)
        
        return enemy
    
    def on_game_over(self):
        """Handle game over."""
        print("\n[GAME] GAME OVER!")
        self.running = False
    
    def simulate_gameplay(self):
        """Simulate some gameplay."""
        print("\n=== SIMULATING GAMEPLAY ===\n")
        
        # Player takes damage
        print("Player takes 20 damage...")
        self.player.take_damage(20)
        time.sleep(0.5)
        
        # Player moves
        print("Player moves to (10, 15)...")
        self.player.move_to(10, 15)
        time.sleep(0.5)
        
        # Player gains score
        print("Player gains 50 points...")
        self.player.add_score(50)
        time.sleep(0.5)
        
        # More damage
        print("Player takes 50 damage...")
        self.player.take_damage(50)
        time.sleep(0.5)
        
        # Player heals
        print("Player heals 30 HP...")
        self.player.heal(30)
        time.sleep(0.5)
        
        # Player dies
        print("Player takes 80 damage (fatal)...")
        self.player.take_damage(80)
        time.sleep(0.5)
        
        # Player respawns
        print("Player respawns at (5, 5)...")
        self.player.respawn(5, 5)
        time.sleep(0.5)
        
        # Final score
        print("Player gains 100 points...")
        self.player.add_score(100)
        time.sleep(0.5)
        
        # Game over
        self.manager.emit('game_over')


def demonstrate_signal_manager():
    """Demonstrate SignalManager features."""
    print("\n=== SIGNAL MANAGER DEMO ===\n")
    
    manager = SignalManager()
    
    # Create signal groups
    ui_group = manager.create_group('ui')
    game_group = manager.create_group('game')
    
    # Add signals to groups
    ui_group.add_signal('button_clicked', Signal(str))
    ui_group.add_signal('menu_opened', Signal(str))
    
    game_group.add_signal('player_joined', Signal(str))
    game_group.add_signal('player_left', Signal(str))
    
    # Connect handlers
    def on_button_click(button_id):
        print(f"[UI] Button clicked: {button_id}")
    
    def on_player_join(name):
        print(f"[Game] {name} joined the game")
    
    def on_player_leave(name):
        print(f"[Game] {name} left the game")
    
    manager.connect('ui.button_clicked', on_button_click)
    manager.connect('game.player_joined', on_player_join)
    manager.connect('game.player_left', on_player_leave)
    
    # Emit signals
    manager.emit('ui.button_clicked', 'start_button')
    manager.emit('game.player_joined', 'Alice')
    manager.emit('game.player_joined', 'Bob')
    manager.emit('ui.button_clicked', 'quit_button')
    manager.emit('game.player_left', 'Alice')
    
    # Show signal info
    print(f"\nSignal groups: {list(manager.get_groups().keys())}")
    print(f"UI signals: {ui_group.get_signal_names()}")
    print(f"Game signals: {game_group.get_signal_names()}")


def demonstrate_threaded_signals():
    """Demonstrate signals with threading."""
    print("\n=== THREADED SIGNALS DEMO ===\n")
    
    manager = SignalManager()
    pool = ThreadPool(max_workers=2)
    
    # Add signal
    manager.add_signal('task_completed', Signal(str, int))
    
    results = []
    
    def handle_task_complete(name, result):
        results.append((name, result))
        print(f"[Handler] Task '{name}' completed with result: {result}")
    
    manager.connect('task_completed', handle_task_complete)
    
    def long_task(name, duration):
        """Simulate long task."""
        time.sleep(duration)
        # Emit signal from thread
        manager.emit('task_completed', name, duration * 10)
        return name
    
    # Submit tasks
    print("Submitting tasks to thread pool...")
    futures = []
    tasks = [
        ('Task A', 0.5),
        ('Task B', 0.3),
        ('Task C', 0.7),
        ('Task D', 0.2)
    ]
    
    for name, duration in tasks:
        future = pool.submit(long_task, name, duration)
        futures.append(future)
    
    # Wait for completion
    for future in futures:
        future.result()
    
    pool.shutdown()
    
    print(f"\nAll results collected: {len(results)} tasks completed")


def main():
    """Main demonstration."""
    print("SIGNAL SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Basic signal demo
    print("\n1. Basic Signal Demo")
    print("-" * 30)
    
    game = Game()
    game.create_player("Hero")
    game.spawn_enemy("Goblin", 20, 20)
    game.spawn_enemy("Orc", 30, 30)
    
    game.simulate_gameplay()
    
    # Signal manager demo
    demonstrate_signal_manager()
    
    # Threaded signals demo
    demonstrate_threaded_signals()
    
    print("\n" + "="*60)
    print("Signal system demonstration complete!")


if __name__ == '__main__':
    main()

# /**************************************************************************/
# /*  game_loop.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional

from engine.core.node_base import Node
from engine.core.project import Project
from engine.core.scene import Scene
from engine.core.signals import SignalBus
from engine.scripting.abi import ScriptContext
from engine.scripting.host import ScriptHost

import logging


logger = logging.getLogger(__name__)



class LoopState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


@dataclass
class RuntimeConfig:
    fixed_dt: float = 1 / 60.0
    max_steps: int = 600
    target_fps: float = 60.0


class FPSCounter:
    """Simple FPS counter with moving average."""

    def __init__(self, window_size: int = 60) -> None:
        self.window_size = window_size
        self.frame_times: List[float] = []
        self.last_time = time.perf_counter()

    def tick(self) -> float:
        """Record a frame and return current FPS."""
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now

        self.frame_times.append(dt)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)

        if not self.frame_times:
            return 0.0
        avg_dt = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_dt if avg_dt > 0 else 0.0

    def reset(self) -> None:
        self.frame_times.clear()
        self.last_time = time.perf_counter()


class GameRuntime:
    def __init__(self, project: Project, config: Optional[RuntimeConfig] = None) -> None:
        self.project = project
        self.config = config or RuntimeConfig()
        self.script_host = ScriptHost()
        self._running = False

    def _walk_nodes(self, node: Node):
        stack = [node]
        while stack:
            n = stack.pop()
            yield n
            for child in getattr(n, "children", []):
                stack.append(child)

    def _run_init(self) -> None:
        scene = self.project.active_scene
        if not scene:
            return
        for node in self._walk_nodes(scene.root):
            script = getattr(node, "script", None)
            if script and hasattr(script, "on_init"):
                script.on_init()

    def _run_update(self, dt: float) -> None:
        scene = self.project.active_scene
        if not scene:
            return
        for node in self._walk_nodes(scene.root):
            script = getattr(node, "script", None)
            if script and hasattr(script, "on_update"):
                script.on_update(dt)

            # Optional: run script source if attached via properties
            language = node.get_property("script_language")
            source = node.get_property("script_source")
            if language and source:
                ctx = ScriptContext(node_id=node.id, scene_id=scene.id, properties=node.properties)
                self.script_host.execute(language, source, ctx)

    def _run_teardown(self) -> None:
        scene = self.project.active_scene
        if not scene:
            return
        for node in self._walk_nodes(scene.root):
            script = getattr(node, "script", None)
            if script and hasattr(script, "on_teardown"):
                script.on_teardown()

    def run(self) -> None:
        self._running = True
        self._run_init()
        steps = 0
        last = time.perf_counter()
        try:
            while self._running and steps < self.config.max_steps:
                now = time.perf_counter()
                dt = now - last
                last = now
                self._run_update(dt)
                steps += 1
                time.sleep(max(0.0, self.config.fixed_dt - dt))
        finally:
            self._run_teardown()

    def stop(self) -> None:
        self._running = False


class GameLoop:
    """Main game loop for editor integration with start/pause/stop controls."""

    def __init__(self, project: Optional[Project] = None, config: Optional[RuntimeConfig] = None) -> None:
        self.project = project
        self.config = config or RuntimeConfig()
        self.state = LoopState.STOPPED
        self.fps_counter = FPSCounter()
        self.script_host = ScriptHost()
        self.signals = SignalBus()

        # Callbacks for UI integration
        self.on_update: Optional[Callable[[float], None]] = None
        self.on_render: Optional[Callable[[], None]] = None
        self.on_fps_changed: Optional[Callable[[float], None]] = None

        self._last_time = time.perf_counter()
        self._accumulated_time = 0.0
        self._running = False

    def start(self) -> None:
        """Start the game loop."""
        if self.state == LoopState.RUNNING:
            return
        self.state = LoopState.RUNNING
        self._running = True
        self._last_time = time.perf_counter()
        self.fps_counter.reset()
        self.signals.emit("loop_started")

    def pause(self) -> None:
        """Pause the game loop."""
        if self.state == LoopState.RUNNING:
            self.state = LoopState.PAUSED
            self.signals.emit("loop_paused")

    def resume(self) -> None:
        """Resume a paused game loop."""
        if self.state == LoopState.PAUSED:
            self.state = LoopState.RUNNING
            self._last_time = time.perf_counter()
            self.signals.emit("loop_resumed")

    def stop(self) -> None:
        """Stop the game loop completely."""
        self.state = LoopState.STOPPED
        self._running = False
        self.signals.emit("loop_stopped")

    def toggle_pause(self) -> None:
        """Toggle between running and paused states."""
        if self.state == LoopState.RUNNING:
            self.pause()
        elif self.state == LoopState.PAUSED:
            self.resume()

    def step(self) -> None:
        """Execute a single frame (for paused mode frame stepping)."""
        if self.state == LoopState.STOPPED:
            return
        self._update_frame()

    def _update_frame(self) -> None:
        """Process one frame update."""
        now = time.perf_counter()
        dt = now - self._last_time
        self._last_time = now

        # Update FPS counter
        fps = self.fps_counter.tick()
        if self.on_fps_changed:
            self.on_fps_changed(fps)

        # Run update callback
        if self.on_update:
            self.on_update(dt)

        # Run scripts if project is available
        if self.project and self.project.active_scene:
            self._run_scripts(dt)

        # Run render callback
        if self.on_render:
            self.on_render()

    def _run_scripts(self, dt: float) -> None:
        """Run scripts on all nodes in the active scene."""
        scene = self.project.active_scene
        if not scene:
            return

        def walk_nodes(node: Node):
            stack = [node]
            while stack:
                n = stack.pop()
                yield n
                for child in getattr(n, "children", []):
                    stack.append(child)

        for node in walk_nodes(scene.root):
            language = node.get_property("script_language")
            source = node.get_property("script_source")
            if language and source:
                ctx = ScriptContext(
                    node_id=node.id,
                    scene_id=scene.id,
                    properties=node.properties
                )
                try:
                    self.script_host.execute(language, source, ctx)
                except Exception as e:
                    # Log error but don't crash the loop
                    print(f"Script error on node {node.name}: {e}")

    def run_single_frame(self) -> float:
        """Run a single frame and return the FPS."""
        if self.state != LoopState.RUNNING:
            return 0.0
        self._update_frame()
        return self.fps_counter.tick()

    @property
    def is_running(self) -> bool:
        return self.state == LoopState.RUNNING

    @property
    def is_paused(self) -> bool:
        return self.state == LoopState.PAUSED


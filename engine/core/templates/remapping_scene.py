# /**************************************************************************/
# /*  remapping_scene.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Remapping Scene - ready-made scene for input remapping."""

from engine.core.scene import Scene
from engine.core.node_base import Node
from engine.core.nodes import Node2D, Label, Button, Panel
from engine.core.controllers.input_controller import InputController, InputAction

import logging


logger = logging.getLogger(__name__)



class RemappingScene(Scene):
    """Ready-made scene for remapping game controls."""

    def __init__(self):
        super().__init__("Input Remapping")
        self._input_controller = InputController()
        self._current_action_index = 0
        self._waiting_for_input = False
        self._actions_to_remap = [
            InputAction.MOVE_UP,
            InputAction.MOVE_DOWN,
            InputAction.MOVE_LEFT,
            InputAction.MOVE_RIGHT,
            InputAction.JUMP,
            InputAction.ATTACK,
            InputAction.INTERACT,
            InputAction.CANCEL,
        ]

    def create_scene_structure(self) -> None:
        """Create the scene structure for input remapping."""
        # Background panel
        bg_panel = Panel()
        bg_panel.set_position(0, 0)
        bg_panel.set_size(800, 600)
        bg_panel.set_property("background_color", (30, 30, 40, 255))
        self.root.add_child(bg_panel)

        # Title label
        title_label = Label()
        title_label.set_property("text", "Input Remapping")
        title_label.set_position(300, 50)
        title_label.set_property("font_size", 24)
        bg_panel.add_child(title_label)

        # Instructions label
        instructions = Label()
        instructions.set_property("text", "Press any key to remap action")
        instructions.set_position(250, 100)
        instructions.set_property("font_size", 14)
        bg_panel.add_child(instructions)

        # Create action buttons for each action
        y_offset = 150
        for action in self._actions_to_remap:
            # Action label
            action_label = Label()
            action_label.set_property("text", action.value.replace("_", " ").title())
            action_label.set_position(100, y_offset)
            action_label.set_property("font_size", 16)
            bg_panel.add_child(action_label)

            # Current key display
            key_display = Label()
            key_display.set_property("text", self._get_current_key_text(action))
            key_display.set_position(400, y_offset)
            key_display.set_property("font_size", 16)
            key_display.set_property("text_color", (100, 200, 255, 255))
            bg_panel.add_child(key_display)

            # Remap button
            remap_btn = Button()
            remap_btn.set_property("text", "Remap")
            remap_btn.set_position(600, y_offset)
            remap_btn.set_property("size", (100, 30))
            bg_panel.add_child(remap_btn)

            y_offset += 50

        # Save button
        save_btn = Button()
        save_btn.set_property("text", "Save Changes")
        save_btn.set_position(300, 550)
        save_btn.set_property("size", (200, 40))
        bg_panel.add_child(save_btn)

        # Cancel button
        cancel_btn = Button()
        cancel_btn.set_property("text", "Cancel")
        cancel_btn.set_position(520, 550)
        cancel_btn.set_property("size", (100, 40))
        bg_panel.add_child(cancel_btn)

    def _get_current_key_text(self, action: InputAction) -> str:
        """Get current key text for an action."""
        mappings = self._input_controller.get_mappings()
        if action in mappings:
            keys = mappings[action]
            if keys:
                return self._key_to_text(keys[0])
        return "Not Set"

    def _key_to_text(self, key: int) -> str:
        """Convert key code to text."""
        key_names = {
            87: "W", 83: "S", 65: "A", 68: "D", 32: "Space",
            70: "F", 69: "E", 27: "Escape", 9: "Tab", 80: "P",
            16: "Shift", 17: "Ctrl", 18: "Alt", 13: "Enter",
            38: "Up", 40: "Down", 37: "Left", 39: "Right"
        }
        return key_names.get(key, f"Key_{key}")

    def get_input_controller(self) -> InputController:
        """Get the input controller for this scene."""
        return self._input_controller

    def set_input_controller(self, controller: InputController) -> None:
        """Set the input controller for this scene."""
        self._input_controller = controller

    def save_mappings(self) -> Dict:
        """Save current mappings to dictionary."""
        return {
            "version": 1,
            "mappings": {
                action.value: keys
                for action, keys in self._input_controller.get_mappings().items()
            }
        }

    def load_mappings(self, data: Dict) -> bool:
        """Load mappings from dictionary."""
        try:
            if "mappings" not in data:
                return False

            new_mappings = {}
            for action_str, keys in data["mappings"].items():
                try:
                    action = InputAction(action_str)
                    new_mappings[action] = keys
                except ValueError:
                    continue

            self._input_controller.set_mappings(new_mappings)
            return True
        except Exception:
            return False

    def reset_to_defaults(self) -> None:
        """Reset all mappings to defaults."""
        self._input_controller.reset_mappings()

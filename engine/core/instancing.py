# /**************************************************************************/
# /*  instancing.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from engine.core.node_base import Node
from engine.core.scene import Scene

def instance_scene(target_scene: Scene, source_scene: Scene, name_prefix: str = "Instance") -> Node:
    """Create a lightweight instanced scene root node.

    v0: stores metadata and links to source scene; deep copy is deferred to a future resource/packer layer.
    """

    instance_root = Node(f"{name_prefix}_{source_scene.name}")
    instance_root.set_property("instance_of_scene_id", source_scene.id)
    instance_root.set_property("instance_of_scene_name", source_scene.name)
    target_scene.add_node(instance_root)
    target_scene.instantiate_scene(source_scene.name)
    return instance_root

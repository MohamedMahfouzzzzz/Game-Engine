# /**************************************************************************/
# /*  scene.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import logging
from typing import Dict, List, Optional
import uuid

from engine.core.node_base import Node

logger = logging.getLogger(__name__)


class Scene:
    def __init__(self, name: str = "Scene"):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.root: Node = Node(f"{name}Root")
        self.nodes: Dict[str, Node] = {self.root.uid: self.root}
        self.instances: List[str] = []
        logger.info("Scene '%s' created with id %s", name, self.id)

    def _index_node_recursive(self, node: Node) -> None:
        self.nodes[node.uid] = node
        for child in node.children:
            self._index_node_recursive(child)

    def _collect_node_ids(self, node: Node) -> List[str]:
        collected = [node.uid]
        for child in node.children:
            collected.extend(self._collect_node_ids(child))
        return collected

    def add_node(self, node: Node, parent: Optional[Node] = None) -> None:
        if parent is None:
            parent = self.root
        parent.add_child(node)
        self._index_node_recursive(node)
        logger.debug("Node '%s' added to scene '%s' under '%s'", node.name, self.name, parent.name)

    def remove_node(self, node: Node) -> None:
        node_name = node.name
        if node.parent:
            node.parent.remove_child(node)
        for node_id in self._collect_node_ids(node):
            self.nodes.pop(node_id, None)
        logger.debug("Node '%s' removed from scene '%s'", node_name, self.name)

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def instantiate_scene(self, scene_name: str) -> None:
        self.instances.append(scene_name)
        logger.info("Scene '%s' instantiated in '%s'", scene_name, self.name)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "root": self.root.to_dict(),
            "instances": self.instances,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Scene":
        scene = Scene(data.get("name", "Scene"))
        scene.id = data.get("id", scene.id)
        root_data = data.get("root")
        if root_data:
            scene.root = Node.from_dict(root_data)
            scene.nodes = {}
            scene._index_node_recursive(scene.root)
        scene.instances = data.get("instances", [])
        node_count = len(scene.nodes)
        logger.info("Scene '%s' loaded from dict with %d nodes", scene.name, node_count)
        return scene

"""Test importing Godot scene with improved importer."""
import sys
sys.path.insert(0, '.')

from engine.interop.godot_importer import GodotImporter
from engine.core.nodes import Sprite, TileMap, Button, Label, Control

tscn_path = r'C:\Users\anasg\My Games\The-Blue-Bunny\Levels\easy\level_1_ar.tscn'

print('Testing improved Godot importer...')
importer = GodotImporter()
project = importer.import_project(tscn_path)

print(f'✅ Import successful!')
print(f'  Project: {project.name}')
print(f'  Scenes: {len(project.scenes)}')

if project.active_scene:
    scene = project.active_scene
    print(f'  Scene: {scene.name}')
    print(f'  Root children: {len(scene.root.children)}')
    
    # Count node types
    sprites = 0
    tilemaps = 0
    buttons = 0
    labels = 0
    controls = 0
    node2ds = 0
    nodes = 0
    
    def count_types(node):
        global sprites, tilemaps, buttons, labels, controls, node2ds, nodes
        if isinstance(node, Sprite):
            sprites += 1
        elif isinstance(node, TileMap):
            tilemaps += 1
        elif isinstance(node, Button):
            buttons += 1
        elif isinstance(node, Label):
            labels += 1
        elif isinstance(node, Control):
            controls += 1
        elif hasattr(node, 'position') and not isinstance(node, (Sprite, TileMap)):
            node2ds += 1
        else:
            nodes += 1
        for child in node.children:
            count_types(child)
    
    for child in scene.root.children:
        count_types(child)
    
    print(f'\n  TileMaps: {tilemaps}')
    print(f'  Buttons: {buttons}')
    print(f'  Labels: {labels}')
    print(f'  Controls: {controls}')
    print(f'  Node2Ds: {node2ds}')
    print(f'  Nodes: {nodes}')
    
    # Show report
    report = scene.root.get_property('interop_report', {})
    print(f'\n  Imported nodes: {report.get("imported_nodes", 0)}')
    if report.get('unsupported_node_types'):
        print(f'  Unsupported: {report["unsupported_node_types"]}')

print('\n🎉 Godot scene import test complete!')

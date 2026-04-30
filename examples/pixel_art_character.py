#!/usr/bin/env python
"""Example: Creating a pixel art character sprite."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.core import Document, Layer, BlendMode, ColorMode
from engine.io import BinaryFormat
from engine.tools.pixel_art_editor.algorithms import line_points, rectangle
from engine.tools.pixel_art_editor.brushes import BrushManager, BrushPresets


def create_character():
    """Create a simple pixel art character."""
    # Create document
    doc = Document(32, 32, 'Character')
    
    # Setup layers
    bg_layer = doc.sprite.add_layer('Background')
    bg_layer.is_background = True
    bg_layer.locked = True
    
    body_layer = doc.sprite.add_layer('Body')
    eyes_layer = doc.sprite.add_layer('Eyes')
    
    # Draw background (light blue)
    bg_cel = bg_layer.get_cel(0)
    for y in range(32):
        for x in range(32):
            bg_cel.image.set_pixel(x, y, (200, 220, 255, 255))
    
    # Draw body (red rectangle)
    body_cel = body_layer.get_cel(0)
    rectangle(8, 12, 24, 28, lambda x, y: body_cel.image.set_pixel(x, y, (255, 100, 100, 255)), filled=True)
    
    # Draw head (circle approximation)
    for y in range(8, 16):
        for x in range(8, 24):
            dx = x - 16
            dy = y - 12
            if dx*dx + dy*dy <= 16:  # Circle radius 4
                body_cel.image.set_pixel(x, y, (255, 150, 150, 255))
    
    # Draw eyes
    eyes_cel = eyes_layer.get_cel(0)
    eyes_cel.image.set_pixel(12, 11, (0, 0, 0, 255))  # Left eye
    eyes_cel.image.set_pixel(20, 11, (0, 0, 0, 255))  # Right eye
    
    # Draw smile
    for x in range(13, 21):
        y = 14 + int(((x-16)*(x-16)) / 9)
        eyes_cel.image.set_pixel(x, y, (0, 0, 0, 255))
    
    return doc


def create_animation_frames(doc):
    """Create animation frames for the character."""
    # Add frames for walk animation
    doc.sprite.add_frame(100)  # Frame 1
    doc.sprite.add_frame(100)  # Frame 2
    
    # Frame 1 - character shifted right
    body_layer = doc.sprite.get_layer('Body', 1)
    eyes_layer = doc.sprite.get_layer('Eyes', 1)
    
    # Clear and redraw shifted
    body_cel = body_layer.get_cel(1)
    body_cel.image.clear((0, 0, 0, 0))
    
    # Draw shifted body
    rectangle(10, 12, 26, 28, lambda x, y: body_cel.image.set_pixel(x, y, (255, 100, 100, 255)), filled=True)
    
    # Draw shifted head
    for y in range(8, 16):
        for x in range(10, 26):
            dx = x - 18
            dy = y - 12
            if dx*dx + dy*dy <= 16:
                body_cel.image.set_pixel(x, y, (255, 150, 150, 255))
    
    # Frame 2 - character shifted left
    body_layer = doc.sprite.get_layer('Body', 2)
    eyes_layer = doc.sprite.get_layer('Eyes', 2)
    
    body_cel = body_layer.get_cel(2)
    body_cel.image.clear((0, 0, 0, 0))
    
    # Draw shifted body
    rectangle(6, 12, 22, 28, lambda x, y: body_cel.image.set_pixel(x, y, (255, 100, 100, 255)), filled=True)
    
    # Draw shifted head
    for y in range(8, 16):
        for x in range(6, 22):
            dx = x - 14
            dy = y - 12
            if dx*dx + dy*dy <= 16:
                body_cel.image.set_pixel(x, y, (255, 150, 150, 255))
    
    # Add animation tag
    from engine.tools.pixel_art_editor.core import Tag, TagRepeat
    walk_tag = Tag('Walk', 0, 2, (255, 0, 0), TagRepeat.LOOP)
    doc.sprite.add_tag(walk_tag)


def main():
    """Main function."""
    print("Creating pixel art character...")
    
    # Create character
    doc = create_character()
    
    # Add animation
    create_animation_frames(doc)
    
    # Save document
    output_file = 'character.ges'
    success = BinaryFormat.save(doc, output_file)
    
    if success:
        print(f"Character saved to {output_file}")
        print(f"  Size: {doc.width}x{doc.height}")
        print(f"  Layers: {doc.sprite.layer_count}")
        print(f"  Frames: {doc.sprite.frame_count}")
        print(f"  Tags: {len(doc.sprite.tags)}")
    else:
        print("Failed to save character")
    
    # Export as PNG for preview
    from PIL import Image
    
    # Get first frame as image
    layer = doc.sprite.get_layer('Body', 0)
    cel = layer.get_cel(0)
    img = cel.image._image.convert('RGBA')
    img.save('character_preview.png')
    print("Preview saved as character_preview.png")


if __name__ == '__main__':
    main()

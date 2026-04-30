#!/usr/bin/env python
"""Example: Creating animated pixel art."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.core import Document, Layer, Tag, TagRepeat
from engine.io import BinaryFormat
from engine.tools.pixel_art_editor.algorithms import line_points, rectangle, ellipse


def create_bouncing_ball():
    """Create a bouncing ball animation."""
    doc = Document(64, 64, 'BouncingBall')
    
    # Add background layer
    bg_layer = doc.sprite.add_layer('Background')
    bg_layer.is_background = True
    
    # Add ball layer
    ball_layer = doc.sprite.add_layer('Ball')
    
    # Create 8 frames for animation
    for frame in range(8):
        if frame > 0:
            doc.sprite.add_frame(50)  # 50ms per frame
        
        # Draw background (gradient)
        bg_cel = bg_layer.get_cel(frame)
        for y in range(64):
            for x in range(64):
                color_value = 100 + int(y * 2)
                bg_cel.image.set_pixel(x, y, (color_value, color_value, 255, 255))
        
        # Calculate ball position (bouncing motion)
        t = frame / 8.0
        # Bounce height using sine wave
        bounce_height = int(abs(t - 0.5) * 40)
        ball_y = 50 - bounce_height
        ball_x = 32 + int((t - 0.5) * 20)  # Slight horizontal movement
        
        # Draw ball
        ball_cel = ball_layer.get_cel(frame)
        for y in range(64):
            for x in range(64):
                dx = x - ball_x
                dy = y - ball_y
                if dx*dx + dy*dy <= 25:  # Ball radius 5
                    # Add shading
                    intensity = 255 - int((dx*dx + dy*dy) * 2)
                    intensity = max(100, min(255, intensity))
                    ball_cel.image.set_pixel(x, y, (intensity, intensity//2, 0, 255))
    
    # Add animation tag
    bounce_tag = Tag('Bounce', 0, 7, (255, 255, 0), TagRepeat.LOOP)
    doc.sprite.add_tag(bounce_tag)
    
    return doc


def create_rotating_star():
    """Create a rotating star animation."""
    doc = Document(64, 64, 'RotatingStar')
    
    # Add layers
    bg_layer = doc.sprite.add_layer('Background')
    star_layer = doc.sprite.add_layer('Star')
    
    # Create 12 frames for rotation
    for frame in range(12):
        if frame > 0:
            doc.sprite.add_frame(83)  # ~12 FPS
        
        # Draw background (space)
        bg_cel = bg_layer.get_cel(frame)
        for y in range(64):
            for x in range(64):
                bg_cel.image.set_pixel(x, y, (0, 0, 20, 255))
        
        # Add some stars
        import random
        random.seed(42)  # Fixed seed for consistent stars
        for _ in range(20):
            sx = random.randint(0, 63)
            sy = random.randint(0, 63)
            bg_cel.image.set_pixel(sx, sy, (255, 255, 255, 255))
        
        # Draw rotating star
        star_cel = star_layer.get_cel(frame)
        angle = frame * 30  # 30 degrees per frame
        
        # Star points
        points = []
        for i in range(10):
            a = angle + i * 36  # 36 degrees between points
            if i % 2 == 0:
                r = 20  # Outer points
            else:
                r = 8   # Inner points
            
            import math
            rad = math.radians(a)
            x = 32 + int(r * math.cos(rad))
            y = 32 + int(r * math.sin(rad))
            points.append((x, y))
        
        # Draw star outline
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            
            # Draw line between points
            line_pts = line_points(p1[0], p1[1], p2[0], p2[1])
            for x, y in line_pts:
                if 0 <= x < 64 and 0 <= y < 64:
                    star_cel.image.set_pixel(x, y, (255, 255, 0, 255))
        
        # Fill star (simple flood fill)
        star_cel.image.set_pixel(32, 32, (255, 200, 0, 255))
    
    # Add animation tag
    rotate_tag = Tag('Rotate', 0, 11, (255, 255, 0), TagRepeat.LOOP)
    doc.sprite.add_tag(rotate_tag)
    
    return doc


def create_text_animation():
    """Create text animation."""
    doc = Document(128, 32, 'TextAnimation')
    
    # Add layers
    bg_layer = doc.sprite.add_layer('Background')
    text_layer = doc.sprite.add_layer('Text')
    
    # Text to animate
    text = "HELLO WORLD"
    
    # Create frames for scrolling text
    total_frames = len(text) * 4 + 20  # Extra frames at start/end
    
    for frame in range(total_frames):
        if frame > 0:
            doc.sprite.add_frame(100)
        
        # Draw background
        bg_cel = bg_layer.get_cel(frame)
        for y in range(32):
            for x in range(128):
                bg_cel.image.set_pixel(x, y, (50, 50, 50, 255))
        
        # Calculate text position
        text_x = 128 - frame * 2  # Scroll from right to left
        
        # Draw text (simple 5x5 font)
        text_cel = text_layer.get_cel(frame)
        
        # Simple font representation
        font = {
            'H': [(0,0), (0,4), (2,0), (2,4), (0,2), (2,2)],
            'E': [(0,0), (0,4), (2,0), (2,4), (0,0), (2,0), (0,2), (2,2)],
            'L': [(0,0), (0,4), (0,0), (2,0)],
            'O': [(0,0), (0,4), (2,0), (2,4), (0,0), (2,0), (0,4), (2,4)],
            'W': [(0,0), (0,4), (1,2), (2,0), (2,4)],
            'R': [(0,0), (0,4), (2,0), (2,2), (0,2), (2,2), (2,2), (2,4)],
            'D': [(0,0), (0,4), (2,0), (2,4), (0,0), (2,0), (0,4), (2,4)],
            ' ': []
        }
        
        char_x = text_x
        for char in text:
            if char in font:
                for px, py in font[char]:
                    x = char_x + px
                    y = 13 + py  # Center vertically
                    if 0 <= x < 128 and 0 <= y < 32:
                        text_cel.image.set_pixel(x, y, (255, 255, 255, 255))
            char_x += 4  # Character spacing
    
    # Add animation tag
    scroll_tag = Tag('Scroll', 0, total_frames-1, (255, 255, 255), TagRepeat.ONCE)
    doc.sprite.add_tag(scroll_tag)
    
    return doc


def export_gif(doc, filename):
    """Export animation as GIF."""
    try:
        from PIL import Image
        
        frames = []
        for frame_idx in range(doc.sprite.frame_count):
            # Composite all layers for this frame
            composite = Image.new('RGBA', (doc.width, doc.height), (0, 0, 0, 0))
            
            for layer in doc.sprite.layers:
                cel = layer.get_cel(frame_idx)
                if cel and not layer.is_visible:
                    continue
                
                if cel:
                    layer_img = cel.image._image.convert('RGBA')
                    composite = Image.alpha_composite(composite, layer_img)
            
            frames.append(composite)
        
        # Save as GIF
        if frames:
            durations = [frame.duration_ms for frame in doc.sprite.frames]
            frames[0].save(
                filename,
                save_all=True,
                append_images=frames[1:],
                duration=durations[0] if durations else 100,
                loop=0
            )
            print(f"Animation exported as {filename}")
            return True
    except ImportError:
        print("PIL not available for GIF export")
    except Exception as e:
        print(f"Error exporting GIF: {e}")
    
    return False


def main():
    """Main function."""
    print("Creating animation examples...")
    
    # Create bouncing ball
    print("\n1. Creating bouncing ball...")
    ball_doc = create_bouncing_ball()
    BinaryFormat.save(ball_doc, 'bouncing_ball.ges')
    export_gif(ball_doc, 'bouncing_ball.gif')
    
    # Create rotating star
    print("\n2. Creating rotating star...")
    star_doc = create_rotating_star()
    BinaryFormat.save(star_doc, 'rotating_star.ges')
    export_gif(star_doc, 'rotating_star.gif')
    
    # Create text animation
    print("\n3. Creating text animation...")
    text_doc = create_text_animation()
    BinaryFormat.save(text_doc, 'text_animation.ges')
    export_gif(text_doc, 'text_animation.gif')
    
    print("\nAll animations created!")
    print("\nFiles created:")
    print("  - bouncing_ball.ges")
    print("  - bouncing_ball.gif")
    print("  - rotating_star.ges")
    print("  - rotating_star.gif")
    print("  - text_animation.ges")
    print("  - text_animation.gif")


if __name__ == '__main__':
    main()

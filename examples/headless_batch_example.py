#!/usr/bin/env python
"""Example: Using headless mode for batch processing."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.headless import HeadlessEngine, BatchProcessor
from engine.tools.pixel_art_editor.core import Document
from engine.io import BinaryFormat


def create_sample_documents():
    """Create sample documents for batch processing."""
    print("Creating sample documents...")
    
    # Create a directory for samples
    os.makedirs('batch_input', exist_ok=True)
    
    # Create different types of documents
    documents = []
    
    # 1. Character sprite
    char_doc = Document(32, 32, 'Character')
    layer = char_doc.sprite.add_layer('Body')
    cel = layer.get_cel(0)
    
    # Draw simple character
    for y in range(32):
        for x in range(32):
            if 8 <= x <= 24 and 12 <= y <= 28:
                cel.image.set_pixel(x, y, (255, 100, 100, 255))
            elif 12 <= x <= 20 and 8 <= y <= 16:
                cel.image.set_pixel(x, y, (255, 150, 150, 255))
    
    documents.append(('character.ges', char_doc))
    
    # 2. Tile
    tile_doc = Document(16, 16, 'Tile')
    layer = tile_doc.sprite.add_layer('Tile')
    cel = layer.get_cel(0)
    
    # Draw grass tile
    for y in range(16):
        for x in range(16):
            cel.image.set_pixel(x, y, (50, 150, 50, 255))
    
    # Add some detail
    for _ in range(20):
        x = random.randint(0, 15)
        y = random.randint(0, 15)
        cel.image.set_pixel(x, y, (70, 170, 70, 255))
    
    documents.append(('tile.ges', tile_doc))
    
    # 3. Animation
    anim_doc = Document(64, 64, 'Animation')
    layer = anim_doc.sprite.add_layer('Anim')
    
    # Create 4 frames
    for frame in range(4):
        if frame > 0:
            anim_doc.add_frame(100)
        
        cel = layer.get_cel(frame)
        
        # Draw bouncing ball
        import math
        t = frame / 4.0
        ball_y = 32 + int(math.sin(t * math.pi * 2) * 10)
        
        for y in range(64):
            for x in range(64):
                dx = x - 32
                dy = y - ball_y
                if dx*dx + dy*dy <= 25:
                    cel.image.set_pixel(x, y, (255, 255, 0, 255))
    
    documents.append(('animation.ges', anim_doc))
    
    # Save all documents
    for filename, doc in documents:
        filepath = os.path.join('batch_input', filename)
        BinaryFormat.save(doc, filepath)
        print(f"  Created {filepath}")
    
    return [os.path.join('batch_input', doc[0]) for doc in documents]


def basic_headless_operations():
    """Demonstrate basic headless engine operations."""
    print("\n=== BASIC HEADLESS OPERATIONS ===\n")
    
    # Initialize engine
    engine = HeadlessEngine()
    engine.initialize()
    
    # Set progress callback
    def progress_callback(progress, message):
        print(f"[{progress*100:.0f}%] {message}")
    
    engine.set_progress_callback(progress_callback)
    
    # Load a document
    print("Loading document...")
    doc = engine.load_project('batch_input/character.ges')
    if doc:
        print(f"Loaded: {doc.name} ({doc.width}x{doc.height})")
        print(f"  Layers: {doc.sprite.layer_count}")
        print(f"  Frames: {doc.sprite.frame_count}")
    
    # Export to different formats
    print("\nExporting to different formats...")
    
    formats = [
        ('character.png', 'PNG'),
        ('character.jpg', 'JPEG'),
        ('character.bmp', 'BMP')
    ]
    
    for filename, format_name in formats:
        success = engine.export(filename, format=format_name)
        if success:
            print(f"  Exported {filename}")
    
    # Export spritesheet
    print("\nExporting spritesheet...")
    success = engine.export_sheet('character_sheet.png', columns=4, rows=1)
    if success:
        print("  Exported character_sheet.png")
    
    # Validate document
    print("\nValidating document...")
    result = engine.validate('batch_input/character.ges')
    if result.success:
        print(f"  Valid: {result.data}")
    else:
        print(f"  Invalid: {result.error}")
    
    engine.shutdown()
    
    # Cleanup
    for filename, _ in formats:
        if os.path.exists(filename):
            os.remove(filename)
    if os.path.exists('character_sheet.png'):
        os.remove('character_sheet.png')


def batch_processing_demo():
    """Demonstrate batch processing."""
    print("\n=== BATCH PROCESSING DEMO ===\n")
    
    # Create sample documents
    input_files = create_sample_documents()
    
    # Initialize engine and processor
    engine = HeadlessEngine()
    engine.initialize()
    
    processor = BatchProcessor(engine)
    
    # Set up progress tracking
    def progress_callback(progress, message):
        print(f"[{progress*100:.0f}%] {message}")
    
    processor.set_progress_callback(progress_callback)
    
    # Process directory
    print("Processing directory...")
    results = processor.process_directory(
        input_dir='batch_input',
        output_dir='batch_output',
        input_pattern='*.ges',
        output_format='PNG',
        recursive=False
    )
    
    # Print results
    print(f"\nProcessed {len(results)} files:")
    success_count = 0
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"  {status} {result.input_file} -> {result.output_file}")
        if result.success:
            success_count += 1
        elif result.error:
            print(f"    Error: {result.error}")
    
    print(f"\nSuccess: {success_count}/{len(results)} files")
    
    # Get statistics
    stats = processor.get_stats(results)
    print(f"\nStatistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Success: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Time: {stats['elapsed_time']:.2f}s")
    
    engine.shutdown()
    
    # Cleanup
    import shutil
    if os.path.exists('batch_output'):
        shutil.rmtree('batch_output')
    if os.path.exists('batch_input'):
        shutil.rmtree('batch_input')


def custom_batch_processing():
    """Demonstrate custom batch processing logic."""
    print("\n=== CUSTOM BATCH PROCESSING ===\n")
    
    # Create sample documents
    input_files = create_sample_documents()
    
    # Initialize engine
    engine = HeadlessEngine()
    engine.initialize()
    
    # Custom processing function
    def process_with_metadata(input_file, output_file):
        """Process document and add metadata."""
        # Load document
        doc = engine.load_project(input_file)
        if not doc:
            return False, "Failed to load document"
        
        # Add metadata
        import time
        doc.author = "Batch Processor"
        doc.description = f"Processed on {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Export with metadata
        success = engine.export(output_file, format='PNG')
        
        # Also save processed GES
        ges_output = output_file.replace('.png', '_processed.ges')
        BinaryFormat.save(doc, ges_output)
        
        return success, None
    
    # Process files
    print("Custom processing with metadata...")
    
    output_dir = 'custom_output'
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    for input_file in input_files:
        basename = os.path.basename(input_file).replace('.ges', '.png')
        output_file = os.path.join(output_dir, basename)
        
        success, error = process_with_metadata(input_file, output_file)
        
        result = type('Result', (), {
            'input_file': input_file,
            'output_file': output_file,
            'success': success,
            'error': error
        })()
        
        results.append(result)
        
        status = "✓" if success else "✗"
        print(f"  {status} {os.path.basename(input_file)}")
    
    # Verify processed files
    print("\nVerifying processed files...")
    for result in results:
        if result.success and os.path.exists(result.output_file):
            # Load and verify
            from PIL import Image
            try:
                img = Image.open(result.output_file)
                print(f"  ✓ {os.path.basename(result.output_file)} ({img.size[0]}x{img.size[1]})")
            except Exception as e:
                print(f"  ✗ {os.path.basename(result.output_file)}: {e}")
    
    engine.shutdown()
    
    # Cleanup
    import shutil
    if os.path.exists('custom_output'):
        shutil.rmtree('custom_output')
    if os.path.exists('batch_input'):
        shutil.rmtree('batch_input')


def validation_and_quality_check():
    """Demonstrate document validation and quality checks."""
    print("\n=== VALIDATION & QUALITY CHECK ===\n")
    
    # Create test documents with various issues
    os.makedirs('validation_test', exist_ok=True)
    
    # 1. Valid document
    valid_doc = Document(32, 32, 'Valid')
    layer = valid_doc.sprite.add_layer('Layer')
    cel = layer.get_cel(0)
    cel.image.clear((255, 255, 255, 255))
    BinaryFormat.save(valid_doc, 'validation_test/valid.ges')
    
    # 2. Empty document
    empty_doc = Document(16, 16, 'Empty')
    BinaryFormat.save(empty_doc, 'validation_test/empty.ges')
    
    # 3. Large document
    large_doc = Document(1024, 1024, 'Large')
    layer = large_doc.sprite.add_layer('Layer')
    cel = layer.get_cel(0)
    for y in range(0, 1024, 8):
        for x in range(0, 1024, 8):
            cel.image.set_pixel(x, y, (255, 0, 0, 255))
    BinaryFormat.save(large_doc, 'validation_test/large.ges')
    
    # Initialize engine
    engine = HeadlessEngine()
    engine.initialize()
    
    # Validate all documents
    test_files = [
        'validation_test/valid.ges',
        'validation_test/empty.ges',
        'validation_test/large.ges',
        'validation_test/nonexistent.ges'  # This should fail
    ]
    
    print("Validating documents...")
    
    for filepath in test_files:
        print(f"\nValidating {filepath}...")
        result = engine.validate(filepath)
        
        if result.success:
            data = result.data
            print(f"  ✓ Valid document")
            print(f"    Size: {data['width']}x{data['height']}")
            print(f"    Layers: {data['layers']}")
            print(f"    Frames: {data['frames']}")
            print(f"    File size: {data['file_size']} bytes")
            
            # Quality checks
            if data['layers'] == 0:
                print("    ⚠ Warning: No layers")
            if data['width'] * data['height'] > 512 * 512:
                print("    ⚠ Warning: Large image size")
        else:
            print(f"  ✗ Invalid: {result.error}")
    
    engine.shutdown()
    
    # Cleanup
    import shutil
    if os.path.exists('validation_test'):
        shutil.rmtree('validation_test')


def main():
    """Main demonstration."""
    print("HEADLESS MODE DEMONSTRATION")
    print("="*60)
    
    try:
        import random
    except ImportError:
        print("Warning: random module not available")
        random = None
    
    # Run all demos
    basic_headless_operations()
    batch_processing_demo()
    custom_batch_processing()
    validation_and_quality_check()
    
    print("\n" + "="*60)
    print("Headless mode demonstration complete!")
    print("\nKey features demonstrated:")
    print("  ✓ Document loading and saving")
    print("  ✓ Format conversion (PNG, JPEG, BMP)")
    print("  ✓ Spritesheet generation")
    print("  ✓ Document validation")
    print("  ✓ Batch processing")
    print("  ✓ Custom processing pipelines")
    print("  ✓ Progress tracking")
    print("  ✓ Error handling")
    print("  ✓ Quality checks")


if __name__ == '__main__':
    main()

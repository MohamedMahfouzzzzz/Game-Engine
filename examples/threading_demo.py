#!/usr/bin/env python
"""Example: Using the threading system for parallel processing."""

import os
import sys
import time
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.threading import ThreadPool, TaskPriority
from engine.tools.pixel_art_editor.core import Document, ImageBuffer, ColorMode
from engine.io import BinaryFormat


def image_processing_demo():
    """Demonstrate parallel image processing."""
    print("\n=== IMAGE PROCESSING DEMO ===\n")
    
    # Create test images
    images = []
    for i in range(8):
        img = ImageBuffer(128, 128, ColorMode.RGBA)
        # Add some random data
        for y in range(0, 128, 4):
            for x in range(0, 128, 4):
                color = (random.randint(0, 255), 
                        random.randint(0, 255), 
                        random.randint(0, 255), 
                        255)
                img.set_pixel(x, y, color)
        images.append(img)
    
    print(f"Created {len(images)} test images (128x128)")
    
    # Processing function
    def apply_filter(image_data, filter_type):
        """Apply a filter to image data."""
        time.sleep(0.1)  # Simulate processing time
        
        if filter_type == 'grayscale':
            # Convert to grayscale
            for y in range(image_data.height):
                for x in range(image_data.width):
                    r, g, b, a = image_data.get_pixel(x, y)
                    gray = int((r + g + b) / 3)
                    image_data.set_pixel(x, y, (gray, gray, gray, a))
        
        elif filter_type == 'invert':
            # Invert colors
            for y in range(image_data.height):
                for x in range(image_data.width):
                    r, g, b, a = image_data.get_pixel(x, y)
                    image_data.set_pixel(x, y, (255-r, 255-g, 255-b, a))
        
        elif filter_type == 'sepia':
            # Apply sepia tone
            for y in range(image_data.height):
                for x in range(image_data.width):
                    r, g, b, a = image_data.get_pixel(x, y)
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    image_data.set_pixel(x, y, 
                                       (min(255, tr), min(255, tg), min(255, tb), a))
        
        return f"Applied {filter_type} filter"
    
    # Sequential processing
    print("\nSequential processing...")
    start = time.time()
    
    sequential_results = []
    for i, img in enumerate(images):
        filter_type = ['grayscale', 'invert', 'sepia'][i % 3]
        result = apply_filter(img, filter_type)
        sequential_results.append(result)
    
    sequential_time = time.time() - start
    print(f"Sequential: {sequential_time:.2f}s")
    
    # Parallel processing
    print("\nParallel processing...")
    pool = ThreadPool(max_workers=4)
    start = time.time()
    
    futures = []
    for i, img in enumerate(images):
        filter_type = ['grayscale', 'invert', 'sepia'][i % 3]
        future = pool.submit(apply_filter, img, filter_type)
        futures.append(future)
    
    parallel_results = []
    for future in futures:
        result = future.result()
        parallel_results.append(result)
    
    parallel_time = time.time() - start
    print(f"Parallel: {parallel_time:.2f}s")
    
    pool.shutdown()
    
    # Calculate speedup
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x")
    
    return sequential_results, parallel_results


def document_batch_processing():
    """Demonstrate batch processing of documents."""
    print("\n=== DOCUMENT BATCH PROCESSING ===\n")
    
    # Create test documents
    documents = []
    for i in range(6):
        doc = Document(64, 64, f'Doc{i}')
        layer = doc.sprite.add_layer(f'Layer{i}')
        
        # Add some data
        cel = layer.get_cel(0)
        for y in range(64):
            for x in range(64):
                color = (i * 40, x, y, 255)
                cel.image.set_pixel(x, y, color)
        
        documents.append(doc)
    
    print(f"Created {len(documents)} test documents")
    
    # Processing functions
    def save_document(doc, filename):
        """Save document to file."""
        time.sleep(0.05)  # Simulate I/O time
        success = BinaryFormat.save(doc, filename)
        return success
    
    def add_metadata(doc, author, description):
        """Add metadata to document."""
        time.sleep(0.02)  # Simulate processing
        doc.author = author
        doc.description = description
        return f"Added metadata to {doc.name}"
    
    def create_thumbnail(doc, size):
        """Create thumbnail of document."""
        time.sleep(0.03)  # Simulate processing
        # Resize logic would go here
        return f"Created {size}x{size} thumbnail for {doc.name}"
    
    # Batch process with ThreadPool
    pool = ThreadPool(max_workers=3)
    
    print("\nStarting batch processing...")
    
    # Submit all tasks
    futures = []
    
    # Save documents
    for i, doc in enumerate(documents):
        future = pool.submit(save_document, doc, f'batch_doc_{i}.ges')
        futures.append(('save', future))
    
    # Add metadata
    for doc in documents:
        future = pool.submit(add_metadata, doc, 'Batch Processor', 'Processed in batch')
        futures.append(('metadata', future))
    
    # Create thumbnails
    for doc in documents:
        future = pool.submit(create_thumbnail, doc, 32)
        futures.append(('thumbnail', future))
    
    # Collect results
    results = {'save': [], 'metadata': [], 'thumbnail': []}
    
    for task_type, future in futures:
        try:
            result = future.result(timeout=5)
            results[task_type].append(result)
        except Exception as e:
            print(f"Error in {task_type}: {e}")
    
    pool.shutdown()
    
    # Print summary
    print(f"\nBatch processing complete:")
    print(f"  Saved: {len(results['save'])} documents")
    print(f"  Metadata: {len(results['metadata'])} documents")
    print(f"  Thumbnails: {len(results['thumbnail'])} thumbnails")
    
    # Cleanup
    for i in range(len(documents)):
        filename = f'batch_doc_{i}.ges'
        if os.path.exists(filename):
            os.remove(filename)
    
    return results


def priority_tasks_demo():
    """Demonstrate task priority system."""
    print("\n=== TASK PRIORITY DEMO ===\n")
    
    pool = ThreadPool(max_workers=2)
    
    def task(name, duration):
        """Simple task that prints when it starts and ends."""
        print(f"[START] {name}")
        time.sleep(duration)
        print(f"[END]   {name}")
        return f"Completed {name}"
    
    import time
    start_time = time.time()
    
    # Submit tasks with different priorities
    futures = []
    
    # Low priority tasks
    for i in range(3):
        future = pool.submit(task, f"Low-{i}", 0.5, priority=TaskPriority.LOW)
        futures.append(future)
    
    # High priority task
    future = pool.submit(task, "HIGH", 0.5, priority=TaskPriority.HIGH)
    futures.append(future)
    
    # Normal priority tasks
    for i in range(2):
        future = pool.submit(task, f"Normal-{i}", 0.5, priority=TaskPriority.NORMAL)
        futures.append(future)
    
    # Critical priority task
    future = pool.submit(task, "CRITICAL", 0.5, priority=TaskPriority.CRITICAL)
    futures.append(future)
    
    # Wait for all to complete
    for future in futures:
        future.result()
    
    total_time = time.time() - start_time
    print(f"\nTotal time: {total_time:.2f}s")
    print("Note: CRITICAL and HIGH tasks should run first")
    
    pool.shutdown()


def async_file_operations():
    """Demonstrate async file operations."""
    print("\n=== ASYNC FILE OPERATIONS ===\n")
    
    # Create test data
    test_docs = []
    for i in range(4):
        doc = Document(32, 32, f'AsyncDoc{i}')
        layer = doc.sprite.add_layer('TestLayer')
        cel = layer.get_cel(0)
        
        # Simple pattern
        for y in range(32):
            for x in range(32):
                if (x + y) % 2 == 0:
                    cel.image.set_pixel(x, y, (255, 255, 255, 255))
        
        test_docs.append(doc)
    
    pool = ThreadPool(max_workers=3)
    
    def save_with_retry(doc, filename, max_retries=3):
        """Save document with retry logic."""
        for attempt in range(max_retries):
            try:
                # Simulate occasional failure
                if random.random() < 0.3:  # 30% chance of failure
                    raise Exception("Simulated I/O error")
                
                success = BinaryFormat.save(doc, filename)
                if success:
                    return f"Saved {filename} on attempt {attempt + 1}"
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Failed to save {filename} after {max_retries} attempts: {e}"
                time.sleep(0.1)  # Wait before retry
        
        return f"Failed to save {filename}"
    
    def load_and_verify(filename):
        """Load and verify document."""
        time.sleep(0.1)  # Simulate load time
        
        doc = BinaryFormat.load(filename)
        if doc:
            return f"Verified {filename}: {doc.width}x{doc.height}"
        else:
            return f"Failed to load {filename}"
    
    # Submit save operations
    print("Submitting save operations...")
    save_futures = []
    for i, doc in enumerate(test_docs):
        filename = f'async_doc_{i}.ges'
        future = pool.submit(save_with_retry, doc, filename)
        save_futures.append((filename, future))
    
    # Wait for saves to complete
    save_results = []
    for filename, future in save_futures:
        result = future.result()
        save_results.append((filename, result))
        print(f"  {result}")
    
    # Submit load and verify operations
    print("\nSubmitting verification operations...")
    verify_futures = []
    for filename, _ in save_futures:
        if os.path.exists(filename):
            future = pool.submit(load_and_verify, filename)
            verify_futures.append(future)
    
    # Wait for verification
    for future in verify_futures:
        result = future.result()
        print(f"  {result}")
    
    pool.shutdown()
    
    # Cleanup
    for i in range(len(test_docs)):
        filename = f'async_doc_{i}.ges'
        if os.path.exists(filename):
            os.remove(filename)
    
    return save_results


def main():
    """Main demonstration."""
    print("THREADING SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Run all demos
    image_processing_demo()
    document_batch_processing()
    priority_tasks_demo()
    async_file_operations()
    
    print("\n" + "="*60)
    print("Threading system demonstration complete!")
    print("\nKey features demonstrated:")
    print("  ✓ Parallel image processing")
    print("  ✓ Batch document operations")
    print("  ✓ Task priority system")
    print("  ✓ Async file operations with retry")
    print("  ✓ Error handling in threads")


if __name__ == '__main__':
    main()

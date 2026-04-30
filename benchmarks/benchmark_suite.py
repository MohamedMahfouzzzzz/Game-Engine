# /**************************************************************************/
# /*  benchmark_suite.py                                                    */
# /**************************************************************************/

"""Performance benchmark suite for Game Engine Studio."""

import time
import statistics
import sys
import os
from typing import Dict, List, Callable, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.core import Document, ImageBuffer, ColorMode
from engine.io import BinaryFormat
from engine.signals import Signal, SignalManager
from engine.threading import ThreadPool
from engine.tools.pixel_art_editor.algorithms import line_points, flood_fill_simple
from engine.tools.pixel_art_editor.brushes import BrushManager, BrushPresets


class Benchmark:
    """Single benchmark test."""
    
    def __init__(self, name: str, func: Callable, iterations: int = 10):
        self.name = name
        self.func = func
        self.iterations = iterations
    
    def run(self) -> Dict[str, Any]:
        """Run benchmark and return results."""
        times = []
        
        # Warm up
        self.func()
        
        # Run iterations
        for _ in range(self.iterations):
            start = time.perf_counter()
            self.func()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        return {
            'name': self.name,
            'times': times,
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0
        }


class BenchmarkSuite:
    """Collection of benchmarks."""
    
    def __init__(self):
        self.benchmarks = []
        self.results = []
    
    def add(self, name: str, func: Callable, iterations: int = 10):
        """Add benchmark to suite."""
        self.benchmarks.append(Benchmark(name, func, iterations))
    
    def run(self) -> List[Dict[str, Any]]:
        """Run all benchmarks."""
        print("="*60)
        print("PERFORMANCE BENCHMARK SUITE")
        print("="*60)
        print()
        
        for benchmark in self.benchmarks:
            print(f"Running {benchmark.name}...", end=' ')
            result = benchmark.run()
            self.results.append(result)
            print(f"Done ({result['mean']:.4f}s avg)")
        
        self.print_summary()
        return self.results
    
    def print_summary(self):
        """Print benchmark summary."""
        print()
        print("="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        print()
        
        for result in self.results:
            print(f"{result['name']}")
            print(f"  Mean:   {result['mean']:.4f}s")
            print(f"  Median: {result['median']:.4f}s")
            print(f"  Min:    {result['min']:.4f}s")
            print(f"  Max:    {result['max']:.4f}s")
            print(f"  StdDev: {result['stdev']:.4f}s")
            print()


def benchmark_image_operations():
    """Benchmark image operations."""
    suite = BenchmarkSuite()
    
    # Pixel setting
    def set_pixels():
        img = ImageBuffer(256, 256, ColorMode.RGBA)
        for y in range(256):
            for x in range(256):
                img.set_pixel(x, y, (x % 256, y % 256, 128, 255))
    
    suite.add("Set 256x256 pixels (sequential)", set_pixels, iterations=5)
    
    # Clear operation
    def clear_image():
        img = ImageBuffer(512, 512, ColorMode.RGBA)
        img.clear((255, 128, 64, 255))
    
    suite.add("Clear 512x512 image", clear_image)
    
    # is_empty check
    img = ImageBuffer(512, 512, ColorMode.RGBA)
    
    def check_empty():
        img.is_empty()
    
    suite.add("is_empty() 512x512", check_empty)
    
    # Copy operation
    def copy_image():
        img = ImageBuffer(256, 256, ColorMode.RGBA)
        for y in range(256):
            for x in range(256):
                img.set_pixel(x, y, (x, y, 128, 255))
        copy = img.copy()
    
    suite.add("Copy 256x256 image", copy_image, iterations=5)
    
    return suite.run()


def benchmark_algorithms():
    """Benchmark drawing algorithms."""
    suite = BenchmarkSuite()
    
    # Line drawing
    def draw_long_line():
        points = line_points(0, 0, 1000, 1000)
    
    suite.add("Line drawing (1000 pixels)", draw_long_line)
    
    # Multiple lines
    def draw_multiple_lines():
        for i in range(100):
            line_points(i, 0, i, 100)
    
    suite.add("100 lines (100 pixels each)", draw_multiple_lines)
    
    # Flood fill
    img = ImageBuffer(100, 100, ColorMode.RGBA)
    
    def flood_fill():
        # Fill with pattern
        for y in range(100):
            for x in range(100):
                img.set_pixel(x, y, (255, 255, 255, 255))
        
        # Create hole
        for y in range(30, 70):
            for x in range(30, 70):
                img.set_pixel(x, y, (0, 0, 0, 255))
        
        # Fill hole
        filled = flood_fill_simple(
            50, 50,
            lambda x, y: img.get_pixel(x, y),
            lambda x, y, c: img.set_pixel(x, y, c),
            (0, 0, 0, 255),
            (255, 0, 0, 255),
            (0, 0, 100, 100)
        )
    
    suite.add("Flood fill 40x40 area", flood_fill, iterations=5)
    
    return suite.run()


def benchmark_binary_format():
    """Benchmark binary format operations."""
    suite = BenchmarkSuite()
    
    # Create test document
    doc = Document(256, 256, 'BenchmarkDoc')
    layer = doc.sprite.add_layer('Layer1')
    
    # Add some data
    cel = layer.get_cel(0)
    for y in range(256):
        for x in range(256):
            cel.image.set_pixel(x, y, (x % 256, y % 256, 128, 255))
    
    # Add multiple layers
    for i in range(5):
        layer = doc.sprite.add_layer(f'Layer{i+2}')
        cel = layer.get_cel(0)
        cel.image.clear((128, 128, 128, 255))
    
    # Save benchmark
    def save_document():
        BinaryFormat.save(doc, 'benchmark_save.ges')
    
    suite.add("Save 256x256 document (6 layers)", save_document, iterations=5)
    
    # Load benchmark
    def load_document():
        BinaryFormat.load('benchmark_save.ges')
    
    suite.add("Load 256x256 document (6 layers)", load_document, iterations=5)
    
    # Cleanup
    if os.path.exists('benchmark_save.ges'):
        os.remove('benchmark_save.ges')
    
    return suite.run()


def benchmark_signals():
    """Benchmark signal system."""
    suite = BenchmarkSuite()
    
    # Signal creation
    def create_signals():
        sig = Signal(int, str, float)
    
    suite.add("Signal creation", create_signals, iterations=1000)
    
    # Connection
    sig = Signal()
    
    def connect_handler():
        def handler():
            pass
        sig.connect(handler)
    
    suite.add("Signal connection", connect_handler, iterations=100)
    
    # Emission with handlers
    for i in range(100):
        def handler():
            pass
        sig.connect(handler)
    
    def emit_signal():
        sig.emit()
    
    suite.add("Emit to 100 handlers", emit_signal)
    
    # Signal manager
    manager = SignalManager()
    
    def manager_emit():
        manager.emit('test', 42)
    
    suite.add("SignalManager emit", manager_emit, iterations=1000)
    
    return suite.run()


def benchmark_threading():
    """Benchmark threading system."""
    suite = BenchmarkSuite()
    
    # ThreadPool creation
    def create_pool():
        pool = ThreadPool(max_workers=4)
        pool.shutdown()
    
    suite.add("ThreadPool creation/shutdown", create_pool)
    
    # Task submission
    def submit_tasks():
        pool = ThreadPool(max_workers=4)
        
        def simple_task(n):
            return n * n
        
        futures = [pool.submit(simple_task, i) for i in range(10)]
        results = [f.result() for f in futures]
        pool.shutdown()
    
    suite.add("Submit 10 simple tasks", submit_tasks)
    
    # CPU-bound tasks
    def submit_cpu_tasks():
        pool = ThreadPool(max_workers=4)
        
        def cpu_task(n):
            total = 0
            for i in range(n):
                total += i * i
            return total
        
        futures = [pool.submit(cpu_task, 1000) for _ in range(4)]
        results = [f.result() for f in futures]
        pool.shutdown()
    
    suite.add("Submit 4 CPU-bound tasks", submit_cpu_tasks)
    
    return suite.run()


def benchmark_brush_system():
    """Benchmark brush system."""
    suite = BenchmarkSuite()
    
    # Brush manager setup
    def setup_brush_manager():
        manager = BrushManager()
        BrushPresets.register_all_to_manager(manager)
    
    suite.add("Brush manager setup", setup_brush_manager)
    
    # Brush retrieval
    manager = BrushManager()
    BrushPresets.register_all_to_manager(manager)
    
    def get_brush():
        manager.get_brush('Pencil')
    
    suite.add("Get brush from manager", get_brush, iterations=1000)
    
    # Pressure curve mapping
    from engine.tools.pixel_art_editor.brushes import PressureCurve
    
    curve = PressureCurve.s_curve()
    
    def map_pressure():
        curve.map(0.5)
    
    suite.add("Pressure curve mapping", map_pressure, iterations=10000)
    
    return suite.run()


def run_all_benchmarks():
    """Run all benchmark suites."""
    print("="*60)
    print("GAME ENGINE STUDIO - PERFORMANCE BENCHMARKS")
    print("="*60)
    print()
    
    all_results = []
    
    # Run each suite
    suites = [
        ("Image Operations", benchmark_image_operations),
        ("Algorithms", benchmark_algorithms),
        ("Binary Format", benchmark_binary_format),
        ("Signals", benchmark_signals),
        ("Threading", benchmark_threading),
        ("Brush System", benchmark_brush_system)
    ]
    
    for name, suite_func in suites:
        print(f"\n{'='*20} {name} {'='*20}")
        results = suite_func()
        all_results.extend(results)
    
    # Overall summary
    print("\n" + "="*60)
    print("OVERALL PERFORMANCE SUMMARY")
    print("="*60)
    print()
    
    # Group by category
    categories = {}
    for result in all_results:
        category = result['name'].split('(')[0].strip()
        if category not in categories:
            categories[category] = []
        categories[category].append(result['mean'])
    
    for category, times in categories.items():
        avg_time = statistics.mean(times)
        print(f"{category:.<30} {avg_time:.4f}s avg")
    
    print()
    print("Benchmarks complete!")
    
    return all_results


if __name__ == '__main__':
    run_all_benchmarks()

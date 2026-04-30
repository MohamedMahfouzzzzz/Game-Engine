# /**************************************************************************/
# /*  cli_interface.py                                                      */
# /**************************************************************************/

"""Command-line interface for headless operations.

Provides argument parsing and command execution for CLI usage.
"""

from typing import List, Optional, Dict, Any
from argparse import ArgumentParser, Namespace
from pathlib import Path
import sys

from .headless_engine import HeadlessEngine, HeadlessMode, OperationResult


class CLIInterface:
    """Command-line interface for the game engine.
    
    Handles argument parsing and executes commands in headless mode.
    
    Example:
        # Command line usage:
        python -m engine.headless convert input.ges output.png
        python -m engine.headless batch --input-dir ./assets --output-dir ./exports
        python -m engine.headless validate project.ges
    """
    
    def __init__(self):
        self._engine: Optional[HeadlessEngine] = None
        self._parser = self._create_parser()
    
    def _create_parser(self) -> ArgumentParser:
        """Create the argument parser."""
        parser = ArgumentParser(
            prog='game-engine',
            description='Game Engine Studio - CLI'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Convert command
        convert_parser = subparsers.add_parser(
            'convert',
            help='Convert between formats'
        )
        convert_parser.add_argument('input', help='Input file')
        convert_parser.add_argument('output', help='Output file')
        convert_parser.add_argument(
            '--format',
            choices=['PNG', 'GIF', 'BMP', 'GES'],
            default='PNG',
            help='Output format'
        )
        
        # Validate command
        validate_parser = subparsers.add_parser(
            'validate',
            help='Validate a project file'
        )
        validate_parser.add_argument('file', help='File to validate')
        
        # Batch command
        batch_parser = subparsers.add_parser(
            'batch',
            help='Batch process files'
        )
        batch_parser.add_argument(
            '--input-dir', '-i',
            required=True,
            help='Input directory'
        )
        batch_parser.add_argument(
            '--output-dir', '-o',
            required=True,
            help='Output directory'
        )
        batch_parser.add_argument(
            '--format', '-f',
            default='PNG',
            help='Output format'
        )
        batch_parser.add_argument(
            '--recursive', '-r',
            action='store_true',
            help='Process subdirectories'
        )
        
        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Show file information'
        )
        info_parser.add_argument('file', help='File to inspect')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with arguments.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
        
        Returns:
            Exit code (0 = success)
        """
        parsed = self._parser.parse_args(args)
        
        if not parsed.command:
            self._parser.print_help()
            return 1
        
        # Initialize engine
        self._engine = HeadlessEngine()
        self._engine.set_log_callback(self._print_log)
        self._engine.set_progress_callback(self._print_progress)
        
        if not self._engine.initialize():
            print("Failed to initialize engine", file=sys.stderr)
            return 1
        
        try:
            # Execute command
            if parsed.command == 'convert':
                return self._cmd_convert(parsed)
            elif parsed.command == 'validate':
                return self._cmd_validate(parsed)
            elif parsed.command == 'batch':
                return self._cmd_batch(parsed)
            elif parsed.command == 'info':
                return self._cmd_info(parsed)
            else:
                print(f"Unknown command: {parsed.command}", file=sys.stderr)
                return 1
                
        finally:
            self._engine.shutdown()
    
    def _cmd_convert(self, args: Namespace) -> int:
        """Execute convert command."""
        print(f"Converting {args.input} -> {args.output} ({args.format})")
        
        # Load
        result = self._engine.load_project(args.input)
        if not result.success:
            print(f"Error: {result.message}", file=sys.stderr)
            return 1
        
        # Export
        result = self._engine.export(args.output, format=args.format)
        if not result.success:
            print(f"Error: {result.message}", file=sys.stderr)
            return 1
        
        print(f"Success: {result.message}")
        print(f"Time: {result.execution_time:.2f}s")
        return 0
    
    def _cmd_validate(self, args: Namespace) -> int:
        """Execute validate command."""
        print(f"Validating: {args.file}")
        
        result = self._engine.validate(args.file)
        
        if result.success:
            print(f"✓ {result.message}")
            if result.data:
                info = result.data
                print(f"  Version: {info.get('version', 'unknown')}")
                print(f"  Size: {info.get('width')}x{info.get('height')}")
                print(f"  Layers: {info.get('layers')}")
                print(f"  Frames: {info.get('frames')}")
                print(f"  File size: {info.get('size', 0)} bytes")
            return 0
        else:
            print(f"✗ {result.message}", file=sys.stderr)
            return 1
    
    def _cmd_batch(self, args: Namespace) -> int:
        """Execute batch command."""
        from .batch_processor import BatchProcessor
        
        print(f"Batch processing: {args.input_dir} -> {args.output_dir}")
        
        processor = BatchProcessor(self._engine)
        
        results = processor.process_directory(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            output_format=args.format,
            recursive=args.recursive
        )
        
        # Report
        success_count = sum(1 for r in results if r.success)
        total = len(results)
        
        print(f"\nProcessed: {success_count}/{total} files")
        
        # Show failed files
        failed = [r for r in results if not r.success]
        if failed:
            print("\nFailed files:")
            for r in failed:
                print(f"  - {r.message}")
        
        return 0 if success_count == total else 1
    
    def _cmd_info(self, args: Namespace) -> int:
        """Execute info command."""
        result = self._engine.validate(args.file)
        
        if not result.success:
            print(f"Error: {result.message}", file=sys.stderr)
            return 1
        
        info = result.data
        
        print(f"File: {args.file}")
        print(f"Format: GES v{info.get('version', 'unknown')}")
        print(f"Dimensions: {info.get('width')}x{info.get('height')} pixels")
        print(f"Layers: {info.get('layers')}")
        print(f"Frames: {info.get('frames')}")
        print(f"File size: {info.get('size', 0):,} bytes")
        
        return 0
    
    def _print_log(self, message: str) -> None:
        """Print log message."""
        print(f"[LOG] {message}", file=sys.stderr)
    
    def _print_progress(self, progress: float, message: str) -> None:
        """Print progress."""
        percent = int(progress * 100)
        if message:
            print(f"[{percent:3d}%] {message}", file=sys.stderr)
        else:
            print(f"[{percent:3d}%]", file=sys.stderr)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point."""
    cli = CLIInterface()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())

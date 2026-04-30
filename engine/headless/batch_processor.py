# /**************************************************************************/
# /*  batch_processor.py                                                    */
# /**************************************************************************/

"""Batch processing for multiple files.

Processes multiple files in a directory, useful for:
- Converting formats
- Exporting assets
- Automated builds
"""

from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import os

from .headless_engine import HeadlessEngine, OperationResult


class BatchJob:
    """A single batch job."""
    
    def __init__(self, input_path: str, output_path: str, 
                 operation: str, options: Optional[Dict[str, Any]] = None):
        self.input_path = input_path
        self.output_path = output_path
        self.operation = operation
        self.options = options or {}
        self.result: Optional[OperationResult] = None
    
    def __repr__(self) -> str:
        return f"BatchJob({self.operation}: {self.input_path} -> {self.output_path})"


class BatchProcessor:
    """Processes multiple files in batch.
    
    Manages a queue of jobs and executes them sequentially.
    
    Example:
        processor = BatchProcessor(engine)
        
        jobs = [
            BatchJob('a.ges', 'a.png', 'export'),
            BatchJob('b.ges', 'b.png', 'export'),
        ]
        
        results = processor.process_jobs(jobs)
    """
    
    def __init__(self, engine: HeadlessEngine):
        self._engine = engine
        
        # Callbacks
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None
        self._job_complete_callback: Optional[Callable[[BatchJob], None]] = None
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """Set callback for progress (current, total, message)."""
        self._progress_callback = callback
    
    def set_job_complete_callback(self, callback: Callable[[BatchJob], None]) -> None:
        """Set callback for job completion."""
        self._job_complete_callback = callback
    
    def process_jobs(self, jobs: List[BatchJob]) -> List[OperationResult]:
        """Process a list of batch jobs.
        
        Args:
            jobs: List of jobs to process
        
        Returns:
            List of results (one per job)
        """
        results = []
        total = len(jobs)
        
        for i, job in enumerate(jobs, 1):
            self._report_progress(i, total, f"Processing {Path(job.input_path).name}...")
            
            # Execute job
            result = self._execute_job(job)
            job.result = result
            results.append(result)
            
            # Notify
            if self._job_complete_callback:
                self._job_complete_callback(job)
        
        self._report_progress(total, total, "Complete")
        return results
    
    def _execute_job(self, job: BatchJob) -> OperationResult:
        """Execute a single job."""
        try:
            if job.operation == 'export':
                return self._do_export(job)
            elif job.operation == 'convert':
                return self._do_convert(job)
            elif job.operation == 'validate':
                return self._do_validate(job)
            else:
                return OperationResult(
                    success=False,
                    message=f"Unknown operation: {job.operation}"
                )
        except Exception as e:
            return OperationResult(
                success=False,
                message=str(e),
                error=e
            )
    
    def _do_export(self, job: BatchJob) -> OperationResult:
        """Execute export job."""
        # Load
        load_result = self._engine.load_project(job.input_path)
        if not load_result.success:
            return load_result
        
        # Export
        format = job.options.get('format', 'PNG')
        return self._engine.export(job.output_path, format=format)
    
    def _do_convert(self, job: BatchJob) -> OperationResult:
        """Execute convert job."""
        # Same as export for now
        return self._do_export(job)
    
    def _do_validate(self, job: BatchJob) -> OperationResult:
        """Execute validate job."""
        return self._engine.validate(job.input_path)
    
    def _report_progress(self, current: int, total: int, message: str) -> None:
        """Report progress."""
        if self._progress_callback:
            self._progress_callback(current, total, message)
    
    def process_directory(self,
                        input_dir: str,
                        output_dir: str,
                        input_pattern: str = "*.ges",
                        output_format: str = "PNG",
                        recursive: bool = False) -> List[OperationResult]:
        """Process all matching files in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            input_pattern: Glob pattern for input files
            output_format: Output format
            recursive: Search subdirectories
        
        Returns:
            List of results
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find input files
        if recursive:
            input_files = list(input_path.rglob(input_pattern))
        else:
            input_files = list(input_path.glob(input_pattern))
        
        # Create jobs
        jobs = []
        for input_file in input_files:
            # Compute output path
            relative = input_file.relative_to(input_path)
            output_file = output_path / relative.with_suffix(f'.{output_format.lower()}')
            
            # Ensure output subdirectory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            job = BatchJob(
                str(input_file),
                str(output_file),
                'export',
                {'format': output_format}
            )
            jobs.append(job)
        
        # Process
        return self.process_jobs(jobs)
    
    def create_sprite_sheet(self,
                          input_files: List[str],
                          output_path: str,
                          columns: int = 8,
                          padding: int = 0) -> OperationResult:
        """Create a sprite sheet from multiple files.
        
        Args:
            input_files: List of input file paths
            output_path: Output sprite sheet path
            columns: Number of columns in sheet
            padding: Padding between sprites
        
        Returns:
            OperationResult
        """
        try:
            from PIL import Image
            
            # Load all images
            images = []
            for filepath in input_files:
                result = self._engine.load_project(filepath)
                if result.success and self._engine.document:
                    # Would render document here
                    # For now, create placeholder
                    img = Image.new('RGBA', (32, 32), (255, 0, 0, 128))
                    images.append(img)
            
            if not images:
                return OperationResult(
                    success=False,
                    message="No images to process"
                )
            
            # Calculate sheet size
            sprite_width = images[0].width
            sprite_height = images[0].height
            
            rows = (len(images) + columns - 1) // columns
            
            sheet_width = columns * (sprite_width + padding) + padding
            sheet_height = rows * (sprite_height + padding) + padding
            
            # Create sheet
            sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
            
            # Place images
            for i, img in enumerate(images):
                col = i % columns
                row = i // columns
                
                x = padding + col * (sprite_width + padding)
                y = padding + row * (sprite_height + padding)
                
                sheet.paste(img, (x, y))
            
            # Save
            sheet.save(output_path)
            
            return OperationResult(
                success=True,
                message=f"Created sprite sheet: {len(images)} sprites, "
                        f"{columns}x{rows} layout",
                data={'sprites': len(images), 'columns': columns, 'rows': rows}
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                message=str(e),
                error=e
            )
    
    def get_stats(self, results: List[OperationResult]) -> Dict[str, Any]:
        """Get statistics from a batch of results."""
        total = len(results)
        success = sum(1 for r in results if r.success)
        failed = total - success
        
        total_time = sum(r.execution_time for r in results)
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'success_rate': success / total if total > 0 else 0,
            'total_time': total_time,
            'average_time': total_time / total if total > 0 else 0,
        }

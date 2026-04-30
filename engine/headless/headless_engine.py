# /**************************************************************************/
# /*  headless_engine.py                                                    */
# /**************************************************************************/

"""Headless engine core for CLI operations.

Runs the engine without any UI components for automated operations.
"""

from typing import Optional, Dict, Any, Callable, List
from enum import Enum, auto
from dataclasses import dataclass
import time
import sys

from engine.core.project_secure import SecureProject
from engine.tools.pixel_art_editor.core import Document
from engine.io import BinaryFormat


class HeadlessMode(Enum):
    """Headless operation mode."""
    BATCH_PROCESS = auto()   # Process multiple files
    RENDER = auto()          # Render/Export only
    CONVERT = auto()         # Format conversion
    VALIDATE = auto()        # Validate projects
    AUTOMATED_TEST = auto()  # Run automated tests


@dataclass
class OperationResult:
    """Result of a headless operation."""
    success: bool
    message: str = ""
    data: Any = None
    execution_time: float = 0.0
    error: Optional[Exception] = None


class HeadlessEngine:
    """Engine core for headless/CLI operations.
    
    Provides core functionality without UI:
    - Project loading/saving
    - Export/render operations
    - Batch processing
    - Validation
    
    Example:
        engine = HeadlessEngine()
        engine.initialize()
        
        # Load and export
        result = engine.load_project('input.ges')
        engine.export('output.png', format='PNG')
        
        engine.shutdown()
    """
    
    def __init__(self):
        self._initialized = False
        self._project: Optional[SecureProject] = None
        self._document: Optional[Document] = None
        
        # Callbacks for progress reporting
        self._progress_callback: Optional[Callable[[float, str], None]] = None
        self._log_callback: Optional[Callable[[str], None]] = None
        
        # Statistics
        self._operations_count = 0
        self._errors_count = 0
        self._start_time = 0.0
    
    def initialize(self) -> bool:
        """Initialize the headless engine."""
        if self._initialized:
            return True
        
        try:
            # Initialize core systems (no UI)
            self._log("Initializing headless engine...")
            
            # Could load plugins here
            
            self._initialized = True
            self._start_time = time.time()
            self._log("Headless engine ready")
            return True
            
        except Exception as e:
            self._error(f"Initialization failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the headless engine."""
        if not self._initialized:
            return
        
        runtime = time.time() - self._start_time
        self._log(f"Shutting down. Runtime: {runtime:.2f}s, "
                  f"Operations: {self._operations_count}, "
                  f"Errors: {self._errors_count}")
        
        self._initialized = False
    
    def set_progress_callback(self, callback: Callable[[float, str], None]) -> None:
        """Set callback for progress updates (0.0-1.0, message)."""
        self._progress_callback = callback
    
    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for log messages."""
        self._log_callback = callback
    
    def _log(self, message: str) -> None:
        """Log a message."""
        if self._log_callback:
            self._log_callback(message)
        else:
            print(message, file=sys.stderr)
    
    def _error(self, message: str) -> None:
        """Log an error."""
        self._errors_count += 1
        self._log(f"ERROR: {message}")
    
    def _progress(self, progress: float, message: str = "") -> None:
        """Report progress."""
        if self._progress_callback:
            self._progress_callback(progress, message)
    
    def load_project(self, filepath: str) -> OperationResult:
        """Load a project file.
        
        Args:
            filepath: Path to project file
        
        Returns:
            OperationResult with loaded project
        """
        start = time.time()
        self._operations_count += 1
        
        try:
            self._log(f"Loading project: {filepath}")
            self._progress(0.1, "Loading...")
            
            # Try binary format first
            document = BinaryFormat.load(filepath)
            
            if document:
                self._document = document
                self._progress(1.0, "Loaded")
                return OperationResult(
                    success=True,
                    message=f"Loaded {document.name}",
                    data=document,
                    execution_time=time.time() - start
                )
            
            return OperationResult(
                success=False,
                message="Failed to load project",
                execution_time=time.time() - start
            )
            
        except Exception as e:
            self._error(f"Load failed: {e}")
            return OperationResult(
                success=False,
                message=str(e),
                error=e,
                execution_time=time.time() - start
            )
    
    def save_project(self, filepath: str, 
                     document: Optional[Document] = None) -> OperationResult:
        """Save a project file.
        
        Args:
            filepath: Output path
            document: Document to save (uses current if None)
        
        Returns:
            OperationResult
        """
        start = time.time()
        self._operations_count += 1
        
        doc = document or self._document
        if not doc:
            return OperationResult(
                success=False,
                message="No document to save"
            )
        
        try:
            self._log(f"Saving project: {filepath}")
            self._progress(0.5, "Saving...")
            
            success = BinaryFormat.save(doc, filepath)
            
            self._progress(1.0, "Saved")
            return OperationResult(
                success=success,
                message="Project saved" if success else "Save failed",
                execution_time=time.time() - start
            )
            
        except Exception as e:
            self._error(f"Save failed: {e}")
            return OperationResult(
                success=False,
                message=str(e),
                error=e,
                execution_time=time.time() - start
            )
    
    def export(self, filepath: str, format: str = "PNG",
               options: Optional[Dict[str, Any]] = None) -> OperationResult:
        """Export current document to image format.
        
        Args:
            filepath: Output file path
            format: Export format (PNG, GIF, BMP, etc.)
            options: Format-specific options
        
        Returns:
            OperationResult
        """
        start = time.time()
        self._operations_count += 1
        
        if not self._document:
            return OperationResult(
                success=False,
                message="No document loaded"
            )
        
        try:
            self._log(f"Exporting to {format}: {filepath}")
            self._progress(0.3, "Rendering...")
            
            # Render document (placeholder - would use actual renderer)
            from PIL import Image
            
            # Create simple export (would be more complex in reality)
            width = self._document.width
            height = self._document.height
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            self._progress(0.6, "Encoding...")
            
            # Save
            img.save(filepath, format=format)
            
            self._progress(1.0, "Exported")
            return OperationResult(
                success=True,
                message=f"Exported to {filepath}",
                data=filepath,
                execution_time=time.time() - start
            )
            
        except Exception as e:
            self._error(f"Export failed: {e}")
            return OperationResult(
                success=False,
                message=str(e),
                error=e,
                execution_time=time.time() - start
            )
    
    def validate(self, filepath: str) -> OperationResult:
        """Validate a project file without loading it fully.
        
        Args:
            filepath: Path to file to validate
        
        Returns:
            OperationResult with validation info
        """
        start = time.time()
        self._operations_count += 1
        
        try:
            self._log(f"Validating: {filepath}")
            
            # Get file info without full load
            info = BinaryFormat.get_info(filepath)
            
            if info:
                return OperationResult(
                    success=True,
                    message=f"Valid {info['version']} file: "
                            f"{info['width']}x{info['height']}, "
                            f"{info['layers']} layers",
                    data=info,
                    execution_time=time.time() - start
                )
            
            return OperationResult(
                success=False,
                message="Invalid or corrupted file",
                execution_time=time.time() - start
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                message=str(e),
                error=e,
                execution_time=time.time() - start
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        runtime = time.time() - self._start_time if self._start_time > 0 else 0
        return {
            'initialized': self._initialized,
            'runtime': runtime,
            'operations': self._operations_count,
            'errors': self._errors_count,
            'document_loaded': self._document is not None,
        }
    
    @property
    def document(self) -> Optional[Document]:
        """Get currently loaded document."""
        return self._document
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()

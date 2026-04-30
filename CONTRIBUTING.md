# Contributing to Game Engine Studio

Thank you for your interest in contributing to Game Engine Studio! This guide will help you get started.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Submitting Changes](#submitting-changes)
8. [Review Process](#review-process)

## Code of Conduct

Please be respectful and inclusive. We welcome contributors of all backgrounds and experience levels.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code recommended)

### Setup

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/yourusername/game_engine_studio.git
cd game_engine_studio
```

3. Add the upstream repository:
```bash
git remote add upstream https://github.com/original/game_engine_studio.git
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. Run tests to verify setup:
```bash
python run_tests.py
```

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Follow the coding standards below
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
python run_tests.py

# Run specific test
python -m unittest tests.test_module

# Run with coverage
coverage run run_tests.py
coverage report
```

### 4. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: Add new brush type for pixel art"
```

### 5. Keep Updated

Before submitting, sync with upstream:

```bash
git fetch upstream
git rebase upstream/main
```

### 6. Submit Pull Request

Push your branch and create a pull request on GitHub.

## Coding Standards

### Python Style

Follow PEP 8 with these modifications:

- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Use snake_case for variables and functions
- Use PascalCase for classes
- Use UPPER_CASE for constants

### Imports

Group imports in this order:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import os
import sys
from typing import List, Optional

import numpy as np
from PIL import Image

from engine.core import Entity
from engine.tools.pixel_art_editor.core import Document
```

### Docstrings

Use Google-style docstrings:

```python
def process_image(image_data: bytes, format: str = 'PNG') -> Image.Image:
    """Process image data and return PIL Image.
    
    Args:
        image_data: Raw image data in bytes
        format: Image format ('PNG', 'JPEG', etc.)
    
    Returns:
        PIL Image object
    
    Raises:
        ValueError: If format is not supported
        IOError: If image data is corrupted
    """
    pass
```

### Type Hints

Use type hints for all public functions and methods:

```python
from typing import List, Dict, Optional, Union

def get_layers(document: Document) -> List[Layer]:
    """Get all layers from document."""
    return document.sprite.layers

def process_data(data: Dict[str, Union[str, int]]) -> Optional[str]:
    """Process data dictionary."""
    if 'key' in data:
        return str(data['key'])
    return None
```

### Error Handling

- Use specific exceptions
- Include helpful error messages
- Use logging for debugging

```python
import logging

logger = logging.getLogger(__name__)

def load_document(path: str) -> Optional[Document]:
    """Load document from file path."""
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        return BinaryFormat.load(path)
    except Exception as e:
        logger.error(f"Failed to load document: {e}")
        return None
```

## Testing

### Writing Tests

- Write unit tests for all new functionality
- Test both success and failure cases
- Use descriptive test names

```python
class TestNewFeature(unittest.TestCase):
    """Test new feature functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.doc = Document(32, 32, 'Test')
    
    def test_basic_functionality(self):
        """Test basic feature works correctly."""
        result = new_feature(self.doc)
        self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Test error cases are handled properly."""
        with self.assertRaises(ValueError):
            new_feature(None)
```

### Test Coverage

- Aim for >80% code coverage
- Focus on critical paths
- Test edge cases

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run with coverage
coverage run run_tests.py
coverage html  # Generate HTML report
```

## Documentation

### API Documentation

- Update API_REFERENCE.md for new public APIs
- Include examples in docstrings
- Document parameters and return values

### Code Comments

- Comment complex algorithms
- Explain non-obvious logic
- Use TODO/FIXME for temporary notes

```python
# TODO: Optimize this loop for large images
for y in range(height):
    for x in range(width):
        # Apply gaussian blur kernel
        pixel = apply_kernel(image, x, y, kernel)
        result.set_pixel(x, y, pixel)
```

### README Updates

- Update README.md for significant features
- Update installation instructions if needed
- Add new examples

## Submitting Changes

### Pull Request Guidelines

1. **Title**: Use clear, descriptive title
   - "feat: Add new brush system"
   - "fix: Resolve memory leak in image loading"
   - "docs: Update API reference"

2. **Description**: Explain what and why
   - What problem does this solve?
   - How did you solve it?
   - Are there any breaking changes?

3. **Testing**: Show tests pass
   - Include test output
   - Mention manual testing done

4. **Documentation**: Link to docs
   - Reference updated documentation
   - Include screenshots if UI changes

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

## Review Process

### What Reviewers Look For

1. **Code Quality**
   - Clean, readable code
   - Good design patterns
   - Proper error handling

2. **Functionality**
   - Works as intended
   - No regressions
   - Performance impact

3. **Testing**
   - Adequate test coverage
   - Tests are meaningful
   - Edge cases covered

4. **Documentation**
   - Clear explanations
   - Examples provided
   - API docs updated

### Responding to Reviews

- Address all feedback
- Explain design decisions
- Update code as requested
- Be respectful and collaborative

## Development Tools

### Recommended VS Code Extensions

- Python
- Pylance
- Python Docstring Generator
- GitLens
- Coverage Gutters

### Pre-commit Hooks

Set up pre-commit hooks to automatically check code:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Performance Guidelines

### Optimization

- Profile before optimizing
- Focus on hot paths
- Use appropriate data structures
- Consider memory usage

### Benchmarks

Add benchmarks for performance-critical code:

```python
def benchmark_image_processing():
    """Benchmark image processing performance."""
    import time
    
    img = ImageBuffer(1024, 1024, ColorMode.RGBA)
    
    start = time.time()
    process_image(img)
    elapsed = time.time() - start
    
    print(f"Processed 1024x1024 image in {elapsed:.3f}s")
```

## Security

### Guidelines

- Validate all inputs
- Use secure defaults
- Don't expose sensitive data
- Follow principle of least privilege

### Reporting Security Issues

If you find a security vulnerability:

1. Do not open a public issue
2. Email security@example.com
3. Include details and reproduction steps
4. We'll respond within 48 hours

## Getting Help

### Resources

- [API Reference](API_REFERENCE.md)
- [Tutorial](TUTORIAL.md)
- [GitHub Issues](https://github.com/yourusername/game_engine_studio/issues)
- [Discord Community](https://discord.gg/gameengine)

### Asking Questions

- Check existing issues first
- Provide minimal reproduction case
- Include error messages and logs
- Be patient and respectful

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Game Engine Studio! 🎮

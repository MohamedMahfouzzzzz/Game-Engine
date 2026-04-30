# /**************************************************************************/
# /*  conftest.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""pytest configuration for game_engine_studio tests."""
import sys
import os
import asyncio
import pytest

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# pytest-asyncio configuration
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def benchmark():
    """Lightweight fallback for environments without pytest-benchmark."""
    def run(func, *args, **kwargs):
        return func(*args, **kwargs)

    return run


def pytest_configure(config):
    """Configure pytest-asyncio mode."""
    config.option.asyncio_mode = "auto"

"""Compatibility project API.

Older editor and test modules import ``engine.core.project``.  The secure
project implementation is the canonical implementation, so this module keeps
that import stable without duplicating project logic.
"""

from engine.core.project_secure import PROJECT_FILE_MAGIC, ProjectConfig, SecureProject

Project = SecureProject

__all__ = ["Project", "ProjectConfig", "SecureProject", "PROJECT_FILE_MAGIC"]

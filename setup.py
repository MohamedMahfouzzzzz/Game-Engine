#!/usr/bin/env python
"""Setup script for Game Engine Studio."""

from setuptools import setup, find_packages
import os

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

install_requires = read_requirements('requirements.txt') if os.path.exists('requirements.txt') else []
dev_requires = read_requirements('requirements-dev.txt') if os.path.exists('requirements-dev.txt') else []

setup(
    name='game-engine-studio',
    version='1.0.0',
    description='A comprehensive 2D game engine with pixel art editor',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Game Engine Studio Team',
    author_email='contact@gameengine.studio',
    url='https://github.com/yourusername/game_engine_studio',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/game_engine_studio/issues',
        'Source': 'https://github.com/yourusername/game_engine_studio',
        'Documentation': 'https://gameengine.studio/docs',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'benchmarks', 'examples']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: pygame',
    ],
    python_requires='>=3.8',
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'coverage>=6.0',
        ],
        'profile': [
            'memory-profiler>=0.60',
            'line-profiler>=3.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'game-engine=engine.headless.cli_interface:main',
            'ges=engine.headless.cli_interface:main',
        ],
    },
    include_package_data=True,
    package_data={
        'engine': [
            'tools/pixel_art_editor/brushes/presets/*.json',
            'tools/pixel_art_editor/algorithms/patterns/*.json',
        ],
    },
    zip_safe=False,
    keywords=[
        'game engine',
        '2d',
        'pixel art',
        'graphics',
        'animation',
        'python',
        'pygame',
    ],
)

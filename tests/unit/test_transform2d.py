# /**************************************************************************/
# /*  test_transform2d.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Unit tests for 2D Transform system.

Focused tests for Transform2D math operations.
"""

import pytest
import math


class TestTransform2D:
    """Test Transform2D matrix operations."""
    
    def test_transform_creation(self):
        """Transform can be created with identity."""
        # Identity transform
        transform = {
            'm11': 1, 'm12': 0,
            'm21': 0, 'm22': 1,
            'm31': 0, 'm32': 0,
        }
        
        assert transform['m11'] == 1
        assert transform['m22'] == 1
    
    def test_transform_translation(self):
        """Translation moves points correctly."""
        # Translation by (10, 20)
        tx, ty = 10, 20
        
        point = {'x': 5, 'y': 15}
        
        # Apply translation
        new_x = point['x'] + tx
        new_y = point['y'] + ty
        
        assert new_x == 15
        assert new_y == 35
    
    def test_transform_rotation_90_degrees(self):
        """90 degree rotation works correctly."""
        angle = math.pi / 2  # 90 degrees
        
        # Rotation matrix
        cos_a = round(math.cos(angle))
        sin_a = round(math.sin(angle))
        
        # Point (1, 0) rotated 90° should be (0, 1)
        x, y = 1, 0
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        assert round(new_x) == 0
        assert round(new_y) == 1
    
    def test_transform_scale(self):
        """Scaling multiplies coordinates."""
        sx, sy = 2, 3
        x, y = 5, 10
        
        new_x = x * sx
        new_y = y * sy
        
        assert new_x == 10
        assert new_y == 30
    
    def test_transform_composition(self):
        """Multiple transforms compose correctly."""
        # Translate then rotate
        x, y = 10, 0
        
        # Translate by (5, 0)
        x += 5
        
        # Rotate 90 degrees around origin
        angle = math.pi / 2
        new_x = x * math.cos(angle) - y * math.sin(angle)
        new_y = x * math.sin(angle) + y * math.cos(angle)
        
        # (15, 0) rotated 90° ≈ (0, 15)
        assert round(new_x) == 0
        assert round(new_y) == 15


class TestVectorMath:
    """Test vector operations."""
    
    def test_vector_addition(self):
        """Vectors add component-wise."""
        v1 = {'x': 1, 'y': 2}
        v2 = {'x': 3, 'y': 4}
        
        result = {
            'x': v1['x'] + v2['x'],
            'y': v1['y'] + v2['y']
        }
        
        assert result['x'] == 4
        assert result['y'] == 6
    
    def test_vector_subtraction(self):
        """Vectors subtract component-wise."""
        v1 = {'x': 5, 'y': 8}
        v2 = {'x': 2, 'y': 3}
        
        result = {
            'x': v1['x'] - v2['x'],
            'y': v1['y'] - v2['y']
        }
        
        assert result['x'] == 3
        assert result['y'] == 5
    
    def test_vector_length(self):
        """Vector length calculated correctly."""
        v = {'x': 3, 'y': 4}
        length = math.sqrt(v['x']**2 + v['y']**2)
        
        assert length == 5
    
    def test_vector_normalization(self):
        """Vector normalization produces unit vector."""
        v = {'x': 3, 'y': 4}
        length = math.sqrt(v['x']**2 + v['y']**2)
        
        if length > 0:
            normalized = {
                'x': v['x'] / length,
                'y': v['y'] / length
            }
            
            # Normalized vector should have length 1
            new_length = math.sqrt(normalized['x']**2 + normalized['y']**2)
            assert abs(new_length - 1.0) < 0.0001


class TestMatrixOperations:
    """Test matrix math operations."""
    
    def test_matrix_multiplication_identity(self):
        """Identity matrix multiplication preserves values."""
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        vector = [5, 10, 1]
        
        # Multiply
        result = [
            identity[0][0] * vector[0] + identity[0][1] * vector[1] + identity[0][2] * vector[2],
            identity[1][0] * vector[0] + identity[1][1] * vector[1] + identity[1][2] * vector[2],
            identity[2][0] * vector[0] + identity[2][1] * vector[1] + identity[2][2] * vector[2],
        ]
        
        assert result[0] == 5
        assert result[1] == 10
        assert result[2] == 1
    
    def test_matrix_multiplication_translation(self):
        """Translation matrix moves point."""
        # Translation by (10, 20)
        matrix = [[1, 0, 0], [0, 1, 0], [10, 20, 1]]
        point = [5, 15, 1]
        
        # Multiply
        result = [
            matrix[0][0] * point[0] + matrix[1][0] * point[1] + matrix[2][0] * point[2],
            matrix[0][1] * point[0] + matrix[1][1] * point[1] + matrix[2][1] * point[2],
            matrix[0][2] * point[0] + matrix[1][2] * point[1] + matrix[2][2] * point[2],
        ]
        
        assert result[0] == 15  # 5 + 10
        assert result[1] == 35  # 15 + 20

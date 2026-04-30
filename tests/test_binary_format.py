# /**************************************************************************/
# /*  test_binary_format.py                                                 */
# /**************************************************************************/

"""Unit tests for binary format (GES) I/O."""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.core import Document, Layer
from engine.io import BinaryFormat, GESReader, GESWriter


class TestBinaryFormat(unittest.TestCase):
    """Test binary format save/load."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.ges')
        self.doc = Document(64, 64, 'TestDocument')
    
    def tearDown(self):
        # Cleanup
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_save_document(self):
        """Test saving a document."""
        success = BinaryFormat.save(self.doc, self.test_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_load_document(self):
        """Test loading a saved document."""
        BinaryFormat.save(self.doc, self.test_file)
        loaded = BinaryFormat.load(self.test_file)
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, 'TestDocument')
        self.assertEqual(loaded.width, 64)
        self.assertEqual(loaded.height, 64)
    
    def test_round_trip(self):
        """Test save and load preserves data."""
        # Add some data
        self.doc.sprite.add_layer('Layer 1')
        self.doc.sprite.add_layer('Layer 2')
        self.doc.sprite.add_frame(100)
        
        # Save and load
        BinaryFormat.save(self.doc, self.test_file)
        loaded = BinaryFormat.load(self.test_file)
        
        # Verify
        self.assertEqual(loaded.sprite.layer_count, 3)  # 2 added + 1 default
        self.assertEqual(loaded.sprite.frame_count, 2)  # 1 added + 1 default
    
    def test_get_info(self):
        """Test getting file info without loading."""
        BinaryFormat.save(self.doc, self.test_file)
        info = BinaryFormat.get_info(self.test_file)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['width'], 64)
        self.assertEqual(info['height'], 64)
        self.assertEqual(info['version'], '1.0.0')
    
    def test_invalid_file(self):
        """Test loading invalid file."""
        # Create invalid file
        with open(self.test_file, 'wb') as f:
            f.write(b'NOT_A_VALID_GES_FILE')
        
        loaded = BinaryFormat.load(self.test_file)
        self.assertIsNone(loaded)
    
    def test_nonexistent_file(self):
        """Test loading non-existent file."""
        loaded = BinaryFormat.load('nonexistent.ges')
        self.assertIsNone(loaded)
    
    def test_document_with_metadata(self):
        """Test saving/loading document with metadata."""
        self.doc.author = 'Test Author'
        self.doc.description = 'Test Description'
        
        BinaryFormat.save(self.doc, self.test_file)
        loaded = BinaryFormat.load(self.test_file)
        
        self.assertEqual(loaded.author, 'Test Author')
        self.assertEqual(loaded.description, 'Test Description')


if __name__ == '__main__':
    unittest.main()

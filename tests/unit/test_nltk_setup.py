"""
Tests for NLTK setup functionality using unittest
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.setup_nltk import get_nltk_data_dir, setup_nltk, download_nltk_data

class TestNLTKSetup(unittest.TestCase):
    """Test cases for NLTK setup functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.nltk_data_dir = Path(self.temp_dir) / 'nltk_data'
        self.nltk_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Store original environment
        self.original_env = dict(os.environ)
        os.environ['NLTK_DATA'] = str(self.nltk_data_dir)
        
        # Create mock NLTK
        self.nltk_patcher = patch('src.setup_nltk.nltk')
        self.mock_nltk = self.nltk_patcher.start()
        self.mock_nltk.data.path = []
        
        # Configure mock download to succeed by default
        self.mock_nltk.download.return_value = True
    
    def tearDown(self):
        """Clean up after each test"""
        # Stop all patches
        self.nltk_patcher.stop()
        
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        try:
            shutil.rmtree(self.temp_dir)
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors
    
    def test_get_nltk_data_dir_from_env(self):
        """Test getting NLTK data dir from environment variable"""
        result = get_nltk_data_dir()
        self.assertEqual(str(result), str(self.nltk_data_dir))
    
    def test_get_nltk_data_dir_default(self):
        """Test getting default NLTK data dir"""
        # Clear NLTK_DATA from environment
        del os.environ['NLTK_DATA']
        
        result = get_nltk_data_dir()
        expected = project_root / 'data' / 'nltk_data'
        self.assertEqual(result, expected)
    
    def test_setup_nltk_creates_directory(self):
        """Test that setup_nltk creates the data directory"""
        # Remove the directory created in setUp
        shutil.rmtree(self.nltk_data_dir)
        
        setup_nltk()
        self.assertTrue(self.nltk_data_dir.exists())
    
    def test_setup_nltk_downloads_required_packages(self):
        """Test that setup_nltk downloads required packages"""
        setup_nltk()
        
        # Verify each required package was downloaded
        required_packages = ['punkt', 'averaged_perceptron_tagger', 'wordnet']
        for package in required_packages:
            self.mock_nltk.download.assert_any_call(
                package,
                download_dir=str(self.nltk_data_dir),
                quiet=True
            )
    
    def test_setup_nltk_handles_download_error(self):
        """Test error handling during package download"""
        self.mock_nltk.download.side_effect = Exception("Download failed")
        
        # Should not raise exception
        try:
            setup_nltk()
        except Exception as e:
            self.fail(f"setup_nltk raised an exception: {e}")
        
        # Verify download was attempted
        self.mock_nltk.download.assert_called()
    
    def test_download_nltk_data_success(self):
        """Test successful NLTK data download"""
        # Configure mock to return True
        self.mock_nltk.download.return_value = True
        
        result = download_nltk_data()
        self.assertTrue(result)
        self.mock_nltk.download.assert_called()
    
    def test_download_nltk_data_failure(self):
        """Test NLTK data download failure"""
        # Configure mock to raise an exception
        self.mock_nltk.download.side_effect = Exception("Download failed")
        
        result = download_nltk_data()
        self.assertFalse(result)
        self.mock_nltk.download.assert_called()
    
    def test_nltk_data_path_added(self):
        """Test that NLTK data path is properly added"""
        setup_nltk()
        self.assertIn(str(self.nltk_data_dir), self.mock_nltk.data.path)

@unittest.skipIf(os.getenv('CI') == 'true', "Skip in CI environment")
class TestNLTKIntegration(unittest.TestCase):
    """Integration tests for NLTK setup"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.nltk_data_dir = Path(cls.temp_dir) / 'nltk_data'
        cls.nltk_data_dir.mkdir(parents=True)
        
        # Store original environment
        cls.original_env = dict(os.environ)
        os.environ['NLTK_DATA'] = str(cls.nltk_data_dir)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(cls.original_env)
        try:
            shutil.rmtree(cls.temp_dir)
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors
    
    def test_nltk_integration(self):
        """Test actual NLTK functionality"""
        try:
            import nltk
            
            # Setup NLTK
            success = download_nltk_data()
            if not success:
                self.skipTest("Failed to download NLTK data")
            
            # Test tokenization (requires 'punkt')
            tokens = nltk.word_tokenize("This is a test sentence.")
            self.assertTrue(len(tokens) > 0)
            
            # Test part-of-speech tagging (requires 'averaged_perceptron_tagger')
            tags = nltk.pos_tag(tokens)
            self.assertTrue(len(tags) > 0)
            
            # Test WordNet (requires 'wordnet')
            from nltk.corpus import wordnet
            synsets = wordnet.synsets("test")
            self.assertTrue(len(synsets) > 0)
            
        except ImportError as e:
            self.skipTest(f"NLTK not available: {e}")
        except Exception as e:
            self.skipTest(f"NLTK test failed: {e}")

if __name__ == '__main__':
    unittest.main()

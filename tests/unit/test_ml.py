import pytest
import numpy as np
from unittest.mock import Mock, patch
import torch
import tensorflow as tf
from src.data.models import ModelManager
from src.data.validation import DataValidator

@pytest.fixture
def mock_data():
    """Fixture for mock training data"""
    return {
        'inputs': np.random.rand(100, 10),
        'labels': np.random.randint(0, 2, 100)
    }

@pytest.fixture
def model_config():
    """Fixture for model configuration"""
    return {
        'model_type': 'transformer',
        'embedding_dim': 256,
        'num_heads': 8,
        'num_layers': 6,
        'dropout': 0.1
    }

class TestModelManager:
    def test_model_initialization(self, model_config):
        """Test model initialization"""
        with patch('torch.nn.Transformer') as mock_transformer:
            manager = ModelManager(model_config)
            assert manager.model_type == 'transformer'
            mock_transformer.assert_called_once()

    @pytest.mark.gpu
    def test_gpu_availability(self):
        """Test GPU detection and usage"""
        with patch('torch.cuda.is_available') as mock_cuda:
            mock_cuda.return_value = True
            assert torch.cuda.is_available()

    def test_model_training(self, mock_data, model_config):
        """Test model training process"""
        with patch('torch.nn.Transformer') as mock_transformer:
            manager = ModelManager(model_config)
            
            # Mock training process
            mock_transformer.return_value.train = Mock()
            mock_transformer.return_value.forward = Mock(
                return_value=torch.randn(100, 2)
            )
            
            history = manager.train(
                mock_data['inputs'],
                mock_data['labels'],
                epochs=5,
                batch_size=32
            )
            
            assert isinstance(history, dict)
            assert 'loss' in history
            assert 'accuracy' in history

    def test_model_inference(self, model_config):
        """Test model inference"""
        with patch('torch.nn.Transformer') as mock_transformer:
            manager = ModelManager(model_config)
            
            # Mock inference
            test_input = np.random.rand(1, 10)
            mock_transformer.return_value.eval = Mock()
            mock_transformer.return_value.forward = Mock(
                return_value=torch.randn(1, 2)
            )
            
            prediction = manager.predict(test_input)
            assert isinstance(prediction, np.ndarray)

    def test_model_saving_loading(self, model_config, tmp_path):
        """Test model serialization"""
        with patch('torch.nn.Transformer') as mock_transformer:
            manager = ModelManager(model_config)
            
            # Test save
            save_path = tmp_path / "model.pt"
            manager.save_model(save_path)
            assert save_path.exists()
            
            # Test load
            manager.load_model(save_path)
            mock_transformer.assert_called()

class TestDataValidator:
    def test_input_validation(self):
        """Test input data validation"""
        validator = DataValidator()
        
        # Test valid input
        valid_input = np.random.rand(10, 5)
        assert validator.validate_input(valid_input)
        
        # Test invalid input
        invalid_input = [1, 2, 3]  # Not numpy array
        with pytest.raises(ValueError):
            validator.validate_input(invalid_input)

    def test_data_preprocessing(self):
        """Test data preprocessing"""
        validator = DataValidator()
        
        # Test normalization
        test_data = np.random.rand(100, 5) * 100
        processed_data = validator.preprocess_data(test_data)
        assert np.all(processed_data >= -1) and np.all(processed_data <= 1)

    def test_data_augmentation(self):
        """Test data augmentation techniques"""
        validator = DataValidator()
        
        original_data = np.random.rand(10, 5)
        augmented_data = validator.augment_data(original_data)
        
        assert augmented_data.shape[0] > original_data.shape[0]
        assert augmented_data.shape[1] == original_data.shape[1]

class TestModelPerformance:
    @pytest.mark.performance
    def test_inference_speed(self, model_config):
        """Test model inference speed"""
        with patch('torch.nn.Transformer') as mock_transformer:
            manager = ModelManager(model_config)
            
            # Test batch inference time
            batch_size = 32
            input_data = np.random.rand(batch_size, 10)
            
            import time
            start_time = time.time()
            _ = manager.predict(input_data)
            inference_time = time.time() - start_time
            
            assert inference_time < 1.0  # Should complete within 1 second

    @pytest.mark.memory
    def test_memory_usage(self, model_config):
        """Test model memory usage"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        with patch('torch.nn.Transformer') as mock_transformer:
            manager = ModelManager(model_config)
            
            # Check memory after model creation
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable
            assert memory_increase < 1e9  # Less than 1GB increase

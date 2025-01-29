import pytest
from unittest.mock import Mock, patch
import json
from src.ai_providers import AIProvider, OpenAIProvider, AnthropicProvider, GeminiProvider

@pytest.fixture
def mock_config():
    """Fixture for AI provider configuration"""
    return {
        'openai': {
            'api_key': 'test_key',
            'model': 'gpt-4'
        },
        'anthropic': {
            'api_key': 'test_key',
            'model': 'claude-2'
        },
        'gemini': {
            'api_key': 'test_key',
            'model': 'gemini-pro'
        }
    }

class TestAIProviders:
    def test_openai_initialization(self, mock_config):
        """Test OpenAI provider initialization"""
        with patch('openai.OpenAI') as mock_openai:
            provider = OpenAIProvider(mock_config['openai'])
            assert provider.model == 'gpt-4'
            mock_openai.assert_called_once_with(api_key='test_key')

    def test_anthropic_initialization(self, mock_config):
        """Test Anthropic provider initialization"""
        with patch('anthropic.Anthropic') as mock_anthropic:
            provider = AnthropicProvider(mock_config['anthropic'])
            assert provider.model == 'claude-2'
            mock_anthropic.assert_called_once_with(api_key='test_key')

    def test_gemini_initialization(self, mock_config):
        """Test Gemini provider initialization"""
        with patch('google.generativeai') as mock_gemini:
            provider = GeminiProvider(mock_config['gemini'])
            assert provider.model == 'gemini-pro'
            mock_gemini.configure.assert_called_once_with(api_key='test_key')

    @pytest.mark.network
    def test_openai_completion(self, mock_config):
        """Test OpenAI text completion"""
        with patch('openai.OpenAI') as mock_openai:
            provider = OpenAIProvider(mock_config['openai'])
            mock_openai.return_value.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="Test response"))]
            )
            
            response = provider.generate_text("Test prompt")
            assert isinstance(response, str)
            assert response == "Test response"

    @pytest.mark.network
    def test_anthropic_completion(self, mock_config):
        """Test Anthropic text completion"""
        with patch('anthropic.Anthropic') as mock_anthropic:
            provider = AnthropicProvider(mock_config['anthropic'])
            mock_anthropic.return_value.messages.create.return_value = Mock(
                content=[Mock(text="Test response")]
            )
            
            response = provider.generate_text("Test prompt")
            assert isinstance(response, str)
            assert response == "Test response"

    @pytest.mark.network
    def test_gemini_completion(self, mock_config):
        """Test Gemini text completion"""
        with patch('google.generativeai') as mock_gemini:
            provider = GeminiProvider(mock_config['gemini'])
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_gemini.generate_text.return_value = mock_response
            
            response = provider.generate_text("Test prompt")
            assert isinstance(response, str)
            assert response == "Test response"

    def test_error_handling(self, mock_config):
        """Test error handling in AI providers"""
        with patch('openai.OpenAI') as mock_openai:
            provider = OpenAIProvider(mock_config['openai'])
            mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                provider.generate_text("Test prompt")

    def test_response_validation(self, mock_config):
        """Test response validation from AI providers"""
        with patch('openai.OpenAI') as mock_openai:
            provider = OpenAIProvider(mock_config['openai'])
            mock_openai.return_value.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content=""))]
            )
            
            response = provider.generate_text("Test prompt")
            assert response == ""  # or handle empty response as needed

    def test_provider_selection(self, mock_config):
        """Test dynamic provider selection"""
        providers = {
            'openai': OpenAIProvider(mock_config['openai']),
            'anthropic': AnthropicProvider(mock_config['anthropic']),
            'gemini': GeminiProvider(mock_config['gemini'])
        }
        
        assert isinstance(providers['openai'], OpenAIProvider)
        assert isinstance(providers['anthropic'], AnthropicProvider)
        assert isinstance(providers['gemini'], GeminiProvider)

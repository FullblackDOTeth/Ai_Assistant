import pytest
from unittest.mock import Mock, patch
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

@pytest.fixture
def mock_anthropic():
    with patch('anthropic.Anthropic') as mock:
        mock_instance = Mock()
        mock_instance.completions.create.return_value = Mock(completion="Digital helper's light\nGuiding through complex queries\nSilent partner here")
        mock.return_value = mock_instance
        yield mock_instance

@pytest.mark.network
def test_anthropic_live():
    """Live test requiring API key - only runs with network marker"""
    anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    completion = anthropic.completions.create(
        model="claude-2.1",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT} Write a haiku about AI assistants.{AI_PROMPT}"
    )
    assert isinstance(completion.completion, str)
    assert len(completion.completion) > 0

def test_anthropic_mock(mock_anthropic):
    """Test with mocked Anthropic client"""
    completion = mock_anthropic.completions.create(
        model="claude-2.1",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT} Write a haiku about AI assistants.{AI_PROMPT}"
    )
    assert isinstance(completion.completion, str)
    assert len(completion.completion) > 0
    mock_anthropic.completions.create.assert_called_once()

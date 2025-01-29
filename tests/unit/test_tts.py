import pytest
from src.utils.tts_engines import LocalTTS, GoogleTTS, AzureTTS, AmazonTTS, MultiTTS
import os
import tempfile
import pygame
import time

@pytest.fixture
def multi_tts():
    return MultiTTS()

class TestLocalTTS:
    def test_local_tts_init(self):
        """Test local TTS initialization"""
        tts = LocalTTS()
        assert tts.engine is not None
    
    def test_local_tts_speak(self):
        """Test local TTS speak functionality"""
        tts = LocalTTS()
        test_text = "This is a test message"
        tts.speak(test_text)  # Should speak without errors
    
    def test_local_tts_stop(self):
        """Test local TTS stop functionality"""
        tts = LocalTTS()
        tts.stop()  # Should stop without errors

class TestGoogleTTS:
    def test_google_tts_init(self):
        """Test Google TTS initialization"""
        tts = GoogleTTS()
        assert hasattr(tts, 'language')
        assert pygame.mixer.get_init() is not None
    
    def test_google_tts_speak(self):
        """Test Google TTS speak functionality"""
        tts = GoogleTTS()
        test_text = "This is a test message"
        tts.speak(test_text)  # Should speak without errors
        
        # Check if temporary file was cleaned up
        temp_files = os.listdir(tempfile.gettempdir())
        assert not any(f.startswith('gtts_temp') for f in temp_files)
    
    def test_google_tts_stop(self):
        """Test Google TTS stop functionality"""
        tts = GoogleTTS()
        tts.stop()
        assert not pygame.mixer.music.get_busy()

@pytest.mark.skipif(not os.getenv('AZURE_SPEECH_KEY'), reason="Azure credentials not configured")
class TestAzureTTS:
    def test_azure_tts_init(self):
        """Test Azure TTS initialization"""
        tts = AzureTTS()
        assert hasattr(tts, 'speech_synthesizer')
    
    def test_azure_tts_speak(self):
        """Test Azure TTS speak functionality"""
        tts = AzureTTS()
        test_text = "This is a test message"
        tts.speak(test_text)  # Should speak without errors
    
    def test_azure_tts_stop(self):
        """Test Azure TTS stop functionality"""
        tts = AzureTTS()
        tts.stop()  # Should stop without errors

@pytest.mark.skipif(not os.getenv('AWS_ACCESS_KEY_ID'), reason="AWS credentials not configured")
class TestAmazonTTS:
    def test_amazon_tts_init(self):
        """Test Amazon Polly initialization"""
        tts = AmazonTTS()
        assert hasattr(tts, 'polly')
    
    def test_amazon_tts_speak(self):
        """Test Amazon Polly speak functionality"""
        tts = AmazonTTS()
        test_text = "This is a test message"
        tts.speak(test_text)  # Should speak without errors
        
        # Check if temporary file was cleaned up
        temp_files = os.listdir(tempfile.gettempdir())
        assert not any(f.startswith('polly_temp') for f in temp_files)
    
    def test_amazon_tts_stop(self):
        """Test Amazon Polly stop functionality"""
        tts = AmazonTTS()
        tts.stop()
        assert not pygame.mixer.music.get_busy()

class TestMultiTTS:
    def test_multi_tts_init(self, multi_tts):
        """Test MultiTTS initialization"""
        assert 'local' in multi_tts.engines
        assert 'google' in multi_tts.engines
        assert 'azure' in multi_tts.engines
        assert 'amazon' in multi_tts.engines
        assert multi_tts.current_engine == 'local'
    
    def test_engine_switching(self, multi_tts):
        """Test switching between TTS engines"""
        # Test switching to each available engine
        for engine in ['local', 'google', 'azure', 'amazon']:
            assert multi_tts.set_engine(engine)
            assert multi_tts.current_engine == engine
        
        # Test invalid engine
        assert not multi_tts.set_engine('invalid_engine')
    
    def test_speak_queue(self, multi_tts):
        """Test speech queue functionality"""
        test_messages = [
            "First test message",
            "Second test message",
            "Third test message"
        ]
        
        # Queue multiple messages
        for msg in test_messages:
            multi_tts.speak(msg)
        
        # Let some messages process
        time.sleep(2)
        
        # Stop and clear queue
        multi_tts.stop()
        assert not multi_tts.is_speaking
    
    def test_fallback_behavior(self, multi_tts):
        """Test fallback to local TTS when other engines fail"""
        # Force an error with Azure/Amazon by not providing credentials
        multi_tts.set_engine('azure')
        multi_tts.speak("This should fallback to local TTS")
        
        # Verify it falls back to local
        time.sleep(1)  # Wait for fallback
        assert multi_tts.current_engine == 'local'

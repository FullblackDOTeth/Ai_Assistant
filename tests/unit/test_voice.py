import pytest
from unittest.mock import Mock, patch
import os
import tempfile
import wave
import numpy as np

@pytest.fixture
def mock_audio_data():
    """Fixture to create mock audio data for testing"""
    # Create a simple sine wave as test audio data
    duration = 1  # seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    return (audio_data * 32767).astype(np.int16)

@pytest.fixture
def temp_audio_file(mock_audio_data):
    """Fixture to create a temporary WAV file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(mock_audio_data.tobytes())
    yield temp_file.name
    os.unlink(temp_file.name)

class TestVoiceActivation:
    @pytest.mark.voice
    def test_speech_recognition_setup(self):
        """Test speech recognition initialization"""
        with patch('speech_recognition.Recognizer') as mock_recognizer:
            recognizer = mock_recognizer()
            assert recognizer is not None

    @pytest.mark.voice
    def test_microphone_access(self):
        """Test microphone access"""
        with patch('speech_recognition.Microphone') as mock_mic:
            mic = mock_mic()
            assert mic is not None

    @pytest.mark.voice
    def test_audio_recording(self, temp_audio_file):
        """Test audio recording functionality"""
        assert os.path.exists(temp_audio_file)
        with wave.open(temp_audio_file, 'rb') as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == 44100

    @pytest.mark.voice
    def test_speech_to_text(self):
        """Test speech-to-text conversion"""
        with patch('speech_recognition.Recognizer') as mock_recognizer:
            recognizer = mock_recognizer()
            mock_recognizer.recognize_google.return_value = "test speech"
            
            with patch('speech_recognition.AudioFile') as mock_audio_file:
                audio_file = mock_audio_file()
                text = recognizer.recognize_google(audio_file)
                assert text == "test speech"

    @pytest.mark.voice
    def test_text_to_speech(self):
        """Test text-to-speech functionality"""
        with patch('pyttsx3.init') as mock_tts:
            engine = mock_tts()
            test_text = "Hello, this is a test"
            
            engine.say(test_text)
            engine.runAndWait.assert_called_once()

class TestVoiceCommands:
    @pytest.mark.voice
    def test_command_recognition(self):
        """Test voice command recognition"""
        test_commands = {
            "open": lambda x: f"Opening {x}",
            "close": lambda x: f"Closing {x}",
            "search": lambda x: f"Searching for {x}"
        }
        
        test_input = "open browser"
        command, arg = test_input.split(" ", 1)
        assert command in test_commands
        assert test_commands[command](arg) == "Opening browser"

    @pytest.mark.voice
    def test_command_validation(self):
        """Test voice command validation"""
        invalid_command = "invalid_command test"
        command, arg = invalid_command.split(" ", 1)
        with pytest.raises(KeyError):
            test_commands = {}
            assert command in test_commands

    @pytest.mark.voice
    def test_noise_filtering(self, mock_audio_data):
        """Test noise filtering in audio input"""
        # Add noise to the audio data
        noise = np.random.normal(0, 0.1, len(mock_audio_data))
        noisy_audio = mock_audio_data + (noise * 32767).astype(np.int16)
        
        # Basic noise reduction test
        assert np.mean(np.abs(noisy_audio)) > np.mean(np.abs(mock_audio_data))

    @pytest.mark.voice
    def test_continuous_listening(self):
        """Test continuous listening mode"""
        with patch('speech_recognition.Recognizer') as mock_recognizer:
            recognizer = mock_recognizer()
            
            def mock_listen(source):
                return "mock_audio_data"
            
            recognizer.listen = mock_listen
            audio_data = recognizer.listen(Mock())
            assert audio_data is not None

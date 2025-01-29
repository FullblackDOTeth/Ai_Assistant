import pyttsx3
from gtts import gTTS
import azure.cognitiveservices.speech as speechsdk
import boto3
import os
import tempfile
import pygame
from abc import ABC, abstractmethod
import threading
import queue
from dotenv import load_dotenv

load_dotenv()

class TTSEngine(ABC):
    """Abstract base class for TTS engines"""
    @abstractmethod
    def speak(self, text):
        pass

    @abstractmethod
    def stop(self):
        pass

class LocalTTS(TTSEngine):
    """Local TTS using pyttsx3"""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        
        # Try to set a better voice
        voices = self.engine.getProperty('voices')
        if voices:
            female_voice = next((v for v in voices if 'female' in v.name.lower()), None)
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
    
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
    
    def stop(self):
        self.engine.stop()

class GoogleTTS(TTSEngine):
    """Google Text-to-Speech"""
    def __init__(self):
        self.language = 'en'
        pygame.mixer.init()
        self.temp_dir = tempfile.gettempdir()
    
    def speak(self, text):
        try:
            tts = gTTS(text=text, lang=self.language)
            temp_file = os.path.join(self.temp_dir, 'gtts_temp.mp3')
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            os.remove(temp_file)
        except Exception as e:
            print(f"Google TTS error: {str(e)}")
    
    def stop(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

class AzureTTS(TTSEngine):
    """Azure Cognitive Services TTS"""
    def __init__(self):
        self.subscription_key = os.getenv('AZURE_SPEECH_KEY')
        self.region = os.getenv('AZURE_SPEECH_REGION')
        if self.subscription_key and self.region:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key,
                region=self.region
            )
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config
            )
    
    def speak(self, text):
        if not (self.subscription_key and self.region):
            raise ValueError("Azure credentials not configured")
        result = self.speech_synthesizer.speak_text_async(text).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Azure TTS error: {result.reason}")
    
    def stop(self):
        if hasattr(self, 'speech_synthesizer'):
            self.speech_synthesizer.stop_speaking_async()

class AmazonTTS(TTSEngine):
    """Amazon Polly TTS"""
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        if all([self.aws_access_key, self.aws_secret_key]):
            self.polly = boto3.client('polly',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
            pygame.mixer.init()
    
    def speak(self, text):
        if not all([self.aws_access_key, self.aws_secret_key]):
            raise ValueError("AWS credentials not configured")
        
        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Joanna',
                Engine='neural'
            )
            
            if "AudioStream" in response:
                temp_file = os.path.join(tempfile.gettempdir(), 'polly_temp.mp3')
                with open(temp_file, 'wb') as f:
                    f.write(response['AudioStream'].read())
                
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                os.remove(temp_file)
        
        except Exception as e:
            print(f"Amazon Polly error: {str(e)}")
    
    def stop(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

class MultiTTS:
    """Multi-engine TTS manager"""
    def __init__(self):
        self.engines = {
            'local': LocalTTS(),
            'google': GoogleTTS(),
            'azure': AzureTTS(),
            'amazon': AmazonTTS()
        }
        self.current_engine = 'local'
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.speech_thread.start()
    
    def _process_queue(self):
        while True:
            try:
                if not self.is_speaking:
                    text, engine_name = self.speech_queue.get()
                    self.is_speaking = True
                    try:
                        self.engines[engine_name].speak(text)
                    except Exception as e:
                        print(f"TTS error with {engine_name}: {str(e)}")
                        # Fallback to local TTS
                        if engine_name != 'local':
                            try:
                                self.engines['local'].speak(text)
                            except Exception as e2:
                                print(f"Local TTS fallback error: {str(e2)}")
                    finally:
                        self.is_speaking = False
                        self.speech_queue.task_done()
            except Exception as e:
                print(f"Queue processing error: {str(e)}")
    
    def speak(self, text, engine=None):
        """Add text to speech queue"""
        engine = engine or self.current_engine
        self.speech_queue.put((text, engine))
    
    def stop(self):
        """Stop current speech"""
        for engine in self.engines.values():
            engine.stop()
        self.is_speaking = False
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()
    
    def set_engine(self, engine_name):
        """Set the current TTS engine"""
        if engine_name in self.engines:
            self.current_engine = engine_name
            return True
        return False
    
    def get_available_engines(self):
        """Get list of available engines"""
        return list(self.engines.keys())

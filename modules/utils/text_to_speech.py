import pyttsx3
import threading
import queue

class TextToSpeech:
    def __init__(self):
        """Initialize the text-to-speech engine"""
        self.engine = pyttsx3.init()
        self.voice_enabled = True
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self.speech_thread.start()
        
        # Configure the voice
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Get available voices and set a default one
        voices = self.engine.getProperty('voices')
        if voices:
            # Try to find a female voice
            female_voice = next((voice for voice in voices if 'female' in voice.name.lower()), None)
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
    
    def _process_speech_queue(self):
        """Process text in the speech queue"""
        while True:
            try:
                text = self.speech_queue.get()
                if self.voice_enabled:
                    self.engine.say(text)
                    self.engine.runAndWait()
                self.speech_queue.task_done()
            except Exception as e:
                print(f"Error in speech processing: {str(e)}")
    
    def speak(self, text):
        """Add text to the speech queue"""
        if text and self.voice_enabled:
            self.speech_queue.put(text)
    
    def toggle_voice(self):
        """Toggle voice output on/off"""
        self.voice_enabled = not self.voice_enabled
        return self.voice_enabled
    
    def set_rate(self, rate):
        """Set speech rate (words per minute)"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set speech volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def change_voice(self, voice_index):
        """Change the voice by index"""
        voices = self.engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            return True
        return False

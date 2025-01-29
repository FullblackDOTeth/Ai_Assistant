import threading
import customtkinter as ctk
from ai_providers.free_provider import FreeAIProvider
from utils.tts_engines import MultiTTS
from utils.text_to_speech import TextToSpeech
from utils.web_utils import get_web_info, summarize_web_results

class Assistant:
    def __init__(self):
        # Initialize AI provider
        self.ai_provider = FreeAIProvider()
        # Initialize multi-engine TTS
        self.tts = MultiTTS()
        self.voice_enabled = True
    
    def handle_message(self, message):
        """Process message and return researched response"""
        try:
            # Handle voice commands
            if message.startswith('/'):
                return self.handle_command(message)
            
            # Check if it's a web search query
            if message.lower().startswith(('search ', 'find ', 'lookup ', 'what ', 'who ', 'where ', 'when ', 'why ', 'how ')):
                # Get web information
                results = get_web_info(message)
                response = summarize_web_results(results)
                
                # Speak the response if voice is enabled
                if self.voice_enabled:
                    self.tts.speak(response)
                    
                return response
                
            # Handle regular messages
            response = self.ai_provider.generate_response(message)
            if self.voice_enabled:
                self.tts.speak(response)
            return response
            
        except Exception as e:
            error_msg = f"I encountered an error while researching. Details: {str(e)}"
            if self.voice_enabled:
                self.tts.speak(error_msg)
            return error_msg
    
    def handle_command(self, command):
        """Handle voice control commands"""
        parts = command.lower().split()
        if not parts:
            return "Invalid command"
            
        if parts[0] == '/voice':
            if len(parts) < 2:
                return "Invalid voice command"
                
            action = parts[1]
            
            if action == 'toggle':
                self.voice_enabled = not self.voice_enabled
                state = "enabled" if self.voice_enabled else "disabled"
                return f"Voice {state}"
                
            elif action == 'stop':
                self.tts.stop()
                return "Stopped speaking"
                
            elif action == 'rate' and len(parts) == 3:
                try:
                    rate = int(parts[2])
                    if self.tts.current_engine == 'local':
                        self.tts.engines['local'].engine.setProperty('rate', rate)
                        return f"Rate set to {rate}"
                    return "Rate adjustment only available for local TTS engine"
                except ValueError:
                    return "Invalid rate value"
                    
            elif action == 'volume' and len(parts) == 3:
                try:
                    volume = float(parts[2])
                    if self.tts.current_engine == 'local':
                        self.tts.engines['local'].engine.setProperty('volume', volume)
                        return f"Volume set to {volume}"
                    return "Volume adjustment only available for local TTS engine"
                except ValueError:
                    return "Invalid volume value"
                    
            elif action == 'engine' and len(parts) == 3:
                engine = parts[2]
                if self.tts.set_engine(engine):
                    return f"Switched to {engine} TTS engine"
                return f"Invalid engine. Available engines: {', '.join(self.tts.get_available_engines())}"
                
        return "Unknown command"

class AssistantApp:
    def __init__(self):
        # Create window
        self.window = ctk.CTk()
        self.window.title("KT Research")
        self.window.geometry("1000x800")
        
        # Create assistant
        self.assistant = Assistant()
        
        # Create UI
        from ui import ChatUI
        self.ui = ChatUI(self.window, self.handle_message)
        
        # Welcome message
        self.ui.add_message("Ready to help! Just type your question and press Enter.", is_user=False)
    
    def handle_message(self, message):
        """Handle incoming message"""
        return self.assistant.handle_message(message)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    # Configure appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = AssistantApp()
    app.run()

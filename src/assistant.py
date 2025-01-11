import threading
import customtkinter as ctk
from ai_providers.free_provider import FreeAIProvider

class Assistant:
    def __init__(self):
        # Initialize AI provider
        self.ai_provider = FreeAIProvider()
    
    def handle_message(self, message):
        """Process message and return researched response"""
        try:
            return self.ai_provider.generate_response(message)
        except Exception as e:
            return f"I encountered an error while researching. Details: {str(e)}"

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

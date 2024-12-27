import customtkinter as ctk
from ui import ChatUI
import json
import os
from datetime import datetime
import threading
import wikipedia
from duckduckgo_search import DDGS

class Assistant:
    def __init__(self):
        self.conversation_history = []
        self.ddg = DDGS()
        print("AI Assistant initialized successfully!")
    
    def process_message(self, message):
        """Process user message and generate response"""
        try:
            # Try Wikipedia first for fast responses
            try:
                wiki_summary = wikipedia.summary(message, sentences=1)
                return wiki_summary
            except:
                pass
            
            # Try quick web search
            try:
                results = list(self.ddg.text(message, max_results=1))
                if results:
                    return results[0]['body']
            except:
                pass
            
            # Fallback response
            return "I'm not sure about that. Could you try rephrasing your question?"
            
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def save_conversation(self):
        """Save conversation history to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
                
            print(f"Conversation saved to {filename}")
            
        except Exception as e:
            print(f"Error saving conversation: {e}")

class AssistantApp:
    def __init__(self):
        self.assistant = Assistant()
        self.window = ctk.CTk()
        self.window.title("KT - Your AI Assistant")
        self.window.geometry("800x600")
        
        # Configure the UI
        self.ui = ChatUI(self.window, self.handle_message)
        
        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Add welcome message
        welcome_msg = "Hello! 👋 I'm KT, your AI assistant. Ask me anything!"
        self.ui.add_message(welcome_msg, is_user=False)
    
    def handle_message(self, message):
        return self.assistant.process_message(message)
    
    def on_closing(self):
        self.assistant.save_conversation()
        self.window.destroy()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    # Configure appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = AssistantApp()
    app.run()

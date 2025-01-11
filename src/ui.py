"""
AI Assistant UI Implementation
"""

import customtkinter as ctk
from tkinter import ttk
import threading

class ChatUI:
    def __init__(self, window, message_callback):
        self.window = window
        self.message_callback = message_callback
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create chat display
        self.chat_frame = ctk.CTkTextbox(self.main_frame, wrap="word")
        self.chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_frame.configure(state="disabled")
        
        # Create input frame
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        # Create input field
        self.input_field = ctk.CTkEntry(input_frame, placeholder_text="Ask anything...")
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.send_message)
        
        # Create send button
        self.send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right")
        
        # Focus input field
        self.input_field.focus()
    
    def send_message(self, event=None):
        message = self.input_field.get().strip()
        if message:
            # Clear input immediately
            self.input_field.delete(0, "end")
            self.input_field.configure(state="disabled")
            self.send_button.configure(state="disabled")
            
            # Show user message
            self.add_message(message, is_user=True)
            
            # Process in background
            def process():
                try:
                    response = self.message_callback(message)
                    self.window.after(0, self.add_message, response, False)
                finally:
                    # Re-enable input
                    self.window.after(0, self.enable_input)
            
            threading.Thread(target=process, daemon=True).start()
    
    def enable_input(self):
        """Re-enable input after processing"""
        self.input_field.configure(state="normal")
        self.send_button.configure(state="normal")
        self.input_field.focus()
    
    def add_message(self, message, is_user=False):
        """Add message to chat"""
        self.chat_frame.configure(state="normal")
        
        # Add prefix
        prefix = "You: " if is_user else "KT: "
        self.chat_frame.insert("end", prefix)
        
        # Add message
        self.chat_frame.insert("end", message + "\n\n")
        
        # Scroll to bottom
        self.chat_frame.see("end")
        self.chat_frame.configure(state="disabled")

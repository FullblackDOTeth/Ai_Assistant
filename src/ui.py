"""
AI Assistant UI Implementation
"""

import customtkinter as ctk
from datetime import datetime
import json
from pathlib import Path

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, message, is_user=False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Create bubble frame
        bubble = ctk.CTkFrame(
            self,
            fg_color="#2B5278" if is_user else "#383838",
            corner_radius=20
        )
        bubble.pack(
            side="right" if is_user else "left",
            padx=10,
            pady=5
        )
        
        # Add message
        message_label = ctk.CTkLabel(
            bubble,
            text=message,
            wraplength=400,
            justify="left"
        )
        message_label.pack(padx=15, pady=10)

class ChatUI:
    def __init__(self, window, message_callback):
        self.window = window
        self.message_callback = message_callback
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(window, fg_color="#1A1A1A")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create chat frame
        self.chat_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#1A1A1A",
            corner_radius=0
        )
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create input frame with rounded corners
        self.input_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#2D2D2D",
            corner_radius=20,
            border_width=2,
            border_color="#3F3F3F"
        )
        self.input_frame.pack(fill="x", pady=5)
        
        # Create input field
        self.input_field = ctk.CTkTextbox(
            self.input_frame,
            height=60,
            fg_color="#1E1E1E",
            corner_radius=15,
            border_width=0,
            text_color="white",
            font=("Arial", 12)
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=10)
        self.input_field.bind("<Return>", self.handle_return)
        
        # Add placeholder text
        self.input_field.insert("1.0", "Ask me anything...")
        self.input_field.bind("<FocusIn>", self._clear_placeholder)
        self.input_field.bind("<FocusOut>", self._add_placeholder)
        self.input_field.configure(text_color="gray60")
        
        # Create send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Ask",
            width=100,
            corner_radius=20,
            command=self.send_message,
            fg_color="#2B5278",
            hover_color="#1B3B5E"
        )
        self.send_button.pack(side="right", padx=10, pady=10)
    
    def handle_return(self, event):
        """Handle return key press in input field"""
        if not event.state & 0x1:  # Shift key not pressed
            self.send_message()
            return "break"
    
    def send_message(self):
        """Send message from input field"""
        message = self.input_field.get("1.0", "end-1c").strip()
        if message and message != "Ask me anything...":
            self.add_message(message, is_user=True)
            self.input_field.delete("1.0", "end")
            self.input_field.insert("1.0", "Ask me anything...")
            self.input_field.configure(text_color="gray60")
            response = self.message_callback(message)
            if response:
                self.add_message(response, is_user=False)
    
    def add_message(self, message, is_user=False):
        """Add a message bubble to the chat"""
        bubble = ChatBubble(self.chat_frame, message, is_user=is_user)
        bubble.pack(fill="x", padx=10, pady=5)
        self.chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _clear_placeholder(self, event):
        """Clear placeholder text when input field gains focus"""
        if self.input_field.get("1.0", "end-1c").strip() == "Ask me anything...":
            self.input_field.delete("1.0", "end")
            self.input_field.configure(text_color="white")
    
    def _add_placeholder(self, event):
        """Add placeholder text when input field loses focus"""
        if not self.input_field.get("1.0", "end-1c").strip():
            self.input_field.delete("1.0", "end")
            self.input_field.insert("1.0", "Ask me anything...")
            self.input_field.configure(text_color="gray60")

"""
UI Preview Generator
Created: 2024-12-14T19:55:20-05:00
Updated: 2024-12-14T20:00:42-05:00
"""

import customtkinter as ctk
from PIL import Image, ImageGrab
import os
from datetime import datetime

def create_preview():
    # Configure appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create window for preview
    window = ctk.CTk()
    window.title("Chat Preview")
    window.geometry("800x600")
    
    # Create main frame
    main_frame = ctk.CTkFrame(window, fg_color="#1A1A1A")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Sample messages
    messages = [
        {"sender": "You", "message": "Hello! Can you help me with a coding question?", "is_user": True},
        {"sender": "Assistant", "message": "Of course! I'd be happy to help. What's your question?", "is_user": False},
        {"sender": "You", "message": "How do I create a beautiful UI in Python?", "is_user": True},
        {"sender": "Assistant", "message": "There are several great options for creating beautiful UIs in Python. One popular choice is customtkinter, which we're using right now! It provides modern-looking widgets and supports themes.", "is_user": False}
    ]
    
    # Create chat bubbles
    for msg in messages:
        # Create bubble frame
        bubble_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bubble_frame.pack(fill="x", padx=10, pady=5)
        
        # Create bubble
        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color="#2B5278" if msg["is_user"] else "#383838",
            corner_radius=20
        )
        bubble.pack(
            side="right" if msg["is_user"] else "left",
            padx=10,
            pady=5
        )
        
        # Add timestamp
        time_label = ctk.CTkLabel(
            bubble,
            text=datetime.now().strftime("%H:%M:%S"),
            text_color="gray70",
            font=("Arial", 8)
        )
        time_label.pack(padx=10, pady=(5, 0))
        
        # Add sender
        sender_label = ctk.CTkLabel(
            bubble,
            text=msg["sender"],
            text_color="gray80",
            font=("Arial", 10, "bold")
        )
        sender_label.pack(padx=10, pady=(0, 5))
        
        # Add message
        message_label = ctk.CTkLabel(
            bubble,
            text=msg["message"],
            text_color="white",
            font=("Arial", 12),
            wraplength=400,
            justify="left"
        )
        message_label.pack(padx=15, pady=(0, 10))
    
    # Create input area with border
    input_frame = ctk.CTkFrame(
        window,
        fg_color="#2D2D2D",
        corner_radius=20,
        border_width=2,
        border_color="#3F3F3F"
    )
    input_frame.pack(fill="x", padx=20, pady=10)
    
    # Add input field with visible background
    input_field = ctk.CTkTextbox(
        input_frame,
        height=60,
        fg_color="#1E1E1E",
        corner_radius=15,
        border_width=0,
        text_color="gray60",
        font=("Arial", 12)
    )
    input_field.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=10)
    input_field.insert("1.0", "Type your message here...")
    
    # Add send button
    send_button = ctk.CTkButton(
        input_frame,
        text="Send",
        width=100,
        corner_radius=20,
        fg_color="#2B5278",
        hover_color="#1B3B5E"
    )
    send_button.pack(side="right", padx=10, pady=10)
    
    # Add voice button
    voice_button = ctk.CTkButton(
        window,
        text="🎤 Voice Input",
        width=150,
        corner_radius=20,
        fg_color="#2B5278",
        hover_color="#1B3B5E"
    )
    voice_button.pack(pady=10)
    
    # Center the window
    window.update()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - 800) // 2
    y = (screen_height - 600) // 2
    window.geometry(f"800x600+{x}+{y}")
    
    # Run the window
    window.mainloop()

if __name__ == "__main__":
    create_preview()

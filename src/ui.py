"""
AI Assistant UI Implementation
"""

import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from thought_unloader import ThoughtUnloaderUI
from ai_providers.claude_provider import ClaudeProvider
from assistant import Assistant

class Button3D(ctk.CTkButton):
    """Enhanced 3D button with smooth animations"""
    def __init__(self, *args, **kwargs):
        self.hover_color = kwargs.pop('hover_color', None)
        self.border_color = kwargs.pop('border_color', None)
        self.original_fg = kwargs.get('fg_color', None)
        
        # Enhanced shadow and lighting effects
        self.shadow_color = self._adjust_color(self.original_fg, -30) if self.original_fg else None
        self.highlight_color = self._adjust_color(self.original_fg, 30) if self.original_fg else None
        
        super().__init__(*args, **kwargs)
        
        # Bind mouse events for smooth animations
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        # Animation state
        self._hover = False
        self._pressed = False
        self._animation_id = None
        
    def _adjust_color(self, color, amount):
        """Adjust color brightness"""
        if not color or color.startswith('var') or color == 'transparent':
            return color
            
        try:
            # Convert hex to RGB
            color = color.lstrip('#')
            r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)
            
            # Adjust and clamp values
            r = max(0, min(255, r + amount))
            g = max(0, min(255, g + amount))
            b = max(0, min(255, b + amount))
            
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return color
    
    def _animate(self, target_state, duration=150):
        """Smooth animation between states"""
        if self._animation_id:
            self.after_cancel(self._animation_id)
            
        start_time = datetime.now().timestamp() * 1000
        start_height = self.winfo_height()
        
        def update():
            current_time = datetime.now().timestamp() * 1000
            progress = min(1.0, (current_time - start_time) / duration)
            
            # Smooth easing function
            t = progress
            ease = 1 - (1 - t) * (1 - t)  # Quadratic ease-out
            
            # Calculate current state
            if target_state == 'hover':
                self.configure(fg_color=self.hover_color if progress > 0.5 else self.original_fg)
                scale = 1.02 - (0.02 * (1 - ease))
            elif target_state == 'press':
                scale = 0.98 + (0.02 * ease)
            else:  # normal
                self.configure(fg_color=self.original_fg if progress > 0.5 else self.hover_color)
                scale = 1.0
            
            # Apply transformation
            current_height = int(start_height * scale)
            self.configure(height=current_height)
            
            # Continue animation if not complete
            if progress < 1.0:
                self._animation_id = self.after(16, update)
            else:
                self._animation_id = None
        
        update()
    
    def _on_enter(self, event):
        self._hover = True
        if not self._pressed:
            self._animate('hover')
    
    def _on_leave(self, event):
        self._hover = False
        if not self._pressed:
            self._animate('normal')
    
    def _on_press(self, event):
        self._pressed = True
        self._animate('press')
    
    def _on_release(self, event):
        self._pressed = False
        if self._hover:
            self._animate('hover')
        else:
            self._animate('normal')

class CollapsibleFrame(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        self.is_expanded = False
        
        # Header frame (always visible)
        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", padx=2, pady=2)
        
        # Title label that triggers expand/collapse
        self.title_label = ctk.CTkLabel(
            self.header,
            text=f"▸ {title}",  # Right-pointing triangle when collapsed
            anchor="w",
            cursor="hand2"  # Hand cursor on hover
        )
        self.title_label.pack(side="left", padx=5)
        
        # Content frame (hidden by default)
        self.content = ctk.CTkFrame(self)
        
        # Bind hover events
        self.title_label.bind("<Enter>", self.expand)
        self.bind("<Leave>", self.collapse)
    
    def expand(self, event=None):
        if not self.is_expanded:
            self.is_expanded = True
            self.title_label.configure(text=f"▾ {self.title}")  # Down-pointing triangle
            self.content.pack(fill="x", padx=2, pady=(0, 2))
    
    def collapse(self, event=None):
        # Check if mouse is still over content
        mouse_x = self.winfo_pointerx() - self.winfo_rootx()
        mouse_y = self.winfo_pointery() - self.winfo_rooty()
        if not (0 <= mouse_x <= self.winfo_width() and 0 <= mouse_y <= self.winfo_height()):
            self.is_expanded = False
            self.title_label.configure(text=f"▸ {self.title}")
            self.content.pack_forget()

class ChatUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Head AI")
        self.window.geometry("1200x800")
        
        # Initialize AI provider
        self.ai_provider = ClaudeProvider()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create frames
        self.create_frames()
        
        # Create UI elements
        self.create_input_area()
        self.create_display_area()
        self.create_assistant()
        
        # Configure tags for message display
        self.configure_tags()
    
    def create_frames(self):
        """Create the main UI frames"""
        # Left frame for chat
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0,5))
        
        # Right frame for assistant
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="y", padx=(5,0))
    
    def create_input_area(self):
        """Create the input area at the bottom"""
        # Frame for input area
        self.input_frame = ctk.CTkFrame(self.left_frame)
        self.input_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # Add buttons above text input
        self.button_frame = ctk.CTkFrame(self.input_frame)
        self.button_frame.pack(fill="x", padx=5, pady=(5,0))
        
        # Thought unloader button
        self.unload_btn = ctk.CTkButton(
            self.input_frame,
            text="💭 Unload Thoughts",
            command=self.open_thought_unloader,
            width=120,
            font=("Metropolis", 13),
            fg_color="#1f6aa5",
            hover_color="#1857a4"
        )
        self.unload_btn.pack(side="left", padx=5)
        
        # Text input
        self.input_text = ctk.CTkTextbox(
            self.input_frame,
            height=100,
            font=("Metropolis", 13),
            wrap="word"
        )
        self.input_text.pack(fill="x", padx=5, pady=5)
        
        # Send button
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Send Message",
            command=self.send_message,
            width=120,
            font=("Metropolis", 13),
            fg_color="#2ea043",
            hover_color="#2c974b"
        )
        self.send_btn.pack(side="right", padx=5, pady=(0,5))
    
    def create_display_area(self):
        """Create the message display area"""
        # Frame for message display
        self.display_frame = ctk.CTkFrame(self.left_frame)
        self.display_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Text display for messages
        self.text_display = ctk.CTkTextbox(
            self.display_frame,
            wrap="word",
            font=("Metropolis", 13)
        )
        self.text_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Make text display read-only
        self.text_display.configure(state="disabled")
    
    def create_assistant(self):
        """Create the assistant display"""
        # Initialize assistant
        self.assistant = Assistant(self.right_frame)
    
    def send_message(self):
        """Send a message and get response"""
        # Get message text
        message = self.input_text.get("1.0", "end-1c")
        if not message.strip():
            return
        
        # Clear input
        self.input_text.delete("1.0", "end")
        
        # Display user message
        self.display_message("You", message, "user")
        
        # Get AI response
        response = self.ai_provider.generate_response(message)
        
        # Display AI response
        self.display_message("Assistant", response, "assistant")
    
    def display_message(self, sender, message, tag):
        """Display a message in the chat"""
        # Enable editing
        self.text_display.configure(state="normal")
        
        # Add line break if not first message
        if self.text_display.get("1.0", "end-1c"):
            self.text_display.insert("end", "\n\n")
        
        # Add message
        self.text_display.insert("end", f"{sender}: ", tag)
        self.text_display.insert("end", message)
        
        # Scroll to bottom
        self.text_display.see("end")
        
        # Disable editing
        self.text_display.configure(state="disabled")
    
    def configure_tags(self):
        """Configure text tags for message display"""
        if hasattr(self, 'text_display'):
            self.text_display.tag_config("user", foreground="#1f6aa5")  # Blue for user
            self.text_display.tag_config("assistant", foreground="#2ea043")  # Green for assistant
    
    def open_thought_unloader(self):
        """Open the thought unloader window"""
        ThoughtUnloaderUI(self.window, self.ai_provider)

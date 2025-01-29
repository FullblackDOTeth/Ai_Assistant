import customtkinter as ctk
from utils.thought_processor import ThoughtProcessor

class ThoughtUnloaderUI:
    def __init__(self, parent_window, ai_provider):
        # Create main window
        self.window = ctk.CTkToplevel(parent_window)
        self.window.title("💭 Thought Unloader")
        self.window.attributes('-topmost', True)  # Make window stay on top
        
        # Set up the window
        window_width = 800
        window_height = 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Initialize thought processor
        self.thought_processor = ThoughtProcessor(ai_provider)
        
        # Create frames
        self.create_frames()
        
        # Create UI elements
        self.create_input_area()
        self.create_output_areas()
        
        # Lift window to top
        self.window.lift()
        self.window.focus_force()
    
    def create_frames(self):
        """Create the main frames for the UI"""
        # Input frame (top)
        self.input_frame = ctk.CTkFrame(self.window)
        self.input_frame.pack(fill="x", padx=10, pady=5)
        
        # Output frame (bottom)
        self.output_frame = ctk.CTkFrame(self.window)
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_input_area(self):
        """Create the input area for thoughts"""
        # Label
        input_label = ctk.CTkLabel(
            self.input_frame,
            text="Unload your thoughts here:",
            font=("Metropolis", 13)
        )
        input_label.pack(anchor="w", padx=5, pady=(5,0))
        
        # Text input
        self.input_text = ctk.CTkTextbox(
            self.input_frame,
            height=150,
            font=("Metropolis", 13),
            wrap="word"
        )
        self.input_text.pack(fill="x", padx=5, pady=5)
        
        # Process button
        self.process_btn = ctk.CTkButton(
            self.input_frame,
            text="Process Thoughts",
            command=self.process_thoughts,
            font=("Metropolis", 13),
            fg_color="#2ea043",
            hover_color="#2c974b"
        )
        self.process_btn.pack(pady=5)
    
    def create_output_areas(self):
        """Create the three output areas"""
        # Create frames for each output
        self.structured_frame = ctk.CTkFrame(self.output_frame)
        self.structured_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.powerful_frame = ctk.CTkFrame(self.output_frame)
        self.powerful_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.template_frame = ctk.CTkFrame(self.output_frame)
        self.template_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add labels and text areas
        self._create_output_section(self.structured_frame, "Structured Content", "structured")
        self._create_output_section(self.powerful_frame, "Powerful, Direct Content", "powerful")
        self._create_output_section(self.template_frame, "Kind but Strong Perspective", "template")
    
    def _create_output_section(self, parent, title, name):
        """Helper to create a labeled output section"""
        label = ctk.CTkLabel(
            parent,
            text=title,
            font=("Metropolis", 13, "bold")
        )
        label.pack(anchor="w", padx=5, pady=(5,0))
        
        text_area = ctk.CTkTextbox(
            parent,
            height=100,
            font=("Metropolis", 13),
            wrap="word"
        )
        text_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store reference to text area
        setattr(self, f"{name}_text", text_area)
    
    def process_thoughts(self):
        """Process the input thoughts"""
        # Get input text
        thoughts = self.input_text.get("1.0", "end-1c")
        
        if thoughts.strip():
            # Disable button while processing
            self.process_btn.configure(state="disabled", text="Processing...")
            
            # Process thoughts
            results = self.thought_processor.process_thoughts(thoughts)
            
            # Update output areas
            self.structured_text.delete("1.0", "end")
            self.structured_text.insert("1.0", results["structured"])
            
            self.powerful_text.delete("1.0", "end")
            self.powerful_text.insert("1.0", results["powerful"])
            
            self.template_text.delete("1.0", "end")
            self.template_text.insert("1.0", results["template"])
            
            # Re-enable button
            self.process_btn.configure(state="normal", text="Process Thoughts")

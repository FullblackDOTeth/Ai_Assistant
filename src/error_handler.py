import customtkinter as ctk
from typing import Optional, Dict, List
from datetime import datetime

class ErrorLog:
    def __init__(self, error_type: str, error_msg: str, solution: str, timestamp: str):
        self.error_type = error_type
        self.error_msg = error_msg
        self.solution = solution
        self.timestamp = timestamp

class ErrorWindow:
    def __init__(self):
        # Create main window
        self.window = ctk.CTkToplevel()
        self.window.title("Error Log")
        self.window.geometry("1000x600")
        self.window.attributes('-topmost', True)
        
        # Create main container with scrollable frame
        self.container = ctk.CTkScrollableFrame(self.window)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # List to store error logs
        self.error_logs: List[ErrorLog] = []
        
        # Button frame at bottom
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Clear and Close buttons
        ctk.CTkButton(
            button_frame,
            text="Clear All",
            command=self.clear_errors,
            font=("Arial Bold", 12),
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.window.destroy,
            font=("Arial Bold", 12),
            width=100
        ).pack(side="right", padx=5)

    def add_error(self, error_log: ErrorLog):
        """Add a new error to the window"""
        self.error_logs.append(error_log)
        self.refresh_display()

    def clear_errors(self):
        """Clear all errors from the window"""
        self.error_logs.clear()
        self.refresh_display()

    def refresh_display(self):
        """Refresh the error display"""
        # Clear existing widgets
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Add each error log
        for log in self.error_logs:
            # Error frame
            error_frame = ctk.CTkFrame(self.container)
            error_frame.pack(fill="x", padx=5, pady=5)
            
            # Header with timestamp and type
            header_frame = ctk.CTkFrame(error_frame)
            header_frame.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(
                header_frame,
                text=f"[{log.timestamp}] {log.error_type}",
                font=("Arial Bold", 12),
                text_color="white"
            ).pack(side="left", padx=5)
            
            # Error section
            error_section = ctk.CTkFrame(error_frame)
            error_section.pack(fill="x", padx=5, pady=2)
            error_section.configure(fg_color="#8B0000")  # Dark red
            
            error_text = ctk.CTkTextbox(
                error_section,
                height=60,
                font=("Arial", 12),
                text_color="white",
                fg_color="#8B0000"
            )
            error_text.pack(fill="x", padx=5, pady=5)
            error_text.insert("1.0", log.error_msg)
            error_text.configure(state="disabled")
            
            # Solution section
            solution_section = ctk.CTkFrame(error_frame)
            solution_section.pack(fill="x", padx=5, pady=2)
            solution_section.configure(fg_color="#006400")  # Dark green
            
            solution_text = ctk.CTkTextbox(
                solution_section,
                height=80,
                font=("Arial", 12),
                text_color="white",
                fg_color="#006400"
            )
            solution_text.pack(fill="x", padx=5, pady=5)
            solution_text.insert("1.0", log.solution)
            solution_text.configure(state="disabled")

class ErrorHandler:
    # Single instance of error window
    _window: Optional[ErrorWindow] = None
    
    # Dictionary of known errors and their solutions
    ERROR_SOLUTIONS: Dict[str, str] = {
        "OPENAI_API_KEY": """
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key
4. Add it to your .env file as: OPENAI_API_KEY=your_key_here
5. Restart the application
        """,
        "GOOGLE_API_KEY": """
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key
4. Add it to your .env file as: GOOGLE_API_KEY=your_key_here
5. Restart the application
        """,
        "ANTHROPIC_API_KEY": """
1. Go to https://console.anthropic.com/
2. Create a new API key
3. Copy the key
4. Add it to your .env file as: ANTHROPIC_API_KEY=your_key_here
5. Restart the application
        """,
        "DEFAULT": """
1. Check your internet connection
2. Verify that all required packages are installed
3. Check the error message for specific details
4. If the problem persists, try restarting the application
        """
    }
    
    @classmethod
    def show_error(cls, error_type: str, error_msg: str, solution: Optional[str] = None):
        """Show error window with message and solution"""
        # Get solution text
        if solution is None:
            solution = cls.ERROR_SOLUTIONS.get(
                error_type,
                cls.ERROR_SOLUTIONS["DEFAULT"]
            )
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create error log
        error_log = ErrorLog(error_type, error_msg, solution, timestamp)
        
        # Create or get window
        if cls._window is None or not cls._window.window.winfo_exists():
            cls._window = ErrorWindow()
        
        # Add error to window
        cls._window.add_error(error_log)

def test_error_handler():
    """Test function to demonstrate error handler"""
    root = ctk.CTk()
    root.geometry("200x200")
    
    def show_api_error():
        ErrorHandler.show_error(
            "OPENAI_API_KEY",
            "Failed to initialize OpenAI API: Invalid API key provided"
        )
    
    def show_custom_error():
        ErrorHandler.show_error(
            "CUSTOM",
            "Custom error message",
            "Here's how to fix this custom error:\n1. Step one\n2. Step two"
        )
    
    def show_multiple_errors():
        show_api_error()
        show_custom_error()
        ErrorHandler.show_error(
            "GOOGLE_API_KEY",
            "Failed to initialize Gemini API",
        )
    
    ctk.CTkButton(
        root,
        text="Show API Error",
        command=show_api_error
    ).pack(pady=10)
    
    ctk.CTkButton(
        root,
        text="Show Custom Error",
        command=show_custom_error
    ).pack(pady=10)
    
    ctk.CTkButton(
        root,
        text="Show Multiple Errors",
        command=show_multiple_errors
    ).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_error_handler()

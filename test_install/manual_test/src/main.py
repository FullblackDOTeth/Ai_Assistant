import customtkinter as ctk
from ui import ChatUI
from assistant import Assistant

def main():
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create window
    window = ctk.CTk()
    window.title("KT - AI Assistant")
    window.geometry("800x600")
    
    # Create assistant
    assistant = Assistant()
    
    # Create UI
    ui = ChatUI(window, assistant.handle_message)
    
    # Start main loop
    window.mainloop()

if __name__ == "__main__":
    main()

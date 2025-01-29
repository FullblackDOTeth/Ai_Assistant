import pytest
import customtkinter as ctk
from unittest.mock import Mock, patch
from src.ui import ChatUI
import threading
import queue

@pytest.fixture
def mock_window():
    """Fixture for mock CTk window"""
    with patch('customtkinter.CTk') as mock_ctk:
        window = mock_ctk()
        yield window

@pytest.fixture
def mock_callback():
    """Fixture for message callback"""
    return Mock()

@pytest.fixture
def chat_ui(mock_window, mock_callback):
    """Fixture for ChatUI instance"""
    return ChatUI(mock_window, mock_callback)

class TestChatUI:
    def test_initialization(self, chat_ui, mock_window):
        """Test UI initialization"""
        assert chat_ui.window == mock_window
        assert isinstance(chat_ui.main_frame, ctk.CTkFrame)
        assert isinstance(chat_ui.chat_frame, ctk.CTkTextbox)
        assert isinstance(chat_ui.input_field, ctk.CTkEntry)

    def test_send_message(self, chat_ui, mock_callback):
        """Test message sending functionality"""
        test_message = "Hello, AI!"
        chat_ui.input_field.get = Mock(return_value=test_message)
        chat_ui.input_field.delete = Mock()
        
        # Simulate pressing enter
        chat_ui.send_message(None)  # None simulates the event object
        
        # Verify callback was called with the message
        mock_callback.assert_called_once_with(test_message)
        # Verify input field was cleared
        chat_ui.input_field.delete.assert_called()

    def test_display_message(self, chat_ui):
        """Test message display functionality"""
        test_message = "Test message"
        chat_ui.display_message(test_message, "user")
        
        # Get displayed text
        chat_ui.chat_frame.configure(state="normal")
        displayed_text = chat_ui.chat_frame.get("1.0", "end-1c")
        chat_ui.chat_frame.configure(state="disabled")
        
        assert test_message in displayed_text
        assert "User:" in displayed_text

    def test_clear_chat(self, chat_ui):
        """Test chat clearing functionality"""
        # First add some text
        chat_ui.display_message("Test message", "user")
        
        # Clear the chat
        chat_ui.clear_chat()
        
        # Verify chat is empty
        chat_ui.chat_frame.configure(state="normal")
        displayed_text = chat_ui.chat_frame.get("1.0", "end-1c")
        chat_ui.chat_frame.configure(state="disabled")
        
        assert displayed_text.strip() == ""

    def test_input_validation(self, chat_ui, mock_callback):
        """Test input validation"""
        # Test empty message
        chat_ui.input_field.get = Mock(return_value="")
        chat_ui.send_message(None)
        mock_callback.assert_not_called()
        
        # Test whitespace-only message
        chat_ui.input_field.get = Mock(return_value="   ")
        chat_ui.send_message(None)
        mock_callback.assert_not_called()

    def test_ui_state_management(self, chat_ui):
        """Test UI state management during processing"""
        # Test disabling input during processing
        chat_ui.set_input_state("disabled")
        assert chat_ui.input_field.cget("state") == "disabled"
        
        # Test re-enabling input after processing
        chat_ui.set_input_state("normal")
        assert chat_ui.input_field.cget("state") == "normal"

    @pytest.mark.asyncio
    async def test_async_message_processing(self, chat_ui):
        """Test asynchronous message processing"""
        message_queue = queue.Queue()
        
        def process_messages():
            while True:
                try:
                    message = message_queue.get_nowait()
                    chat_ui.display_message(message, "assistant")
                    message_queue.task_done()
                except queue.Empty:
                    break
        
        # Simulate receiving messages asynchronously
        message_queue.put("Async response 1")
        message_queue.put("Async response 2")
        
        # Process messages in a separate thread
        thread = threading.Thread(target=process_messages)
        thread.start()
        thread.join()

    def test_error_handling(self, chat_ui):
        """Test error handling in UI"""
        # Test handling of invalid message type
        with pytest.raises(ValueError):
            chat_ui.display_message("Test", "invalid_type")
        
        # Test handling of None message
        chat_ui.display_message(None, "user")  # Should not raise exception
        
        # Test handling of very long messages
        long_message = "x" * 10000
        chat_ui.display_message(long_message, "user")  # Should handle without crashing

    def test_theme_management(self, chat_ui):
        """Test UI theme management"""
        # Test dark theme
        chat_ui.set_theme("dark")
        assert ctk.get_appearance_mode() == "dark"
        
        # Test light theme
        chat_ui.set_theme("light")
        assert ctk.get_appearance_mode() == "light"

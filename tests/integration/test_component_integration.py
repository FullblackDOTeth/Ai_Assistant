import pytest
from unittest.mock import Mock, patch
import threading
import queue
from src.ui import ChatUI
from src.ai_providers import AIProvider
from src.research_methods import ResearchMethods
from src.security.auth_manager import AuthManager

@pytest.fixture
def mock_config():
    """Fixture for test configuration"""
    return {
        'ai_provider': {
            'type': 'openai',
            'api_key': 'test_key',
            'model': 'gpt-4'
        },
        'security': {
            'jwt_secret': 'test_secret',
            'jwt_expiry_hours': 24
        }
    }

@pytest.fixture
def message_queue():
    """Fixture for message queue"""
    return queue.Queue()

class TestComponentIntegration:
    @pytest.mark.integration
    def test_ui_to_ai_integration(self, mock_config, message_queue):
        """Test integration between UI and AI Provider"""
        with patch('customtkinter.CTk') as mock_ctk:
            # Setup components
            window = mock_ctk()
            ai_provider = AIProvider(mock_config['ai_provider'])
            
            def message_callback(msg):
                message_queue.put(msg)
                return "AI Response"
            
            chat_ui = ChatUI(window, message_callback)
            
            # Test message flow
            test_message = "Hello AI!"
            chat_ui.input_field.get = Mock(return_value=test_message)
            chat_ui.send_message()
            
            # Verify message flow
            assert message_queue.get() == test_message
            assert chat_ui.chat_frame.get("1.0", "end-1c").strip().endswith("AI Response")

    @pytest.mark.integration
    def test_ai_to_research_integration(self, mock_config):
        """Test integration between AI Provider and Research Methods"""
        ai_provider = AIProvider(mock_config['ai_provider'])
        research = ResearchMethods()
        
        # Test research query flow
        query = "Latest AI developments"
        with patch('duckduckgo_search.ddg') as mock_search:
            mock_search.return_value = [{"title": "Test", "link": "http://test.com"}]
            
            # AI generates research query
            search_results = research.web_search(query)
            
            # AI processes research results
            response = ai_provider.generate_text(str(search_results))
            
            assert isinstance(response, str)
            assert len(response) > 0

    @pytest.mark.integration
    def test_security_integration(self, mock_config):
        """Test security integration across components"""
        auth_manager = AuthManager(mock_config['security'])
        
        # Create test user
        user = auth_manager.create_user(
            username="testuser",
            password="TestPass123!",
            email="test@example.com"
        )
        
        # Test authenticated AI request
        with patch('customtkinter.CTk') as mock_ctk:
            window = mock_ctk()
            ai_provider = AIProvider(mock_config['ai_provider'])
            
            def secure_callback(msg):
                # Verify user authentication before processing
                if auth_manager.verify_token(user['token']):
                    return ai_provider.generate_text(msg)
                return "Unauthorized"
            
            chat_ui = ChatUI(window, secure_callback)
            
            # Test authorized request
            test_message = "Authorized request"
            chat_ui.input_field.get = Mock(return_value=test_message)
            chat_ui.send_message()
            
            # Verify message was processed
            assert chat_ui.chat_frame.get("1.0", "end-1c").strip() != "Unauthorized"

    @pytest.mark.integration
    def test_error_handling_integration(self, mock_config):
        """Test error handling across components"""
        with patch('customtkinter.CTk') as mock_ctk:
            window = mock_ctk()
            ai_provider = AIProvider(mock_config['ai_provider'])
            
            def error_callback(msg):
                raise Exception("Test error")
            
            chat_ui = ChatUI(window, error_callback)
            
            # Test error handling
            test_message = "Trigger error"
            chat_ui.input_field.get = Mock(return_value=test_message)
            chat_ui.send_message()
            
            # Verify error was handled gracefully
            assert "Error" in chat_ui.chat_frame.get("1.0", "end-1c")

    @pytest.mark.integration
    def test_async_integration(self, mock_config, message_queue):
        """Test asynchronous integration between components"""
        with patch('customtkinter.CTk') as mock_ctk:
            window = mock_ctk()
            ai_provider = AIProvider(mock_config['ai_provider'])
            
            def async_callback(msg):
                # Simulate async processing
                message_queue.put(msg)
                return "Async response"
            
            chat_ui = ChatUI(window, async_callback)
            
            # Test async message flow
            test_messages = ["Message 1", "Message 2", "Message 3"]
            for msg in test_messages:
                chat_ui.input_field.get = Mock(return_value=msg)
                chat_ui.send_message()
            
            # Verify all messages were processed
            received_messages = []
            while not message_queue.empty():
                received_messages.append(message_queue.get())
            
            assert received_messages == test_messages

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class ClaudeProvider:
    """Uses Claude's free web interface for AI responses with learning capabilities"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.conversation_history = []
        self.learning_context = {}
        
    def _init_browser(self):
        """Initialize browser for web interaction"""
        if not self.driver:
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
    
    def _ensure_logged_in(self):
        """Check if logged in to Claude.ai and prompt if not"""
        if not self.is_logged_in:
            self.driver.get('https://claude.ai')
            time.sleep(2)
            
            try:
                self.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
                self.is_logged_in = True
            except:
                print("\nPlease log in to Claude in the browser window.")
                print("1. Sign in with your account")
                print("2. Once you see the chat interface, the program will continue")
                
                while not self.is_logged_in:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Message']")
                        self.is_logged_in = True
                        print("\nSuccessfully logged in!")
                    except:
                        time.sleep(2)
    
    def add_learning_context(self, key, value):
        """Add context for Claude to learn from"""
        self.learning_context[key] = value
    
    def get_learning_context(self, key):
        """Get learned context"""
        return self.learning_context.get(key, None)
    
    def generate_response(self, prompt, maintain_context=True):
        """Generate a response using Claude's web interface with learning context"""
        try:
            self._init_browser()
            self._ensure_logged_in()
            
            # Add learning context to prompt
            if maintain_context and self.learning_context:
                context_str = "\n\nPrevious context:\n"
                for key, value in self.learning_context.items():
                    context_str += f"- {key}: {value}\n"
                prompt = context_str + "\n" + prompt
            
            # Add conversation history if maintaining context
            if maintain_context and self.conversation_history:
                history_str = "\n\nOur previous conversation:\n"
                for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                    history_str += f"- {entry}\n"
                prompt = history_str + "\n" + prompt
            
            try:
                new_chat = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'New chat')]"))
                )
                new_chat.click()
                time.sleep(1)
            except:
                pass
            
            prompt_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))
            )
            prompt_input.clear()
            prompt_input.send_keys(prompt)
            prompt_input.send_keys(Keys.RETURN)
            
            time.sleep(2)
            last_response = ""
            
            while True:
                try:
                    responses = self.driver.find_elements(By.CSS_SELECTOR, ".markdown.prose.w-full")
                    if responses:
                        current_response = responses[-1].text
                        if current_response == last_response:
                            break
                        last_response = current_response
                    time.sleep(1)
                except:
                    break
            
            # Store in conversation history
            if maintain_context:
                self.conversation_history.append(f"User: {prompt}")
                self.conversation_history.append(f"Claude: {last_response}")
            
            return last_response if last_response else "No response received"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_context(self):
        """Clear all learning context and history"""
        self.conversation_history = []
        self.learning_context = {}
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False

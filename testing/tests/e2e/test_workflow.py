#!/usr/bin/env python3

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

class TestUserWorkflow:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize webdriver
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        
        yield
        
        # Cleanup
        self.driver.quit()

    def test_user_registration_login(self):
        """Test user registration and login flow."""
        try:
            # Step 1: Navigate to registration page
            self.logger.info("Navigating to registration page")
            self.driver.get("http://localhost:3000/register")
            
            # Step 2: Fill registration form
            self.logger.info("Filling registration form")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_input.send_keys("test_user")
            
            email_input = self.driver.find_element(By.ID, "email")
            email_input.send_keys("test@example.com")
            
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys("Test@123")
            
            confirm_input = self.driver.find_element(By.ID, "confirm_password")
            confirm_input.send_keys("Test@123")
            
            # Step 3: Submit registration
            self.logger.info("Submitting registration")
            submit_button = self.driver.find_element(By.ID, "register-button")
            submit_button.click()
            
            # Step 4: Verify registration success
            success_message = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )
            assert "Registration successful" in success_message.text
            
            # Step 5: Navigate to login page
            self.logger.info("Navigating to login page")
            self.driver.get("http://localhost:3000/login")
            
            # Step 6: Fill login form
            self.logger.info("Filling login form")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_input.send_keys("test_user")
            
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys("Test@123")
            
            # Step 7: Submit login
            self.logger.info("Submitting login")
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            # Step 8: Verify login success
            self.logger.info("Verifying login success")
            dashboard = self.wait.until(
                EC.presence_of_element_located((By.ID, "dashboard"))
            )
            assert dashboard.is_displayed()
            
        except Exception as e:
            self.logger.error(f"Test failed: {str(e)}")
            self.driver.save_screenshot("error_screenshot.png")
            raise

    def test_product_workflow(self):
        """Test product browsing and purchase flow."""
        try:
            # Step 1: Login
            self.logger.info("Logging in")
            self._login("test_user", "Test@123")
            
            # Step 2: Navigate to products page
            self.logger.info("Navigating to products page")
            self.driver.get("http://localhost:3000/products")
            
            # Step 3: Search for product
            self.logger.info("Searching for product")
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            search_input.send_keys("test product")
            
            search_button = self.driver.find_element(By.ID, "search-button")
            search_button.click()
            
            # Step 4: Select product
            self.logger.info("Selecting product")
            product = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
            )
            product.click()
            
            # Step 5: Add to cart
            self.logger.info("Adding to cart")
            add_to_cart = self.wait.until(
                EC.element_to_be_clickable((By.ID, "add-to-cart"))
            )
            add_to_cart.click()
            
            # Step 6: Verify cart update
            cart_count = self.wait.until(
                EC.presence_of_element_located((By.ID, "cart-count"))
            )
            assert cart_count.text == "1"
            
            # Step 7: Proceed to checkout
            self.logger.info("Proceeding to checkout")
            cart_icon = self.driver.find_element(By.ID, "cart-icon")
            cart_icon.click()
            
            checkout_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "checkout-button"))
            )
            checkout_button.click()
            
            # Step 8: Fill shipping information
            self.logger.info("Filling shipping information")
            self._fill_shipping_form()
            
            # Step 9: Complete purchase
            self.logger.info("Completing purchase")
            complete_button = self.driver.find_element(By.ID, "complete-purchase")
            complete_button.click()
            
            # Step 10: Verify purchase success
            success_message = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )
            assert "Purchase successful" in success_message.text
            
        except Exception as e:
            self.logger.error(f"Test failed: {str(e)}")
            self.driver.save_screenshot("error_screenshot.png")
            raise

    def _login(self, username: str, password: str):
        """Helper method to log in."""
        self.driver.get("http://localhost:3000/login")
        
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_input.send_keys(username)
        
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        
        login_button = self.driver.find_element(By.ID, "login-button")
        login_button.click()
        
        # Wait for dashboard
        self.wait.until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )

    def _fill_shipping_form(self):
        """Helper method to fill shipping form."""
        # Fill address
        address = self.wait.until(
            EC.presence_of_element_located((By.ID, "address"))
        )
        address.send_keys("123 Test St")
        
        city = self.driver.find_element(By.ID, "city")
        city.send_keys("Test City")
        
        state = self.driver.find_element(By.ID, "state")
        state.send_keys("Test State")
        
        zipcode = self.driver.find_element(By.ID, "zipcode")
        zipcode.send_keys("12345")
        
        # Fill payment
        card_number = self.driver.find_element(By.ID, "card-number")
        card_number.send_keys("4111111111111111")
        
        expiry = self.driver.find_element(By.ID, "expiry")
        expiry.send_keys("12/25")
        
        cvv = self.driver.find_element(By.ID, "cvv")
        cvv.send_keys("123")

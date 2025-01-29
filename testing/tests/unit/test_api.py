#!/usr/bin/env python3

import pytest
import json
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st
from api.endpoints import UserAPI, ProductAPI
from models.user import User
from models.product import Product

@pytest.mark.asyncio
class TestUserAPI:
    @pytest.fixture
    async def api(self):
        """Create test UserAPI instance."""
        return UserAPI()

    @pytest.fixture
    async def mock_db(self):
        """Create mock database."""
        return Mock()

    @given(st.text(min_size=1), st.emails())
    async def test_create_user(self, api, mock_db, username, email):
        """Test user creation with property-based testing."""
        # Arrange
        user_data = {
            'username': username,
            'email': email
        }
        mock_db.create_user.return_value = User(id=1, **user_data)
        api.db = mock_db

        # Act
        result = await api.create_user(user_data)

        # Assert
        assert result.username == username
        assert result.email == email
        mock_db.create_user.assert_called_once_with(user_data)

    async def test_get_user(self, api, mock_db):
        """Test getting user by ID."""
        # Arrange
        user_id = 1
        mock_user = User(id=user_id, username='test_user', email='test@example.com')
        mock_db.get_user.return_value = mock_user
        api.db = mock_db

        # Act
        result = await api.get_user(user_id)

        # Assert
        assert result == mock_user
        mock_db.get_user.assert_called_once_with(user_id)

    async def test_update_user(self, api, mock_db):
        """Test updating user."""
        # Arrange
        user_id = 1
        update_data = {'username': 'new_username'}
        mock_user = User(id=user_id, username='new_username', email='test@example.com')
        mock_db.update_user.return_value = mock_user
        api.db = mock_db

        # Act
        result = await api.update_user(user_id, update_data)

        # Assert
        assert result.username == 'new_username'
        mock_db.update_user.assert_called_once_with(user_id, update_data)

    async def test_delete_user(self, api, mock_db):
        """Test deleting user."""
        # Arrange
        user_id = 1
        mock_db.delete_user.return_value = True
        api.db = mock_db

        # Act
        result = await api.delete_user(user_id)

        # Assert
        assert result is True
        mock_db.delete_user.assert_called_once_with(user_id)

@pytest.mark.asyncio
class TestProductAPI:
    @pytest.fixture
    async def api(self):
        """Create test ProductAPI instance."""
        return ProductAPI()

    @pytest.fixture
    async def mock_db(self):
        """Create mock database."""
        return Mock()

    @given(
        st.text(min_size=1),
        st.decimals(min_value=0, max_value=1000000),
        st.integers(min_value=0)
    )
    async def test_create_product(self, api, mock_db, name, price, stock):
        """Test product creation with property-based testing."""
        # Arrange
        product_data = {
            'name': name,
            'price': float(price),
            'stock': stock
        }
        mock_db.create_product.return_value = Product(id=1, **product_data)
        api.db = mock_db

        # Act
        result = await api.create_product(product_data)

        # Assert
        assert result.name == name
        assert result.price == float(price)
        assert result.stock == stock
        mock_db.create_product.assert_called_once_with(product_data)

    async def test_get_product(self, api, mock_db):
        """Test getting product by ID."""
        # Arrange
        product_id = 1
        mock_product = Product(id=product_id, name='Test Product', price=99.99, stock=100)
        mock_db.get_product.return_value = mock_product
        api.db = mock_db

        # Act
        result = await api.get_product(product_id)

        # Assert
        assert result == mock_product
        mock_db.get_product.assert_called_once_with(product_id)

    @pytest.mark.parametrize('stock_change,expected', [
        (10, 110),
        (-10, 90),
        (0, 100)
    ])
    async def test_update_stock(self, api, mock_db, stock_change, expected):
        """Test updating product stock."""
        # Arrange
        product_id = 1
        mock_product = Product(id=product_id, name='Test Product', price=99.99, stock=100)
        mock_db.get_product.return_value = mock_product
        mock_db.update_product.return_value = Product(
            id=product_id,
            name='Test Product',
            price=99.99,
            stock=expected
        )
        api.db = mock_db

        # Act
        result = await api.update_stock(product_id, stock_change)

        # Assert
        assert result.stock == expected
        mock_db.update_product.assert_called_once()

    async def test_delete_product(self, api, mock_db):
        """Test deleting product."""
        # Arrange
        product_id = 1
        mock_db.delete_product.return_value = True
        api.db = mock_db

        # Act
        result = await api.delete_product(product_id)

        # Assert
        assert result is True
        mock_db.delete_product.assert_called_once_with(product_id)

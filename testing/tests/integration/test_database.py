#!/usr/bin/env python3

import pytest
import asyncio
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.product import Product
from database.operations import DatabaseOperations

@pytest.mark.asyncio
class TestDatabaseOperations:
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Set up test database."""
        # Create test database
        self.engine = create_engine('postgresql://test_user:test_pass@localhost/test_db')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Create tables
        User.metadata.create_all(self.engine)
        Product.metadata.create_all(self.engine)
        
        # Create database operations instance
        self.db = DatabaseOperations(self.session)
        
        yield
        
        # Cleanup
        User.metadata.drop_all(self.engine)
        Product.metadata.drop_all(self.engine)
        self.session.close()

    async def test_user_crud(self):
        """Test user CRUD operations."""
        # Create
        user_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'created_at': datetime.now()
        }
        user = await self.db.create_user(user_data)
        assert user.username == 'test_user'
        
        # Read
        retrieved_user = await self.db.get_user(user.id)
        assert retrieved_user.email == 'test@example.com'
        
        # Update
        update_data = {'username': 'updated_user'}
        updated_user = await self.db.update_user(user.id, update_data)
        assert updated_user.username == 'updated_user'
        
        # Delete
        deleted = await self.db.delete_user(user.id)
        assert deleted is True
        
        # Verify deletion
        deleted_user = await self.db.get_user(user.id)
        assert deleted_user is None

    async def test_product_crud(self):
        """Test product CRUD operations."""
        # Create
        product_data = {
            'name': 'Test Product',
            'price': 99.99,
            'stock': 100,
            'created_at': datetime.now()
        }
        product = await self.db.create_product(product_data)
        assert product.name == 'Test Product'
        
        # Read
        retrieved_product = await self.db.get_product(product.id)
        assert retrieved_product.price == 99.99
        
        # Update
        update_data = {'price': 149.99}
        updated_product = await self.db.update_product(product.id, update_data)
        assert updated_product.price == 149.99
        
        # Delete
        deleted = await self.db.delete_product(product.id)
        assert deleted is True
        
        # Verify deletion
        deleted_product = await self.db.get_product(product.id)
        assert deleted_product is None

    async def test_batch_operations(self):
        """Test batch database operations."""
        # Batch create
        users = [
            {'username': f'user_{i}', 'email': f'user_{i}@example.com'}
            for i in range(5)
        ]
        created_users = await self.db.batch_create_users(users)
        assert len(created_users) == 5
        
        # Batch update
        update_data = {'active': True}
        user_ids = [user.id for user in created_users]
        updated_users = await self.db.batch_update_users(user_ids, update_data)
        assert all(user.active for user in updated_users)
        
        # Batch delete
        deleted = await self.db.batch_delete_users(user_ids)
        assert deleted == len(user_ids)

    async def test_transactions(self):
        """Test database transactions."""
        # Start transaction
        async with self.db.transaction() as txn:
            # Create user
            user = await self.db.create_user({
                'username': 'txn_user',
                'email': 'txn@example.com'
            })
            
            # Create product
            product = await self.db.create_product({
                'name': 'Txn Product',
                'price': 99.99,
                'stock': 100
            })
            
            # Create order
            order = await self.db.create_order({
                'user_id': user.id,
                'product_id': product.id,
                'quantity': 1
            })
            
            # Verify all objects created
            assert user.id is not None
            assert product.id is not None
            assert order.id is not None
        
        # Verify transaction committed
        user = await self.db.get_user(user.id)
        assert user is not None

    async def test_concurrent_operations(self):
        """Test concurrent database operations."""
        # Create test data
        product = await self.db.create_product({
            'name': 'Concurrent Product',
            'price': 99.99,
            'stock': 100
        })
        
        # Simulate concurrent stock updates
        async def update_stock(change):
            return await self.db.update_product_stock(product.id, change)
        
        # Run concurrent updates
        tasks = [
            update_stock(1) for _ in range(10)
        ] + [
            update_stock(-1) for _ in range(5)
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify final stock
        updated_product = await self.db.get_product(product.id)
        assert updated_product.stock == 105  # 100 + 10 - 5

    async def test_query_performance(self):
        """Test database query performance."""
        # Create test data
        for i in range(1000):
            await self.db.create_user({
                'username': f'perf_user_{i}',
                'email': f'perf_{i}@example.com'
            })
        
        # Test query with timing
        start_time = datetime.now()
        users = await self.db.get_users_paginated(page=1, per_page=100)
        end_time = datetime.now()
        
        # Verify performance
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Query should complete within 1 second
        assert len(users) == 100

    async def test_error_handling(self):
        """Test database error handling."""
        # Test duplicate user
        user_data = {
            'username': 'unique_user',
            'email': 'unique@example.com'
        }
        await self.db.create_user(user_data)
        
        with pytest.raises(Exception):
            await self.db.create_user(user_data)
        
        # Test invalid foreign key
        with pytest.raises(Exception):
            await self.db.create_order({
                'user_id': 999999,  # Non-existent user
                'product_id': 999999,  # Non-existent product
                'quantity': 1
            })
        
        # Test invalid data type
        with pytest.raises(Exception):
            await self.db.create_product({
                'name': 'Invalid Product',
                'price': 'not_a_number',  # Invalid price
                'stock': 100
            })

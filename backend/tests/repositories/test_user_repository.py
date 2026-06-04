import pytest
from app.repositories import UserRepository
from app.models.user import User

class TestUserRepository:
    """Test cases for UserRepository."""
    
    def test_get_by_email(self, session, sample_user):
        """Test finding user by email."""
        repo = UserRepository(session)
        
        user = repo.get_by_email(sample_user.email)
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
        
        # Test non-existent email
        user = repo.get_by_email("nonexistent@example.com")
        assert user is None
    
    def test_email_exists(self, session, sample_user):
        """Test checking if email exists."""
        repo = UserRepository(session)
        
        assert repo.email_exists(sample_user.email) is True
        assert repo.email_exists("nonexistent@example.com") is False
    
    def test_create_user(self, session):
        """Test creating a new user."""
        repo = UserRepository(session)
        
        user = repo.create_user(
            email="newuser@example.com",
            password_hash="hashed_password",
            name="New User"
        )
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.password_hash == "hashed_password"
        assert user.name == "New User"
        
        # Verify it's in the database
        found = repo.get_by_email("newuser@example.com")
        assert found.id == user.id
    
    def test_update_user_profile(self, session, sample_user):
        """Test updating user profile."""
        repo = UserRepository(session)
        
        updated = repo.update_user_profile(sample_user, name="Updated Name")
        assert updated.name == "Updated Name"
        assert updated.id == sample_user.id
        
        # Verify the change persisted
        found = repo.get_by_id(sample_user.id)
        assert found.name == "Updated Name"
    
    def test_get_users_paginated(self, session):
        """Test getting paginated users."""
        repo = UserRepository(session)
        
        # Create multiple users
        for i in range(15):
            repo.create_user(f"user{i}@example.com", f"hash{i}", f"User {i}")
        
        # Test first page
        users, total = repo.get_users_paginated(page=1, per_page=10)
        assert len(users) == 10
        assert total == 16  # 15 + 1 from sample_user fixture
        
        # Test second page
        users, total = repo.get_users_paginated(page=2, per_page=10)
        assert len(users) == 6
        assert total == 16
    
    def test_inherited_methods(self, session, sample_user):
        """Test methods inherited from BaseRepository."""
        repo = UserRepository(session)
        
        # Test get_by_id
        user = repo.get_by_id(sample_user.id)
        assert user.email == sample_user.email
        
        # Test filter_by
        users = repo.filter_by(email=sample_user.email)
        assert len(users) == 1
        assert users[0].id == sample_user.id
        
        # Test count
        count = repo.count()
        assert count == 1
        
        # Test update
        updated = repo.update(sample_user, name="Updated via base")
        assert updated.name == "Updated via base"
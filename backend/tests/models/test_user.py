import pytest
import uuid
from app.models.user import User
from app.extensions import bcrypt

class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, session):
        """Test creating a new user."""
        user = User(
            email="newuser@example.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            name="New User"
        )
        session.add(user)
        session.commit()
        
        assert user.id is not None
        assert isinstance(user.id, str)
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.created_at is not None
    
    def test_user_uuid_generation(self, session):
        """Test that user ID is a valid UUID."""
        user = User(
            email="uuid@example.com",
            password_hash="hash"
        )
        session.add(user)
        session.commit()
        
        # Should be a valid UUID string
        uuid.UUID(user.id)  # This will raise if invalid
    
    def test_user_to_dict(self, sample_user):
        """Test user serialization."""
        user_dict = sample_user.to_dict()
        
        assert user_dict['id'] == sample_user.id
        assert user_dict['email'] == sample_user.email
        assert user_dict['name'] == sample_user.name
        assert 'password_hash' not in user_dict  # Should not expose password
        assert 'created_at' in user_dict
    
    def test_user_repr(self, sample_user):
        """Test user string representation."""
        repr_str = repr(sample_user)
        assert f"<User id={sample_user.id}" in repr_str
        assert f"email={sample_user.email}" in repr_str
    
    def test_user_relationships(self, session, sample_user, sample_product):
        """Test user relationships with try-on jobs."""
        from app.models.tryon_job import TryOnJob, JobStatus
        
        job = TryOnJob(
            user_id=sample_user.id,
            product_id=sample_product.id,
            person_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg",
            status=JobStatus.PENDING
        )
        session.add(job)
        session.commit()
        
        # Refresh to get relationships
        session.refresh(sample_user)
        
        assert len(sample_user.tryon_jobs) == 1
        assert sample_user.tryon_jobs[0].id == job.id
    
    def test_user_unique_email(self, session):
        """Test that email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            password_hash="hash1"
        )
        session.add(user1)
        session.commit()
        
        user2 = User(
            email="duplicate@example.com",
            password_hash="hash2"
        )
        session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()
    
    def test_user_nullable_name(self, session):
        """Test that name can be null."""
        user = User(
            email="noname@example.com",
            password_hash="hash"
        )
        session.add(user)
        session.commit()
        
        assert user.name is None
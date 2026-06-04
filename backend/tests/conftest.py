import pytest
import os
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.tryon_job import TryOnJob, JobStatus

@pytest.fixture(scope='session')
def test_app():
    """Create and configure a new app instance for each test session."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "CLOUDINARY_URL": "cloudinary://test:test@test",
        "HUGGINGFACE_API_TOKEN": "test-token",
        "PRODUCT_CACHE_TTL_SECONDS": 3600,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """Test client for the Flask application."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def session(test_app):
    """Database session for tests."""
    with test_app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure the session
        session = db.Session(bind=connection)
        db.session = session
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def sample_user(session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        password_hash="$2b$12$test.hash",
        name="Test User"
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def sample_product(session):
    """Create a sample product for testing."""
    product = Product(
        external_id=1,
        title="Test T-Shirt",
        brand="Test Brand",
        category="shirt",
        price=29.99,
        image_url="http://example.com/shirt.jpg",
        cached_at=datetime.utcnow(),
        raw_data={"id": 1, "title": "Test T-Shirt"}
    )
    session.add(product)
    session.commit()
    return product

@pytest.fixture
def sample_tryon_job(session, sample_user, sample_product):
    """Create a sample try-on job for testing."""
    job = TryOnJob(
        user_id=sample_user.id,
        product_id=sample_product.id,
        person_image_url="http://example.com/person.jpg",
        garment_image_url="http://example.com/garment.jpg",
        status=JobStatus.PENDING
    )
    session.add(job)
    session.commit()
    return job

@pytest.fixture
def auth_headers(client, sample_user):
    """Get authorization headers with JWT token."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        token = create_access_token(identity=str(sample_user.id))
        return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def reset_database(session):
    """Reset the database between tests."""
    yield
    # Clean up all data
    session.query(TryOnJob).delete()
    session.query(Product).delete()
    session.query(User).delete()
    session.commit()
import pytest
from datetime import datetime, timedelta, timezone
from app.models.product import Product

class TestProductModel:
    """Test cases for Product model."""
    
    def test_product_creation(self, session):
        """Test creating a new product."""
        product = Product(
            external_id=123,
            title="Test Product",
            brand="Test Brand",
            category="clothing",
            price=49.99,
            image_url="http://example.com/product.jpg",
            cached_at=datetime.now(timezone.utc),
            raw_data={"id": 123, "title": "Test Product"}
        )
        session.add(product)
        session.commit()
        
        assert product.id is not None
        assert product.external_id == 123
        assert product.title == "Test Product"
        assert product.brand == "Test Brand"
        assert product.category == "clothing"
        assert product.price == 49.99
        assert product.image_url == "http://example.com/product.jpg"
        assert product.cached_at is not None
        assert product.raw_data == {"id": 123, "title": "Test Product"}
    
    def test_product_to_dict(self, sample_product):
        """Test product serialization."""
        product_dict = sample_product.to_dict()
        
        assert product_dict['id'] == sample_product.id
        assert product_dict['external_id'] == sample_product.external_id
        assert product_dict['title'] == sample_product.title
        assert product_dict['brand'] == sample_product.brand
        assert product_dict['category'] == sample_product.category
        assert product_dict['price'] == sample_product.price
        assert product_dict['image_url'] == sample_product.image_url
        assert 'cached_at' in product_dict
    
    def test_product_repr(self, sample_product):
        """Test product string representation."""
        repr_str = repr(sample_product)
        assert f"<Product id={sample_product.id}" in repr_str
        assert f"title={sample_product.title}" in repr_str
    
    def test_product_relationships(self, session, sample_product, sample_user):
        """Test product relationships with try-on jobs."""
        from app.models.tryon_job import TryOnJob, JobStatus
        
        job = TryOnJob(
            user_id=sample_user.id,
            product_id=sample_product.id,
            person_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg",
            status=JobStatus.DONE,
            result_url="results/123"
        )
        session.add(job)
        session.commit()
        
        # Refresh to get relationships
        session.refresh(sample_product)
        
        assert len(sample_product.tryon_jobs) == 1
        assert sample_product.tryon_jobs[0].id == job.id
    
    def test_product_cache_timestamp(self, session):
        """Test product cache timestamp behavior."""
        # Create product without cached_at
        product = Product(
            external_id=456,
            title="No Cache Product"
        )
        session.add(product)
        session.commit()
        
        assert product.cached_at is None
        
        # Update cached_at
        product.cached_at = datetime.now(timezone.utc)
        session.commit()
        
        assert product.cached_at is not None
    
    def test_product_unique_external_id(self, session):
        """Test that external_id must be unique."""
        product1 = Product(
            external_id=999,
            title="Product 1"
        )
        session.add(product1)
        session.commit()
        
        product2 = Product(
            external_id=999,
            title="Product 2"
        )
        session.add(product2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()
    
    def test_product_nullable_fields(self, session):
        """Test that most fields can be null."""
        product = Product(
            external_id=789,
            # Only external_id is required
        )
        session.add(product)
        session.commit()
        
        assert product.title is None
        assert product.brand is None
        assert product.category is None
        assert product.price is None
        assert product.image_url is None
        assert product.cached_at is None
        assert product.raw_data is None
import pytest
from datetime import datetime, timedelta, timezone
from app.repositories import ProductRepository
from app.models.product import Product

class TestProductRepository:
    """Test cases for ProductRepository."""
    
    def test_get_by_external_id(self, session, sample_product):
        """Test finding product by external ID."""
        repo = ProductRepository(session)
        
        product = repo.get_by_external_id(sample_product.external_id)
        assert product is not None
        assert product.id == sample_product.id
        assert product.external_id == sample_product.external_id
        
        # Test non-existent external_id
        product = repo.get_by_external_id(99999)
        assert product is None
    
    def test_get_or_create(self, session):
        """Test get or create functionality."""
        repo = ProductRepository(session)
        
        # Create new product
        product = repo.get_or_create(
            external_id=500,
            title="New Product",
            brand="New Brand",
            price=39.99
        )
        assert product.external_id == 500
        assert product.title == "New Product"
        
        # Get existing product
        product2 = repo.get_or_create(
            external_id=500,
            title="Different Title",  # Should be ignored
            price=49.99  # Should be ignored
        )
        assert product2.id == product.id
        assert product2.title == "New Product"  # Original title
        assert product2.price == 39.99  # Original price
    
    def test_update_from_external(self, session, sample_product):
        """Test updating product from external data."""
        repo = ProductRepository(session)
        
        updated = repo.update_from_external(
            sample_product,
            title="Updated Title",
            price=59.99,
            brand="Updated Brand"
        )
        
        assert updated.title == "Updated Title"
        assert updated.price == 59.99
        assert updated.brand == "Updated Brand"
        assert updated.cached_at is not None
        assert updated.cached_at > sample_product.cached_at
    
    def test_is_cache_valid(self, session):
        """Test cache validity checking."""
        repo = ProductRepository(session)
        
        # Product with fresh cache
        fresh_product = Product(
            external_id=100,
            cached_at=datetime.now(timezone.utc)
        )
        session.add(fresh_product)
        session.commit()
        
        assert repo.is_cache_valid(fresh_product, cache_duration_hours=24) is True
        
        # Product with old cache
        old_product = Product(
            external_id=101,
            cached_at=datetime.now(timezone.utc) - timedelta(hours=25)
        )
        session.add(old_product)
        session.commit()
        
        assert repo.is_cache_valid(old_product, cache_duration_hours=24) is False
        
        # Product without cache
        no_cache_product = Product(external_id=102)
        session.add(no_cache_product)
        session.commit()
        
        assert repo.is_cache_valid(no_cache_product) is False
    
    def test_get_featured(self, session):
        """Test getting featured products."""
        repo = ProductRepository(session)
        
        # Create multiple products
        for i in range(15):
            product = Product(
                external_id=1000 + i,
                title=f"Product {i}",
                cached_at=datetime.now(timezone.utc)
            )
            session.add(product)
        session.commit()
        
        featured = repo.get_featured(limit=10)
        assert len(featured) == 10
    
    def test_search(self, session):
        """Test product search functionality."""
        repo = ProductRepository(session)
        
        # Create test products
        products = [
            Product(external_id=200, title="Red T-Shirt", brand="Nike", category="shirt"),
            Product(external_id=201, title="Blue Jeans", brand="Levi's", category="pants"),
            Product(external_id=202, title="Nike Shoes", brand="Nike", category="shoes"),
            Product(external_id=203, title="Red Dress", brand="Zara", category="dress"),
        ]
        for p in products:
            session.add(p)
        session.commit()
        
        # Search by title
        results = repo.search("Red")
        assert len(results) == 2
        assert all("Red" in r.title for r in results)
        
        # Search by brand
        results = repo.search("Nike")
        assert len(results) == 2
        assert all(r.brand == "Nike" or "Nike" in r.title for r in results)
        
        # Search with category filter
        results = repo.search("Red", category="shirt")
        assert len(results) == 1
        assert results[0].title == "Red T-Shirt"
        
        # Search with limit
        results = repo.search("", limit=2)
        assert len(results) == 2
    
    def test_get_by_category(self, session):
        """Test getting products by category."""
        repo = ProductRepository(session)
        
        # Create test products
        for i in range(5):
            session.add(Product(
                external_id=300 + i,
                title=f"Shirt {i}",
                category="shirt"
            ))
        for i in range(3):
            session.add(Product(
                external_id=400 + i,
                title=f"Pants {i}",
                category="pants"
            ))
        session.commit()
        
        shirts = repo.get_by_category("shirt")
        assert len(shirts) == 5
        assert all(s.category == "shirt" for s in shirts)
        
        pants = repo.get_by_category("pants", limit=2)
        assert len(pants) == 2
        assert all(p.category == "pants" for p in pants)
    
    def test_bulk_create_or_update(self, session):
        """Test bulk create or update functionality."""
        repo = ProductRepository(session)
        
        products_data = [
            {"external_id": 500, "title": "Product 1", "price": 10.00},
            {"external_id": 501, "title": "Product 2", "price": 20.00},
            {"id": 502, "title": "Product 3", "price": 30.00},  # Using 'id' instead
        ]
        
        created = repo.bulk_create_or_update(products_data)
        assert len(created) == 3
        assert created[0].external_id == 500
        assert created[1].external_id == 501
        assert created[2].external_id == 502
        
        # Update existing products
        products_data[0]["price"] = 15.00
        updated = repo.bulk_create_or_update(products_data[:1])
        assert len(updated) == 1
        assert updated[0].price == 15.00
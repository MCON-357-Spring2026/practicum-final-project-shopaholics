import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timezone, timedelta

class TestProductRoutes:
    """Test cases for product routes."""
    
    @patch('app.services.catalog.list_wearables')
    def test_featured_products_success(self, mock_list_wearables, client, auth_headers):
        """Test getting featured products."""
        mock_list_wearables.return_value = [
            {"id": 1, "title": "T-Shirt", "category": "shirt", "price": 19.99},
            {"id": 2, "title": "Dress", "category": "dress", "price": 39.99}
        ]
        
        response = client.get('/api/products/featured', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['title'] == "T-Shirt"
        assert data[1]['title'] == "Dress"
    
    def test_featured_products_unauthenticated(self, client):
        """Test featured products without authentication."""
        response = client.get('/api/products/featured')
        assert response.status_code == 401
    
    @patch('app.services.catalog.list_wearables')
    def test_featured_products_api_error(self, mock_list_wearables, client, auth_headers):
        """Test featured products with catalog API error."""
        mock_list_wearables.side_effect = Exception("API Error")
        
        response = client.get('/api/products/featured', headers=auth_headers)
        
        assert response.status_code == 502
        assert 'Failed to fetch products' in response.get_json()['error']
    
    @patch('app.services.catalog.search_products')
    def test_search_products_success(self, mock_search, client, auth_headers):
        """Test searching products."""
        mock_search.return_value = [
            {"id": 3, "title": "Red Shirt", "category": "shirt", "price": 24.99}
        ]
        
        response = client.get('/api/products/search?q=red', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['title'] == "Red Shirt"
        
        mock_search.assert_called_once_with("red", category=None, limit=20)
    
    @patch('app.services.catalog.search_products')
    def test_search_products_with_filters(self, mock_search, client, auth_headers):
        """Test searching products with category and limit."""
        mock_search.return_value = []
        
        response = client.get(
            '/api/products/search?q=blue&category=pants&limit=5', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        mock_search.assert_called_once_with("blue", category="pants", limit=5)
    
    def test_search_products_no_query(self, client, auth_headers):
        """Test search without query parameter."""
        response = client.get('/api/products/search', headers=auth_headers)
        
        assert response.status_code == 400
        assert "Query parameter 'q' is required" in response.get_json()['error']
    
    @patch('app.services.catalog.search_products')
    def test_search_products_api_error(self, mock_search, client, auth_headers):
        """Test search with API error."""
        mock_search.side_effect = Exception("Search API Error")
        
        response = client.get('/api/products/search?q=test', headers=auth_headers)
        
        assert response.status_code == 502
        assert 'Failed to fetch products' in response.get_json()['error']
    
    def test_get_single_product_success(self, client, auth_headers, sample_product):
        """Test getting a single product."""
        response = client.get(
            f'/api/products/{sample_product.id}', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_product.id
        assert data['title'] == sample_product.title
    
    def test_get_single_product_not_found(self, client, auth_headers):
        """Test getting non-existent product."""
        response = client.get('/api/products/nonexistent-id', headers=auth_headers)
        
        assert response.status_code == 404
        assert 'Product not found' in response.get_json()['error']
    
    @patch('app.services.catalog.get_product')
    def test_get_single_product_cache_refresh(self, mock_get_product, client, 
                                            auth_headers, session, sample_product):
        """Test product cache refresh when stale."""
        # Make product cache old
        sample_product.cached_at = datetime.now(timezone.utc) - timedelta(days=2)
        session.commit()
        
        # Mock fresh data from API
        mock_get_product.return_value = {
            "id": sample_product.external_id,
            "title": "Updated Title",
            "price": 99.99
        }
        
        response = client.get(
            f'/api/products/{sample_product.id}', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # Title should be updated from API
        assert data['title'] == "Updated Title"
        
        mock_get_product.assert_called_once_with(str(sample_product.external_id))
    
    @patch('app.routes.products._is_cache_fresh')
    @patch('app.services.catalog.get_product')
    def test_get_single_product_cache_refresh_fail(self, mock_get_product, 
                                                  mock_is_fresh, client, 
                                                  auth_headers, sample_product):
        """Test product returned even if cache refresh fails."""
        mock_is_fresh.return_value = False
        mock_get_product.side_effect = Exception("API Error")
        
        response = client.get(
            f'/api/products/{sample_product.id}', 
            headers=auth_headers
        )
        
        # Should still return the stale product
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_product.id
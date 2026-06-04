import pytest
from unittest.mock import patch, Mock
from app.services import catalog

class TestCatalogService:
    """Test cases for catalog service."""
    
    @patch('app.services.catalog.requests.get')
    def test_search_products_success(self, mock_get):
        """Test successful product search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "products": [
                {"id": 1, "title": "T-Shirt", "category": "shirt", "price": 19.99},
                {"id": 2, "title": "Jeans", "category": "pants", "price": 49.99}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        results = catalog.search_products("clothing", limit=2)
        
        assert len(results) == 2
        assert results[0]["title"] == "T-Shirt"
        assert results[1]["title"] == "Jeans"
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "products/search" in call_args[0][0]
        assert call_args[1]["params"]["q"] == "clothing"
        assert call_args[1]["params"]["limit"] == 2
    
    @patch('app.services.catalog.requests.get')
    def test_search_products_with_category(self, mock_get):
        """Test product search with category filter."""
        mock_response = Mock()
        mock_response.json.return_value = {"products": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog.search_products("red", category="shirt", limit=10)
        
        call_args = mock_get.call_args
        assert call_args[1]["params"]["category"] == "shirt"
    
    @patch('app.services.catalog.requests.get')
    def test_search_products_error(self, mock_get):
        """Test product search with API error."""
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            catalog.search_products("test")
        
        assert "API Error" in str(exc_info.value)
    
    @patch('app.services.catalog.requests.get')
    def test_get_product_success(self, mock_get):
        """Test getting single product."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1,
            "title": "Test Product",
            "price": 29.99
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        product = catalog.get_product("1")
        
        assert product["id"] == 1
        assert product["title"] == "Test Product"
        
        mock_get.assert_called_once()
        assert "products/1" in mock_get.call_args[0][0]
    
    @patch('app.services.catalog._SEED_DATA', [
        {"id": 1, "title": "Shirt", "category": "shirt"},
        {"id": 2, "title": "Dress", "category": "dress"},
        {"id": 3, "title": "Pants", "category": "pants"},
        {"id": 4, "title": "Skirt", "category": "skirt"}
    ])
    def test_list_wearables(self):
        """Test listing wearable items from seed data."""
        wearables = catalog.list_wearables()
        
        # Should return items from wearable categories
        assert len(wearables) > 0
        assert all(item["category"] in catalog._WEARABLE_CATEGORIES for item in wearables)
        
        # Check specific items
        titles = [item["title"] for item in wearables]
        assert "Shirt" in titles
        assert "Dress" in titles
    
    def test_wearable_categories_constant(self):
        """Test that wearable categories are defined correctly."""
        expected_categories = {"shirt", "dress", "pants", "skirt", "overall"}
        assert catalog._WEARABLE_CATEGORIES == expected_categories
    
    @patch('app.services.catalog._load_seed_data')
    def test_seed_data_loading(self, mock_load):
        """Test that seed data is loaded on module import."""
        # The seed data should be loaded when the module is imported
        # This is just to ensure the loading mechanism exists
        mock_load.assert_called()
    
    @patch('app.services.catalog.requests.get')
    def test_api_headers(self, mock_get):
        """Test that API calls include proper headers."""
        mock_response = Mock()
        mock_response.json.return_value = {"products": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        catalog.search_products("test")
        
        call_args = mock_get.call_args
        headers = call_args[1].get("headers", {})
        
        # Should include RapidAPI headers if configured
        if catalog._RAPIDAPI_KEY:
            assert "X-RapidAPI-Key" in headers
            assert "X-RapidAPI-Host" in headers
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    model = Product

    def __init__(self, session: Session = None):
        super().__init__(session)

    def get_by_external_id(self, external_id: int) -> Optional[Product]:
        return self.session.query(Product).filter(Product.external_id == external_id).first()

    def get_or_create(self, external_id: int, **kwargs) -> Product:
        product = self.get_by_external_id(external_id)
        if not product:
            product = Product(external_id=external_id, **kwargs)
            self.save(product)
        return product

    def update_from_external(self, product: Product, **kwargs) -> Product:
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        product.cached_at = datetime.now(timezone.utc)
        return self.save(product)

    def is_cache_valid(self, product: Product, cache_duration_hours: int = 24) -> bool:
        if not product.cached_at:
            return False
        cache_age = datetime.now(timezone.utc) - product.cached_at
        return cache_age < timedelta(hours=cache_duration_hours)

    def get_featured(self, limit: int = 10) -> List[Product]:
        return self.session.query(Product).limit(limit).all()

    def search(self, query: str, category: str = None, limit: int = 20) -> List[Product]:
        filters = []
        
        if query:
            search_pattern = f"%{query}%"
            filters.append(
                or_(
                    Product.title.ilike(search_pattern),
                    Product.brand.ilike(search_pattern),
                    Product.category.ilike(search_pattern)
                )
            )
        
        if category:
            filters.append(Product.category == category)
        
        query_obj = self.session.query(Product)
        for filter_condition in filters:
            query_obj = query_obj.filter(filter_condition)
        
        return query_obj.limit(limit).all()

    def get_by_category(self, category: str, limit: int = None) -> List[Product]:
        query = self.session.query(Product).filter(Product.category == category)
        if limit:
            query = query.limit(limit)
        return query.all()

    def bulk_create_or_update(self, products_data: List[dict]) -> List[Product]:
        products = []
        for data in products_data:
            external_id = data.pop('external_id', data.pop('id', None))
            if external_id:
                product = self.get_or_create(external_id, **data)
                if product.cached_at:
                    product = self.update_from_external(product, **data)
                products.append(product)
        return products
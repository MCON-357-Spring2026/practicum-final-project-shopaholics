from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    model: type[T] = None

    def __init__(self, session: Session = None):
        self.session = session or db.session

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def get_by_id(self, id: Any) -> Optional[T]:
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int = None, offset: int = None) -> List[T]:
        query = self.session.query(self.model)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.session.commit()
        return instance

    def delete(self, instance: T) -> bool:
        try:
            self.session.delete(instance)
            self.session.commit()
            return True
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def save(self, instance: T) -> T:
        self.session.add(instance)
        self.session.commit()
        return instance

    def filter_by(self, **kwargs) -> List[T]:
        return self.session.query(self.model).filter_by(**kwargs).all()

    def first_or_none(self, **kwargs) -> Optional[T]:
        return self.session.query(self.model).filter_by(**kwargs).first()

    def count(self, **kwargs) -> int:
        return self.session.query(self.model).filter_by(**kwargs).count()

    def exists(self, **kwargs) -> bool:
        return self.session.query(self.model.query.exists().where(
            *[getattr(self.model, k) == v for k, v in kwargs.items()]
        )).scalar()
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, session: Session = None):
        super().__init__(session)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def email_exists(self, email: str) -> bool:
        return self.session.query(User).filter(User.email == email).count() > 0

    def create_user(self, email: str, password_hash: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash
        )
        return self.save(user)

    def update_user_profile(self, user: User, **kwargs) -> User:
        # Update any valid attributes on the user
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'password_hash']:
                setattr(user, key, value)
        return self.save(user)

    def get_users_paginated(self, page: int = 1, per_page: int = 10) -> tuple[List[User], int]:
        total = self.count()
        offset = (page - 1) * per_page
        users = self.get_all(limit=per_page, offset=offset)
        return users, total
import uuid
from datetime import datetime, timezone

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ─────────────────────────────
    tryon_jobs = db.relationship(
        "TryOnJob",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # ── Helpers ───────────────────────────────────
    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

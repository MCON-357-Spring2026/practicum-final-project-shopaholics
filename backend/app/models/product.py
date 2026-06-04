import uuid
from datetime import datetime, timezone

from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    external_id = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    title = db.Column(db.String(500))
    brand = db.Column(db.String(255))
    image_url = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    price = db.Column(db.Numeric(10, 2))
    raw_data = db.Column(db.JSON)

    cached_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ── Relationships ─────────────────────────────
    tryon_jobs = db.relationship(
        "TryOnJob",
        back_populates="product",
        lazy="select",
    )

    # ── Helpers ───────────────────────────────────
    def __repr__(self):
        return f"<Product id={self.id} brand={self.brand} title={self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "brand": self.brand,
            "image_url": self.image_url,
            "category": self.category,
            "price": float(self.price) if self.price is not None else None,
            "cached_at": self.cached_at.isoformat(),
        }

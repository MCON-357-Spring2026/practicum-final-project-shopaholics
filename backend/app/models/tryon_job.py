import uuid
import enum
from datetime import datetime, timezone

from app.extensions import db


class JobStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class TryOnJob(db.Model):
    __tablename__ = "tryon_jobs"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id = db.Column(
        db.String(36),
        db.ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    person_image_url = db.Column(db.Text, nullable=False)
    garment_image_url = db.Column(db.Text, nullable=False)
    fashn_prediction_id = db.Column(db.String(255))

    status = db.Column(
        db.Enum(JobStatus),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
    )

    result_url = db.Column(db.Text)
    error_message = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    completed_at = db.Column(db.DateTime(timezone=True))

    # ── Relationships ─────────────────────────────
    user = db.relationship("User", back_populates="tryon_jobs")
    product = db.relationship("Product", back_populates="tryon_jobs")

    # ── Helpers ───────────────────────────────────
    def __repr__(self):
        return f"<TryOnJob id={self.id} status={self.status.value}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "person_image_url": self.person_image_url,
            "garment_image_url": self.garment_image_url,
            "status": self.status.value,
            "result_url": self.result_url,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

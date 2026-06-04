# Import all models so Flask-Migrate can detect them for autogenerate.
from app.models.user import User
from app.models.product import Product
from app.models.tryon_job import TryOnJob, JobStatus

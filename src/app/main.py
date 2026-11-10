"""
Entrypoint alias for uvicorn app.main:app.
Delegates directly to churn_prediction.main:app.
"""
from churn_prediction.main import app

__all__ = ["app"]


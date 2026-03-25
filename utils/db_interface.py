"""
Database Interface
==================
Abstract interface for all database backends.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DatabaseInterface(ABC):
    """Abstract interface for reconciliation database backends."""

    @abstractmethod
    def save_result(self, name: str, workflow_type: str, results: Dict, metadata: Optional[Dict] = None) -> Optional[int]:
        """Save reconciliation results. Returns result ID."""
        ...

    @abstractmethod
    def list_results(self, workflow_type: Optional[str] = None, limit: int = 50) -> List:
        """List saved reconciliation results."""
        ...

    @abstractmethod
    def get_result(self, result_id: int) -> Optional[Dict]:
        """Retrieve a specific reconciliation result."""
        ...

    @abstractmethod
    def delete_result(self, result_id: int) -> bool:
        """Delete a reconciliation result."""
        ...

    @abstractmethod
    def close(self):
        """Close database connection."""
        ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

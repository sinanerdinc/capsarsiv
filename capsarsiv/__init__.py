"""Capsarsiv — Türkçe Caps Arşivi Python SDK ve CLI aracı."""

from capsarsiv.client import CapsArsiv
from capsarsiv.exceptions import (
    APIError,
    AuthenticationError,
    CapsArsivError,
    NotFoundError,
    RateLimitError,
)
from capsarsiv.models import Caps, Tag

__version__ = "0.1.0"

__all__ = [
    "CapsArsiv",
    "Caps",
    "Tag",
    "CapsArsivError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
    "__version__",
]
